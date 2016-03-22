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
import time
import subprocess

from PIL import Image
from pyquery import PyQuery

from lalf.users import Users, UsersPage, User

from lalf.util import month, clean_filename, pages

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

class OcrUser(User):
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
        trust (int): level of trust in the email address
            - 3 if the email has been verified to be correct
            - 2 if the email could not be verified
            - 1 if the email is probably incorrect
            - 0 if the email could not be exported
        img (str): The path of the image containing the email
    """
    # Attributes to save
    STATE_KEEP = User.STATE_KEEP + ["trust", "img"]

    def __init__(self, oldid, name, posts, date):
        User.__init__(self, oldid, name, None, posts, date, 0)
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
        document = PyQuery(response.text)
        for element in document('tbody tr'):
            e = PyQuery(element)

            if e("td a").eq(0).text() == self.name:
                return True

        return False

    def _export_(self):
        self.logger.debug('Récupération du membre %d', self.oldid)

        User._export_(self)

        if not self.exported:
            self.root.current_users += 1
            self.ui.update()

        # Search for this user in the administration panel
        try:
            encodedname = self.name.encode("latin1")
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

        document = PyQuery(response.text)
        for element in document('tbody tr'):
            e = PyQuery(element)
            if e("td a").eq(0).text() == self.name:
                # The user was found
                self.mail = e("td a").eq(1).text()

                if self.mail == "" and e("td a").eq(0).is_('img'):
                    # The administration panel has been blocked, the
                    # email is replaced by an image, download it
                    response = self.session.get(e("td a img").eq(0).attr("src"))
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
                else:
                    # The administration panel hasn't been blocked
                    # yet, the email is available
                    self.trust = 3

                lastvisit = e("td").eq(4).text()
                if lastvisit != "":
                    lastvisit = lastvisit.split(" ")
                    self.lastvisit = int(time.mktime(time.struct_time(
                        (int(lastvisit[2]), month(lastvisit[1]), int(lastvisit[0]), 0, 0, 0, 0, 0,
                         0))))
                else:
                    self.lastvisit = 0

    def confirm_email(self, retries=2):
        """
        Let the user confirm the email address if it could not be
        validated
        """
        if self.trust == 2:
            self.logger.info(
                "L'adresse email de l'utilisateur %s est probablement valide "
                "mais n'a pas pu être validée.)", self.name)
            print((
                "Veuillez saisir l'adresse email de l'utilisateur {} (laissez "
                "vide si l'adresse {} est correcte) :").format(self.name, self.mail))
            self.mail = input("> ").strip()
        elif self.trust == 1:
            self.logger.info(
                "L'adresse email de l'utilisateur %s est probablement invalide.)", self.name)
            print((
                "Veuillez saisir l'adresse email de l'utilisateur {} (laissez "
                "vide si l'adresse {} est correcte) :").format(self.name, self.mail))
            self.mail = input("> ").strip()
        elif self.trust == 0:
            self.logger.info(
                "L'adresse email de l'utilisateur %s n'a pas pu être exportée.", self.name)
            if retries == 0:
                print("Veuillez saisir l'adresse email de l'utilisateur {} :".format(self.name))
                self.mail = input("> ").strip()
            else:
                self._export_(False)
                self.confirm_email(retries-1)

class OcrUsersPage(UsersPage):
    """
    Node representing a page of the list of users
    """
    def _export_(self):
        self.logger.debug('Récupération des membres (page %d)', self.page)

        params = {
            "mode" : "joined",
            "order" : "",
            "start" : self.page,
            "username" : ""
        }
        response = self.session.get("/memberlist", params=params)
        document = PyQuery(response.text)

        table = PyQuery(document("form[action=\"/memberlist\"]").next_all("table.forumline").eq(0))

        first = True
        for element in table.find("tr"):
            # Skip first row
            if first:
                first = False
                continue

            e = PyQuery(element)
            oldid = int(re.search(r"u(\d+)$", e("td a").eq(0).attr("href")).group(1))

            name = e("td a").eq(1).text()
            posts = int(e("td").eq(6).text())

            date = e("td").eq(4).text().split("/")
            date = int(time.mktime(time.struct_time(
                (int(date[2]), int(date[1]), int(date[0]), 0, 0, 0, 0, 0, 0))))

            self.add_child(OcrUser(oldid, name, posts, date))

class OcrUsers(Users):
    """
    Node used to export the users
    """
    def _export_(self):
        self.logger.info('Récupération des membres')

        response = self.session.get("/memberlist")
        for page in pages(response.text):
            self.add_child(OcrUsersPage(page))
