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
import time
from pyquery import PyQuery
import urllib.parse

from lalf.userspage import UsersPage
from lalf.ocruser import OcrUser
from lalf.exceptions import *
from lalf.util import month
from lalf import phpbb
from lalf import session
    
class OcrUsersPage(UsersPage):
    def _export_(self):
        logger.debug('Récupération des membres (page %d)', self.page)

        params = {
            "mode" : "joined",
            "order" : "",
            "start" : self.page,
            "username" : ""
        }
        r = session.get("/memberlist", params=params)
        d = PyQuery(r.text)

        n = 2 + len(phpbb.bots) + self.page

        table = PyQuery(d("form[action=\"/memberlist\"]").nextAll("table.forumline").eq(0))
        
        first = True
        for i in table.find("tr"):
            if first:
                first = False
                continue
            
            e = PyQuery(i)
            id = int(re.search("u(\d+)$", e("td a").eq(0).attr("href")).group(1))

            name = e("td a").eq(1).text()
            posts = int(e("td").eq(6).text())
            
            date = e("td").eq(4).text().split("/")
            date = time.mktime(time.struct_time((int(date[2]),int(date[1]),int(date[0]),0,0,0,0,0,0)))

            self.children.append(OcrUser(self.parent, id, n, name, posts, date))
            
            n += 1
                        
    def __setstate__(self, dict):
        UsersPage.__setstate__(self, dict)
        self.children_exported = False
