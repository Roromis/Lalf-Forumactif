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
from pyquery import PyQuery

from lalf.node import Node
from lalf.smiley import Smiley
from lalf import session

class SmileysPage(Node):
    STATE_KEEP = ["page"]

    def __init__(self, parent, page):
        Node.__init__(self, parent)
        self.page = page

    def _export_(self):
        logger.info('Récupération des émoticones (page %d)', self.page)

        params = {
            "part" : "themes",
            "sub" : "avatars",
            "mode" : "smilies",
            "start" : self.page
        }
        r = session.get_admin("/admin/index.forum", params=params)
        d = PyQuery(r.text)
        
        for i in d('table tr'):
            e = PyQuery(i)
            if e("td").eq(0).text() and e("td").eq(0).attr("colspan") == None:
                smiley_id = e("td").eq(0).text()
                code = e("td").eq(1).text()
                url = e("td").eq(2).find("img").eq(0).attr("src")
                emotion = e("td").eq(3).text()

                if code in self.parent.default_smileys:
                    self.parent.smileys[smiley_id] = self.parent.default_smileys[code]
                else:
                    child = Smiley(self, smiley_id, code, url, emotion)
                    self.children.append(child)
