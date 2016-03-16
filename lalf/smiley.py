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

import logging
logger = logging.getLogger("lalf")

import re
import os
from pyquery import PyQuery

from PIL import Image
from io import BytesIO

from lalf.node import Node
from lalf import session
from lalf import sql
from lalf.config import config

class Smiley(Node):
    STATE_KEEP = ["id", "code", "url", "emotion", "smiley_url", "width", "height", "order"]
    
    def __init__(self, parent, smiley_id, code, url, emotion):
        Node.__init__(self, parent)
        self.id = smiley_id
        self.code = code
        self.url = url
        self.emotion = emotion

        self.smiley_url = None
        self.width = None
        self.height = None
        self.order = None

    def _export_(self):
        if config["export_smilies"]:
            logger.debug("Téléchargement de l'émoticone \"%s\"", self.code)

            dirname = os.path.join("images", "smilies")
            if not os.path.isdir(dirname):
                os.makedirs(dirname)

            r = session.get_image(self.url)
            with Image.open(BytesIO(r.content)) as image:
                self.smiley_url = "icon_exported_{}.{}".format(self.id, image.format.lower())
                self.width = image.width
                self.height = image.height

            self.parent.parent.order += 1
            self.order = self.parent.parent.order

            with open(os.path.join(dirname, self.smiley_url), "wb") as fileobj:
                fileobj.write(r.content)

        self.parent.parent.smileys[self.id] = {
            "code" : self.code,
            "emotion" : self.emotion,
            "smiley_url" : self.smiley_url}

    def _dump_(self, file):
        sql.insert(file, "smilies", {
            "code" : self.code,
            "emotion" : self.emotion,
            "smiley_url" : self.smiley_url,
            "smiley_width" : self.width,
            "smiley_height" : self.height,
            "smiley_order" : self.order,
            "display_on_posting" : "0"
        })
