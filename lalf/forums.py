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
from lalf.forum import Forum
from lalf import sql
from lalf import session

class Forums(Node):
    def _export_(self):
        logger.info('Récupération des forums')

        r = session.get("/a-f1/")
        d = PyQuery(r.text)
        
        levels = []
        n = 1
        left_id = 1
        
        for i in d.find("select option"):
            id = i.get("value", "-1")
            if id != "-1":
                title = re.search('(((\||\xa0)(\xa0\xa0\xa0))*)\|--([^<]+)', i.text).group(5)
                level = len(re.findall('(\||\xa0)\xa0\xa0\xa0', i.text))

                if level <= 0:
                    parent = None
                    parentid = 0
                else:
                    parent = levels[level-1]
                    parentid = parent.newid

                for l in range(level, len(levels)):
                    f = levels.pop()
                    f.right_id = left_id
                    left_id += 1

                forum = Forum(self.parent, int(id[1:]), n, left_id, id[0], parentid, title)
                levels.append(forum)
                self.children.append(forum)
                n += 1
                left_id += 1

        for l in range(0, len(levels)):
            f = levels.pop()
            f.right_id = left_id
            left_id += 1
