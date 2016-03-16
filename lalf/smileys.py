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
import re
import os.path
from pyquery import PyQuery
from PIL import Image
from io import BytesIO

from lalf.config import config
from lalf.node import Node
from lalf.smileyspage import SmileysPage
from lalf import session
from lalf import phpbb
from lalf import sql

logger = logging.getLogger("lalf")

DEFAULT_SMILEYS = {
    ":D" : {
        "code" : ":D",
        "emotion" : "Very Happy",
        "smiley_url" : "icon_e_biggrin.gif"},
    ":-D" : {
        "code" : ":-D",
        "emotion" : "Very Happy",
        "smiley_url" : "icon_e_biggrin.gif"},
    ":grin:" : {
        "code" : ":grin:",
        "emotion" : "Very Happy",
        "smiley_url" : "icon_e_biggrin.gif"},
    ":)" : {
        "code" : ":)",
        "emotion" : "Smile",
        "smiley_url" : "icon_e_smile.gif"},
    ":-)" : {
        "code" : ":-)",
        "emotion" : "Smile",
        "smiley_url" : "icon_e_smile.gif"},
    ":smile:" : {
        "code" : ":smile:",
        "emotion" : "Smile",
        "smiley_url" : "icon_e_smile.gif"},
    ";)" : {
        "code" : ";)",
        "emotion" : "Wink",
        "smiley_url" : "icon_e_wink.gif"},
    ";-)" : {
        "code" : ";-)",
        "emotion" : "Wink",
        "smiley_url" : "icon_e_wink.gif"},
    ":wink:" : {
        "code" : ":wink:",
        "emotion" : "Wink",
        "smiley_url" : "icon_e_wink.gif"},
    ":(" : {
        "code" : ":(",
        "emotion" : "Sad",
        "smiley_url" : "icon_e_sad.gif"},
    ":-(" : {
        "code" : ":-(",
        "emotion" : "Sad",
        "smiley_url" : "icon_e_sad.gif"},
    ":sad:" : {
        "code" : ":sad:",
        "emotion" : "Sad",
        "smiley_url" : "icon_e_sad.gif"},
    ":o" : {
        "code" : ":o",
        "emotion" : "Surprised",
        "smiley_url" : "icon_e_surprised.gif"},
    ":-o" : {
        "code" : ":-o",
        "emotion" : "Surprised",
        "smiley_url" : "icon_e_surprised.gif"},
    ":eek:" : {
        "code" : ":eek:",
        "emotion" : "Surprised",
        "smiley_url" : "icon_e_surprised.gif"},
    ":shock:" : {
        "code" : ":shock:",
        "emotion" : "Shocked",
        "smiley_url" : "icon_eek.gif"},
    ":?" : {
        "code" : ":?",
        "emotion" : "Confused",
        "smiley_url" : "icon_e_confused.gif"},
    ":-?" : {
        "code" : ":-?",
        "emotion" : "Confused",
        "smiley_url" : "icon_e_confused.gif"},
    ":???:" : {
        "code" : ":???:",
        "emotion" : "Confused",
        "smiley_url" : "icon_e_confused.gif"},
    "8-)" : {
        "code" : "8-)",
        "emotion" : "Cool",
        "smiley_url" : "icon_cool.gif"},
    ":cool:" : {
        "code" : ":cool:",
        "emotion" : "Cool",
        "smiley_url" : "icon_cool.gif"},
    ":lol:" : {
        "code" : ":lol:",
        "emotion" : "Laughing",
        "smiley_url" : "icon_lol.gif"},
    ":x" : {
        "code" : ":x",
        "emotion" : "Mad",
        "smiley_url" : "icon_mad.gif"},
    ":-x" : {
        "code" : ":-x",
        "emotion" : "Mad",
        "smiley_url" : "icon_mad.gif"},
    ":mad:" : {
        "code" : ":mad:",
        "emotion" : "Mad",
        "smiley_url" : "icon_mad.gif"},
    ":P" : {
        "code" : ":P",
        "emotion" : "Razz",
        "smiley_url" : "icon_razz.gif"},
    ":-P" : {
        "code" : ":-P",
        "emotion" : "Razz",
        "smiley_url" : "icon_razz.gif"},
    ":razz:" : {
        "code" : ":razz:",
        "emotion" : "Razz",
        "smiley_url" : "icon_razz.gif"},
    ":oops:" : {
        "code" : ":oops:",
        "emotion" : "Embarrassed",
        "smiley_url" : "icon_redface.gif"},
    ":cry:" : {
        "code" : ":cry:",
        "emotion" : "Crying or Very Sad",
        "smiley_url" : "icon_cry.gif"},
    ":evil:" : {
        "code" : ":evil:",
        "emotion" : "Evil or Very Mad",
        "smiley_url" : "icon_evil.gif"},
    ":twisted:" : {
        "code" : ":twisted:",
        "emotion" : "Twisted Evil",
        "smiley_url" : "icon_twisted.gif"},
    ":roll:" : {
        "code" : ":roll:",
        "emotion" : "Rolling Eyes",
        "smiley_url" : "icon_rolleyes.gif"},
    ":!:" : {
        "code" : ":!:",
        "emotion" : "Exclamation",
        "smiley_url" : "icon_exclaim.gif"},
    ":?:" : {
        "code" : ":?:",
        "emotion" : "Question",
        "smiley_url" : "icon_question.gif"},
    ":idea:" : {
        "code" : ":idea:",
        "emotion" : "Idea",
        "smiley_url" : "icon_idea.gif"},
    ":arrow:" : {
        "code" : ":arrow:",
        "emotion" : "Arrow",
        "smiley_url" : "icon_arrow.gif"},
    ":|" : {
        "code" : ":|",
        "emotion" : "Neutral",
        "smiley_url" : "icon_neutral.gif"},
    ":-|" : {
        "code" : ":-|",
        "emotion" : "Neutral",
        "smiley_url" : "icon_neutral.gif"},
    ":mrgreen:" : {
        "code" : ":mrgreen:",
        "emotion" : "Mr. Green",
        "smiley_url" : "icon_mrgreen.gif"},
    ":geek:" : {
        "code" : ":geek:",
        "emotion" : "Geek",
        "smiley_url" : "icon_e_geek.gif"},
    ":ugeek:" : {
        "code" : ":ugeek:",
        "emotion" : "Uber Geek",
        "smiley_url" : "icon_e_ugeek.gif"},

    "8)" : {
        "code" : "8)",
        "emotion" : "Cool",
        "smiley_url" : "icon_cool.gif",
        "smiley_width" : "15",
        "smiley_height" : "17",
        "smiley_order" : "43",
        "display_on_posting" : "0"}
}

class Smileys(Node):
    STATE_KEEP = ["default_smileys", "smileys", "order"]

    def __init__(self, parent):
        Node.__init__(self, parent)
        self.default_smileys = DEFAULT_SMILEYS
        self.smileys = {}
        self.order = len(DEFAULT_SMILEYS)

    def _export_(self):
        logger.info('Récupération des émoticones')

        params = {
            "part" : "themes",
            "sub" : "avatars",
            "mode" : "smilies"
        }
        r = session.get_admin("/admin/index.forum", params=params)
        result = re.search(r'function do_pagination_start\(\)[^\}]*start = \(start > \d+\) \? (\d+) : start;[^\}]*start = \(start - 1\) \* (\d+);[^\}]*\}', r.text)

        try:
            pages = int(result.group(1))
            smileysperpage = int(result.group(2))
        except:
            pages = 1
            smileysperpage = 0

        for page in range(0, pages):
            self.children.append(SmileysPage(self, page*smileysperpage))
