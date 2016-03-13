# -*- coding: utf-8 -*-
#
# This file is part of Lalf.
#
# Lalf is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lalf.  If not, see <http://www.gnu.org/licenses/>.

import logging
logger = logging.getLogger("lalf")

import re
import os.path
from pyquery import PyQuery
from PIL import Image
from io import BytesIO

from lalf.config import config
from lalf.node import Node
from lalf.smileyspage import SmileysPage
from lalf import session
from lalf.htmltobbcode import HtmltobbcodeParser
from lalf import phpbb
from lalf import sql

class Smileys(Node):
    STATE_KEEP = ["smileys"]

    def __init__(self, parent):
        Node.__init__(self, parent)
        self.smileys = {}

    def _export_(self):
        logger.info('Récupération des émoticones')

        HtmltobbcodeParser.smileys = self.smileys

        params = {
            "part" : "themes",
            "sub" : "avatars",
            "mode" : "smilies"
        }
        r = session.get_admin("/admin/index.forum", params=params)
        result = re.search('function do_pagination_start\(\)[^\}]*start = \(start > \d+\) \? (\d+) : start;[^\}]*start = \(start - 1\) \* (\d+);[^\}]*\}', r.text)

        try:
            pages = int(result.group(1))
            smileysperpage = int(result.group(2))
        except:
            pages = 1
            smileysperpage = 0

        for page in range(0,pages):
            self.children.append(SmileysPage(self, page*smileysperpage))

    def _dump_(self, file):
        order = len(phpbb.smileys)

        codes = [smiley["code"] for smiley in phpbb.smileys]

        if config["export_smilies"] == "all":
            export = lambda s: s["code"] not in codes
        elif config["export_smilies"] == "used":
            export = lambda s: s["used"] and s["code"] not in codes
        else:
            export = lambda s: False

        for smiley_id, smiley in self.smileys.items():
            if export(smiley):

                dirname = os.path.join("images", "smilies")
                if not os.path.isdir(dirname):
                    os.makedirs(dirname)

                logger.debug("Téléchargement de l'émoticone \"%s\"", smiley["code"])

                r = session.get_image(smiley["icon"])
                with Image.open(BytesIO(r.content)) as image:
                    filename = "icon_exported_{}.{}".format(smiley_id, image.format.lower())

                    width, height = image.size
                    format = image.format

                with open(os.path.join(dirname, filename), "wb") as fileobj:
                    fileobj.write(r.content)

                phpbb.smileys.append({
                    "code": smiley["code"],
                    "emotion": smiley["emotion"],
                    "smiley_url": filename,
                    "export": True,
                    "smiley_width": width,
                    "smiley_height": height,
                    "smiley_order": order,
                    "display_on_posting": "0"})

                codes.append(smiley["code"])

                order += 1

        for smiley in phpbb.smileys:
            if smiley["export"]:
                sql.insert(file, "smilies", smiley, ["export"])

        phpbb.smileys = sorted(phpbb.smileys, key=lambda s:len(s["code"]), reverse=True)

    def __setstate__(self, dict):
        Node.__setstate__(self, dict)
        HtmltobbcodeParser.smileys = self.smileys
