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
Module handling the exportation of the smilies
"""

import os
from io import BytesIO

from lxml import html
from PIL import Image

from lalf.node import Node, PaginatedNode, Page, ParsingError
from lalf.util import Counter, pages
from lalf.phpbb import SMILIES

class ExistingSmiley(Node):
    """
    Node representing a smiley that already exists in phpbb
    """
    def __init__(self, smiley_id, infos):
        Node.__init__(self, smiley_id)
        self.infos = infos

        self.code = infos["code"]
        self.emotion = infos["emotion"]
        self.smiley_url = infos["smiley_url"]

class Smiley(Node):
    """
    Node representing a smiley

    Attrs:
        id (int): The index of the smiley in the original forum (used
                  to convert html to bbcode)
        code (str): The bbcode of the smiley
        url (str): The url of the image of the smiley
        emotion (str): An expression describing the smiley

        smiley_url (str): The filename of the smiley in the new forum
        width (int): The width of the image
        height (int): The height of the image
        order (int): The position of the smiley in the interface
    """
    def __init__(self, smiley_id, code, url, emotion):
        Node.__init__(self, smiley_id)
        self.code = code
        self.url = url
        self.emotion = emotion

        self.smiley_url = None
        self.width = None
        self.height = None

    def _export_(self):
        if self.config["export_smilies"]:
            self.logger.info("Téléchargement de l'émoticone \"%s\"", self.code)

            # Create the smilies directory if necessary
            dirname = os.path.join("images", "smilies")
            if not os.path.isdir(dirname):
                os.makedirs(dirname)

            # Download the image and get its dimensions and format
            response = self.session.get_image(self.url)
            try:
                with Image.open(BytesIO(response.content)) as image:
                    self.smiley_url = "icon_exported_{}.{}".format(self.id, image.format.lower())
                    self.width = image.width
                    self.height = image.height
            except IOError:
                self.logger.warning("Le format de l'émoticone %s est inconnu", self.code)
            else:
                # Save the image
                with open(os.path.join(dirname, self.smiley_url), "wb") as fileobj:
                    fileobj.write(response.content)

    def _dump_(self, sqlfile):
        order = self.smilies.count.newid()

        sqlfile.insert("smilies", {
            "code" : self.code,
            "emotion" : self.emotion,
            "smiley_url" : self.smiley_url,
            "smiley_width" : self.width,
            "smiley_height" : self.height,
            "smiley_order" : order,
            "display_on_posting" : "0"
        })

class SmiliesPage(Page):
    """
    Node representing a page of the list of smilies

    Attrs:
        page (int): The index of the first smiley on the page
    """
    def __init__(self, page_id):
        Page.__init__(self, page_id)

    def _export_(self):
        self.logger.debug('Récupération des émoticones (page %d)', self.id)

        # Get the page
        params = {
            "part" : "themes",
            "sub" : "avatars",
            "mode" : "smilies",
            "start" : self.id
        }
        response = self.session.get_admin("/admin/index.forum", params=params)
        document = html.fromstring(response.content)

        for row in document.cssselect('form#smiliesList table tr'):
            cols = row.cssselect("td")
            if len(cols) >= 4:
                try:
                    smiley_id = int(cols[0].text_content())
                    code = cols[1].text_content()
                    url = cols[2].cssselect("img")[0].get("src")
                    emotion = cols[3].text_content()
                except (IndexError, ValueError):
                    raise ParsingError(document)

                if code in SMILIES:
                    self.logger.debug("L'émoticone \"%s\" existe déjà dans phpbb.", code)
                    self.add_child(ExistingSmiley(smiley_id, SMILIES[code]))
                else:
                    self.add_child(Smiley(smiley_id, code, url, emotion))

class Smilies(PaginatedNode):
    """
    Node used to export the smilies

    Attrs:
        count (Counter): The number of smilies
    """
    def __init__(self):
        PaginatedNode.__init__(self, "smilies")
        self.count = Counter(1)

    def _export_(self):
        self.logger.info('Récupération des émoticones')

        params = {
            "part" : "themes",
            "sub" : "avatars",
            "mode" : "smilies"
        }
        response = self.session.get_admin("/admin/index.forum", params=params)
        for page in pages(response.content):
            self.add_page(SmiliesPage(page))

    def _dump_(self, sqlfile):
        self.count.reset()

        sqlfile.truncate("smilies")

        for smiley in SMILIES.values():
            smiley["smiley_order"] = self.smilies.count.newid()
            sqlfile.insert("smilies", smiley)
