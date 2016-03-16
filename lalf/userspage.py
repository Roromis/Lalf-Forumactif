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
import time
from pyquery import PyQuery
import urllib.parse

from lalf.node import Node
from lalf.user import User
from lalf.exceptions import *
from lalf.util import month
from lalf import phpbb
from lalf import session
    
class UsersPage(Node):
    STATE_KEEP = ["page"]

    def __init__(self, parent, page):
        Node.__init__(self, parent)
        self.page = page

    def _export_(self):
        logger.debug('Récupération des membres (page %d)', self.page)

        params = {
            "part" : "users_groups",
            "sub" : "users",
            "start" : self.page
        }
        r = session.get_admin("/admin/index.forum", params=params)
        query = urllib.parse.urlparse(r.url).query
        query = urllib.parse.parse_qs(query)

        if "start" not in query:
            raise MemberPageBlocked()
        
        d = PyQuery(r.text)

        n = 2 + len(phpbb.bots) + self.page
        
        for i in d('tbody tr'):
            e = PyQuery(i)
            id = int(re.search("&u=(\d+)&", e("td a").eq(0).attr("href")).group(1))
    
            logger.debug('Récupération du membre %d', id)
            name = e("td a").eq(0).text()
            mail = e("td a").eq(1).text()
            posts = int(e("td").eq(2).text())
            
            date = e("td").eq(3).text().split(" ")
            date = time.mktime(time.struct_time((int(date[2]),month(date[1]),int(date[0]),0,0,0,0,0,0)))
            
            lastvisit = e("td").eq(4).text()
            
            if lastvisit != "":
                lastvisit = lastvisit.split(" ")
                lastvisit = time.mktime(time.struct_time((int(lastvisit[2]),month(lastvisit[1]),int(lastvisit[0]),0,0,0,0,0,0)))
            else:
                lastvisit = 0

            self.children.append(User(self.parent, id, n, name, mail, posts, date, lastvisit))
            
            n += 1
