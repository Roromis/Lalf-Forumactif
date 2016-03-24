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
Module handling the exportation of users (DEPRECATED)

This is the module that previously handled the exporation of
users. Using it can (and probably will) prevent you from having access
to the users list of your administration panel during 24h (thus
preventing you from exporting them).

The ocrusers module now handles the exportation, using this users
module to create the entries in the sql file.
"""

import re
import time
import hashlib
import urllib.parse
import base64
from binascii import crc32

from pyquery import PyQuery

from lalf.node import Node
from lalf.util import Counter, pages, month, random_string
from lalf.phpbb import BOTS
from lalf import htmltobbcode

EMAIL = base64.b64decode(b'bGFsZkBvcGVubWFpbGJveC5vcmc=\n').decode("utf-8")

PM_SUBJECT = "Félicitations !"
PM_POST = """Félicitations !

Vous avez terminé la première partie de l'importation. Suivez la
partie Resynchronisation du README pour terminer la migration.

Une fois la migration terminée, n'hésitez pas à m'envoyer vos
remerciements à l'adresse {}. Si vous le souhaitez, vous pouvez me
supporter en m'offrant un café ;) , j'accepte les dons en
bitcoins.""".format(EMAIL)

def email_hash(email):
    """
    Email hash function used by phpbb
    """
    return str(crc32(email.encode("utf-8"))&0xffffffff) + str(len(email))

class MemberPageBlocked(Exception):
    """
    Exception raised when the member page is blocked
    """

    def __str__(self):
        return (
            "Vous avez été bloqué par forumactif. Attendez d'être débloqué avant de relancer le "
            "script (environ 24h).\n\n"

            "Pour savoir si vous êtes bloqué, essayez d'accéder à la deuxième page de la gestion "
            "des utilisateurs dans votre panneau d'administration (Utilisateurs & Groupes > "
            "Gestion des utilisateurs). Si vous êtes bloqué, vous allez être redirigé vers la page "
            "d'accueil de votre panneau d'administration.\n\n"

            "Pour ne pas avoir à attendre, utilisez l'otion use_ocr."
        )

def md5(string):
    """
    Compute the md5 hash of a string
    """
    return hashlib.md5(string.encode("utf8")).hexdigest()

class User(Node):
    """
    Node representing a user

    Attrs:
        oldid (int): The id of the user in the old forum
        name (str): His username
        mail (str): The email address of the user
        posts (int): The number of posts
        date (int): subscription date (timestamp)
        lastvisit (int): date of last visit (timestamp)

        newid (int): The id of the user in the new forum
    """
    STATE_KEEP = ["oldid", "newid", "name", "mail", "posts", "date", "lastvisit"]

    def __init__(self, oldid, name, mail, posts, date, lastvisit):
        Node.__init__(self)
        self.oldid = oldid
        self.name = name
        self.mail = mail
        self.posts = posts
        self.date = date
        self.lastvisit = lastvisit

        self.newid = None

    def _export_(self):
        if self.newid is None:
            if self.name == self.config["admin_name"]:
                self.newid = 2
            else:
                self.newid = self.users_count.value
                self.users_count += 1

            self.root.current_users += 1
            self.ui.update()

            self.user_names[self.name] = self
            self.user_ids[self.oldid] = self

    def confirm_email(self, _):
        """
        Let the user confirm the email address if it could not be
        validated (for compatibility with OcrUser)
        """
        return

    def _dump_(self, sqlfile):
        user = {
            "user_id" : self.newid,
            "group_id" : "2",
            "user_regdate" : self.date,
            "username" : self.name,
            "username_clean" : self.name.lower(),
            "user_password" : md5(random_string()),
            "user_pass_convert" : "1",
            "user_email" : self.mail,
            "user_email_hash" : email_hash(self.mail),
            "user_lastvisit" : self.lastvisit,
            #"user_lastpost_time" (TODO)
            "user_posts" : self.posts,
            "user_lang" : "fr", # TODO : define in config
            "user_style" : "1",
            #"user_rank" (TODO)
            #"user_colour" (TODO)
            #"user_avatar" (TODO)
            #"user_sig" (TODO)
            #"user_from" (TODO)
            #"user_website" (TODO) (...)
        }

        # Check if the user is the administrator
        if self.name == self.config["admin_name"]:
            user.update({
                "user_type": 3,
                "group_id" : 5,
                "user_password" : md5(self.config["admin_password"]),
                "user_rank" : 1,
                "user_colour" : "AA0000", # TODO : get actual color?
                "user_new_privmsg" : 1,
                "user_unread_privmsg" : 1,
                "user_last_privmsg" : self.root.dump_time
            })

        # Add user to database
        sqlfile.insert("users", user)

        # Add user to registered group
        sqlfile.insert("user_group", {
            "group_id" : 2,
            "user_id" : self.newid,
            "user_pending" : 0
        })

        # Check if the user is the administrator
        if self.name == self.config["admin_name"]:
            # Add user to global moderators group
            sqlfile.insert("user_group", {
                "group_id" : 4,
                "user_id" : self.newid,
                "user_pending" : 0
            })
            # Add user to administrators group
            sqlfile.insert("user_group", {
                "group_id" : 5,
                "user_id" : self.newid,
                "user_pending" : 0,
                "group_leader" : 1
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
                'bbcode_uid'      :post. uid,
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
    # Attributes to keep
    STATE_KEEP = ["page"]

    def __init__(self, page):
        Node.__init__(self)
        self.page = page

    def _export_(self):
        self.logger.debug('Récupération des membres (page %d)', self.page)

        # Get the page of list of users from the administration panel
        params = {
            "part" : "users_groups",
            "sub" : "users",
            "start" : self.page
        }
        response = self.session.get_admin("/admin/index.forum", params=params)

        # Check if the page was blocked
        query = urllib.parse.urlparse(response.url).query
        query = urllib.parse.parse_qs(query)
        if "start" not in query:
            raise MemberPageBlocked()

        document = PyQuery(response.text)

        for element in document('tbody tr'):
            e = PyQuery(element)
            oldid = int(re.search(r"&u=(\d+)&", e("td a").eq(0).attr("href")).group(1))

            self.logger.debug('Récupération du membre %d', oldid)
            name = e("td a").eq(0).text()
            mail = e("td a").eq(1).text()
            posts = int(e("td").eq(2).text())

            date = e("td").eq(3).text().split(" ")
            date = int(time.mktime(time.struct_time(
                (int(date[2]), month(date[1]), int(date[0]), 0, 0, 0, 0, 0, 0))))

            lastvisit = e("td").eq(4).text()

            if lastvisit != "":
                lastvisit = lastvisit.split(" ")
                lastvisit = int(time.mktime(time.struct_time(
                    (int(lastvisit[2]), month(lastvisit[1]), int(lastvisit[0]), 0, 0, 0, 0, 0, 0))))
            else:
                lastvisit = 0

            self.add_child(User(oldid, name, mail, posts, date, lastvisit))

@Node.expose(count="users_count")
class Users(Node):
    """
    Node used to export the users (DEPRECATED)
    """

    # Attributes to save
    STATE_KEEP = ["count"]

    def __init__(self):
        Node.__init__(self)
        # User ids start at one, the first one is the anonymous user,
        # and the second one is the administrator
        self.count = Counter(len(BOTS) + 3)

    def _export_(self):
        self.logger.info('Récupération des membres')

        # Get the list of users from the administration panel
        params = {
            "part" : "users_groups",
            "sub" : "users"
        }
        response = self.session.get_admin("/admin/index.forum", params=params)
        for page in pages(response.text):
            self.add_child(UsersPage(page))

    def _dump_(self, sqlfile):
        # Add anonymous user
        sqlfile.insert("users", {
            "user_id" : "1",
            "user_type" : "2",
            "group_id" : "1",
            "username" : "Anonymous",
            "username_clean" : "anonymous",
            #"user_regdate" : creation date, (TODO)
            "user_lang" : "fr", # TODO : define in config
            "user_style" : "1",
            "user_allow_massemail" : "0"})
        sqlfile.insert("user_group", {
            "group_id" : "1",
            "user_id" : "1",
            "user_pending" : "0"})

        user_id = 3
        # Add bots
        for bot in BOTS:
            sqlfile.insert("users", {
                "user_id" : user_id,
                "user_type" : "2",
                "group_id" : "6",
                #"user_regdate" : creation date, (TODO)
                "username" : bot["name"],
                "username_clean" : bot["name"].lower(),
                "user_passchg" : self.root.dump_time,
                "user_lastmark" : self.root.dump_time,
                "user_lang" : "fr", # TODO : define in config
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
