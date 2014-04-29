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
from pyquery import PyQuery

from lalf.node import Node
from lalf import topicpage
from lalf import session

class SmileysPage(Node):
    STATE_KEEP = ["smileys", "page"]
    def __init__(self, parent, page):
        Node.__init__(self, parent)
        self.smileys = {}
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
        
        first = True
        for i in d('table tr'):
            """if first:
                first = False
                continue"""
            
            e = PyQuery(i)
            if e("td").eq(0).text() != None and e("td").eq(0).attr("colspan") == None:
                id = e("td").eq(0).text()
                code = e("td").eq(1).text()
                self.smileys[id] = code
                topicpage.smileys[id] = code

    def __setstate__(self, dict):
        Node.__setstate__(self, dict)
        for k,v in self.smileys.items():
            topicpage.smileys[k] = v
