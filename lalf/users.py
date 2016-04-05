# -*- coding: utf-8 -*-
#
# This file is part of Lalf.
#
# Lalf is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lalf is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lalf.  If not, see <http://www.gnu.org/licenses/>.

"""
Module handling the exportation of users

In order to prevent the exportation of email addresses, Forumactif
sometimes displays them as images instead of text. This module uses
optical character recognition to export them anyway.
"""

import os
import re
import subprocess
import hashlib
from binascii import crc32

from PIL import Image
from lxml import html

from lalf.node import Node, PaginatedNode, ParsingError
from lalf.util import Counter, pages, random_string, parse_date, parse_userlist_date, clean_filename, clean_url
from lalf.phpbb import BOTS
from lalf import htmltobbcode

PM_SUBJECT = "Félicitations !"
PM_POST = """Félicitations !

Vous avez importé vos données avec succès. N'oubliez pas de
terminer l'importation en suivant la <a class="postlink"
href=https://roromis.github.io/Lalf-Forumactif/importation.html">documentation</a>.

J’ai consacré de nombreuses heures de mon temps libre à la création du
Lalf. Bien que je n’en ai plus l’utilité, j’essaye de le maintenir
malgré les multiples tentatives de la part de l’équipe de Forumactif
de le rendre inutilisable.

N’hésitez pas à me montrer votre reconnaissance une fois l'importation
terminée en effectuant un <a class="postlink"
href="https://roromis.github.io/Lalf-Forumactif/#dons">don</a>."""

class GocrNotInstalled(Exception):
    """
    Exception raised when the gocr executable cannot be found
    """
    def __init__(self, ocrpath):
        Exception.__init__(self)
        self.ocrpath = ocrpath

    def __str__(self):
        return (
            "L'exécutable de gocr ({exe}) n'existe pas. Vérifiez que gocr est bien installé et "
            "que le chemin est correctement configuré dans le fichier config.cfg."
        ).format(exe=self.ocrpath)

def toolong(path):
    """
    Returns true if the email displayed in the image file is too long to
    be displayed entirely
    """
    with Image.open(path) as image:
        width, height = image.size

        for i in range(width-6, width):
            for j in range(0, height):
                if image.getpixel((i, j)) != (255, 255, 255):
                    return True

    return False

def email_hash(email):
    """
    Email hash function used by phpbb
    """
    return str(crc32(email.encode("utf-8"))&0xffffffff) + str(len(email))

def md5(string):
    """
    Compute the md5 hash of a string
    """
    return hashlib.md5(string.encode("utf8")).hexdigest()

class NoUser(object):
    """
    Node used to represent an unexisting user in the database (for
    example if no one has posted in a forum)
    """
    def __init__(self):
        self.newid = 0
        self.name = ""
        self.colour = ""

class AnonymousUser(Node):
    """
    Node representing the anonymous user
    """

    STATE_KEEP = ["newid", "name", "colour"]

    def __init__(self):
        Node.__init__(self, -1)
        self.newid = 1
        self.name = ""
        self.colour = ""

    def _dump_(self, sqlfile):
        post_times = [post.time for post in self.root.get_posts() if post.poster.newid == 1]
        num_posts = sum(1 for _ in post_times)
        if num_posts > 0:
            lastpost_time = max(post_times)
        else:
            lastpost_time = 0

        sqlfile.insert("users", {
            "user_id" : "1",
            "user_type" : "2",
            "group_id" : "1",
            "username" : "Anonymous",
            "username_clean" : "anonymous",
            "user_regdate" : self.root.startdate,
            "user_lang" : self.config["default_lang"],
            "user_style" : "1",
            "user_allow_massemail" : "0",
            "user_lastpost_time" : lastpost_time,
            "user_posts" : num_posts
        })
        sqlfile.insert("user_group", {
            "group_id" : "1",
            "user_id" : "1",
            "user_pending" : "0"
        })

class User(Node):
    """
    Node representing a user

    Attrs:
        id (int): The id of the user in the old forum
        name (str): His username
        mail (str): The email address of the user
        posts (int): The number of posts
        date (int): subscription date (timestamp)
        lastvisit (int): date of last visit (timestamp)
        newid (int): The id of the user in the new forum
        trust (int): level of trust in the email address
            - 3 if the email has been verified to be correct
            - 2 if the email could not be verified
            - 1 if the email is probably incorrect
            - 0 if the email could not be exported
        img (str): The path of the image containing the email
    """
    # Attributes to save
    STATE_KEEP = ["newid", "name", "mail", "posts", "date",
                  "lastvisit", "colour", "groups", "trust", "img"]

    def __init__(self, user_id, name, posts, date, lastvisit, colour):
        Node.__init__(self, user_id)
        self.name = name
        self.posts = posts
        self.date = date
        self.lastvisit = lastvisit
        self.colour = colour

        self.newid = None
        self.groups = []

        self.mail = None
        self.trust = 0
        self.img = os.path.join("usermails", "{}.png".format(clean_filename(self.name)))

    def validate_email(self):
        """
        Check if the email address is correct (using email research)
        """
        # Search for the users who have this email address
        params = {
            "part" : "users_groups",
            "sub" : "users",
            "username" : self.mail,
            "submituser" : "Ok",
            "sort" : "user_id",
            "order" : "ASC"
        }
        response = self.session.get_admin("/admin/index.forum", params=params)

        # Check if this user is one of them
        document = html.fromstring(response.content)
        for row in document.cssselect('table[summary="Liste des Utilisateurs"] tbody tr'):
            cols = row.cssselect("td")
            if cols and cols[0].text_content() == self.name:
                return True

        return False

    def confirm_email(self, retries=2):
        """
        Let the user confirm the email address if it could not be
        validated
        """
        if self.trust == 2:
            self.logger.info(
                "L'adresse email de l'utilisateur %s est probablement valide "
                "mais n'a pas pu être validée.)", self.name)
            self.ui.print((
                "Veuillez saisir l'adresse email de l'utilisateur {} (laissez "
                "vide si l'adresse {} est correcte) :").format(self.name, self.mail))
            self.mail = input("> ").strip()
        elif self.trust == 1:
            self.logger.info(
                "L'adresse email de l'utilisateur %s est probablement invalide.)", self.name)
            self.ui.print((
                "Veuillez saisir l'adresse email de l'utilisateur {} (laissez "
                "vide si l'adresse {} est correcte) :").format(self.name, self.mail))
            self.mail = input("> ").strip()
        elif self.trust == 0:
            self.logger.info(
                "L'adresse email de l'utilisateur %s n'a pas pu être exportée.", self.name)
            if retries == 0:
                self.ui.print("Veuillez saisir l'adresse email de l'utilisateur {} :".format(self.name))
                self.mail = input("> ").strip()
            else:
                self._export_()
                self.confirm_email(retries-1)

    def _export_(self):
        self.logger.info('Récupération du membre %d', self.id)

        if self.newid is None:
            if self.name == self.config["admin_name"]:
                self.newid = 2
            elif self.name == "Anonymous":
                self.newid = 1
            else:
                self.newid = self.users_count.value
                self.users_count += 1

            self.root.current_users += 1
            self.ui.update()

        # Search for this user in the administration panel
        try:
            encodedname = self.name.encode(self.encoding)
        except UnicodeEncodeError:
            encodedname = self.name

        params = {
            "part" : "users_groups",
            "sub" : "users",
            "username" : encodedname,
            "submituser" : "Ok",
            "sort" : "user_id",
            "order" : "ASC"
        }
        response = self.session.get_admin("/admin/index.forum", params=params)

        document = html.fromstring(response.content)
        for row in document.cssselect('table[summary="Liste des Utilisateurs"] tbody tr'):
            cols = row.cssselect("td")
            if cols and cols[0].text_content() == self.name:
                # The user was found
                try:
                    self.mail = cols[1].text_content()
                except IndexError:
                    raise ParsingError(document)

                if self.mail:
                    # The administration panel hasn't been blocked
                    # yet, the email is available
                    self.trust = 3
                    break

                try:
                    img = cols[1].cssselect("img")[0]
                except IndexError:
                    img = None

                if img:
                    # The administration panel has been blocked, the
                    # email is replaced by an image, download it
                    self.logger.warning("Récupération de l'adresse email avec GOCR")

                    response = self.session.get(img.get("src"))
                    with open(self.img, "wb") as fileobj:
                        fileobj.write(response.content)

                    # Use the OCR on it
                    try:
                        self.mail = subprocess.check_output([self.config["gocr"], "-i", self.img],
                                                            universal_newlines=True).strip()
                    except FileNotFoundError:
                        raise GocrNotInstalled(self.config["gocr"])

                    if toolong(self.img):
                        # The image seems to be too small for the
                        # email, the user will have to confirm it
                        self.trust = 1
                    elif self.validate_email():
                        self.trust = 3
                    else:
                        # The email could not be validated, the user
                        # will have to confirm
                        self.trust = 2
                    break


    def _dump_(self, sqlfile):
        try:
            group_id = self.groups[0].newid
        except IndexError:
            group_id = 2

        if 5 in [group.newid for group in self.groups]:
            # The user is an administrator
            self.colour = "AA0000"

        post_times = [post.time for post in self.root.get_posts() if post.poster == self]
        num_posts = sum(1 for _ in post_times)
        if num_posts > 0:
            lastpost_time = max(post_times)
        else:
            lastpost_time = 0

        user = {
            "user_id" : self.newid,
            "group_id" : group_id,
            "user_regdate" : self.date,
            "username" : self.name,
            "username_clean" : self.name.lower(),
            "user_password" : md5(random_string()),
            "user_pass_convert" : "1",
            "user_email" : self.mail,
            "user_email_hash" : email_hash(self.mail),
            "user_lastvisit" : self.lastvisit,
            "user_lastpost_time" : lastpost_time,
            "user_posts" : num_posts,
            "user_lang" : self.config["default_lang"],
            "user_style" : "1",
            #"user_rank" (TODO)
            "user_colour" : self.colour,
            #"user_avatar" (TODO)
            #"user_sig" (TODO)
            #"user_from" (TODO)
            #"user_website" (TODO) (...)
        }

        # Check if the user is the administrator
        if self.name == self.config["admin_name"]:
            user.update({
                "user_type": 3,
                "user_password" : md5(self.config["admin_password"]),
                "user_rank" : 1,
                "user_new_privmsg" : 1,
                "user_unread_privmsg" : 1,
                "user_last_privmsg" : self.root.dump_time
            })

        if self.name == "Anonymous":
            user.update({
                "user_type": 2,
                "group_id": 1,
                "user_allow_massemail" : "0"
            })

        # Add user to database
        sqlfile.insert("users", user)

        # Add user to registered group
        if self.name == "Anonymous":
            sqlfile.insert("user_group", {
                "group_id" : "1",
                "user_id" : "1",
                "user_pending" : "0"
            })
        else:
            sqlfile.insert("user_group", {
                "group_id" : 2,
                "user_id" : self.newid,
                "user_pending" : 0
            })

        for group in self.groups:
            group_leader = 1 if group.leader_name == self.name else 0
            sqlfile.insert("user_group", {
                "group_id" : group.newid,
                "user_id" : self.newid,
                "user_pending" : 0,
                "group_leader": group_leader
            })

        # Check if the user is the administrator
        if self.name == self.config["admin_name"]:
            # Add user to global moderators group
            sqlfile.insert("user_group", {
                "group_id" : 4,
                "user_id" : self.newid,
                "user_pending" : 0
            })

            # Send a private message confirming the import was successful
            parser = htmltobbcode.Parser(self.root)
            parser.feed(PM_POST)
            post = parser.get_post()

            sqlfile.insert("privmsgs", {
                'msg_id'          : 1,
                'author_id'       : self.newid,
                'message_time'    : self.root.dump_time,
                'message_subject' : PM_SUBJECT,
                'message_text'    : post.text,
                'bbcode_bitfield' : post.bitfield,
                'bbcode_uid'      : post.uid,
                'to_address'      : "u_{}".format(self.newid),
                'bcc_address'     : ""
            })

            # Add the message in the inbox
            sqlfile.insert("privmsgs_to", {
                'msg_id'	   : 1,
                'user_id'	   : self.newid,
                'author_id'	   : self.newid,
                'folder_id'	   : -1
            })
            # Add the message in the outbox
            sqlfile.insert("privmsgs_to", {
                'msg_id'	   : 1,
                'user_id'	   : self.newid,
                'author_id'	   : self.newid,
                'folder_id'	   : 0
            })

class UsersPage(Node):
    """
    Node representing a page of the list of users
    """
    def __init__(self, page_id):
        Node.__init__(self, page_id)

    def _export_(self):
        self.logger.debug('Récupération des membres (page %d)', self.id)

        params = {
            "mode" : "joined",
            "order" : "",
            "start" : self.id,
            "username" : ""
        }
        response = self.session.get("/memberlist", params=params)
        document = html.fromstring(response.content)

        try:
            form = document.cssselect('form[action="/memberlist"]')[0]
            table = form.xpath('following-sibling::table[@class="forumline"]')[0]
        except IndexError:
            raise ParsingError(document)

        urlpattern = re.compile(r"/u(\d+)")
        stylepattern = re.compile(r"color:#(.{6})")

        for row in table.cssselect("tr"):
            cols = row.cssselect("td")
            if not cols:
                continue

            try:
                link = cols[1].cssselect("a")[0]
                name = cols[2].text_content()

                posts = int(cols[6].text_content())

                regdate = parse_userlist_date(cols[4].text_content())
                lastvisit = parse_date(cols[5].text_content())
                span = cols[2].cssselect("a span")
            except IndexError:
                raise ParsingError(document)

            match = urlpattern.fullmatch(clean_url(link.get("href")))
            if not match:
                continue

            user_id = int(match.group(1))

            colour = ""
            if span:
                match = stylepattern.fullmatch(span[0].get("style", ""))
                if match:
                    colour = match.group(1)

            self.add_child(User(user_id, name, posts, regdate, lastvisit, colour))

@Node.expose("encoding", count="users_count")
class Users(PaginatedNode):
    """
    Node used to export the users
    """
    # Attributes to save
    STATE_KEEP = ["count", "encoding"]

    def __init__(self):
        PaginatedNode.__init__(self, "users")
        # User ids start at one, the first one is the anonymous user,
        # and the second one is the administrator
        self.count = Counter(len(BOTS) + 3)
        self.encoding = None

    def _export_(self):
        self.logger.info('Récupération des membres')

        self.add_child(AnonymousUser())

        # Get the encoding of the admin panel (will be used later to encode POST data)
        params = {
            "part" : "users_groups",
            "sub" : "users"
        }
        response = self.session.get_admin("/admin/index.forum", params=params)
        document = html.fromstring(response.content)
        self.encoding = document.getroottree().docinfo.encoding

        response = self.session.get("/memberlist")
        for page in pages(response.content):
            self.add_child(UsersPage(page))

    def _dump_(self, sqlfile):
        user_id = 3
        # Add bots
        for bot in BOTS:
            sqlfile.insert("users", {
                "user_id" : user_id,
                "user_type" : "2",
                "group_id" : "6",
                "user_regdate" : self.root.startdate,
                "username" : bot["name"],
                "username_clean" : bot["name"].lower(),
                "user_passchg" : self.root.dump_time,
                "user_lastmark" : self.root.dump_time,
                "user_lang" : self.config["default_lang"],
                "user_dateformat" : "D M d, Y g:i a",
                "user_style" : "1",
                "user_colour" : "9E8DA7",
                "user_allow_pm" : "0",
                "user_allow_massemail" : "0"})
            sqlfile.insert("user_group", {
                "group_id" : "6",
                "user_id" : user_id,
                "user_pending" : "0"})
            sqlfile.insert("bots", {
                "bot_name" : bot["name"],
                "user_id" : user_id,
                "bot_agent" : bot["agent"]})

            user_id += 1
