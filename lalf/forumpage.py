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
from lalf.topic import Topic
from lalf import session

topicids = []

class ForumPage(Node):

    """
    Attributes to save
    """
    STATE_KEEP = ["id", "newid", "type", "page"]
    
    def __init__(self, parent, oldid, newid, page):
        """
        id -- id in the old forum
        newid -- id in the new forum
        type -- c if the forum is a category, else f
        page -- offset
        """
        Node.__init__(self, parent)
        self.oldid = oldid
        self.newid = newid
        self.page = page

    def _export_(self):

        type_dic = {'Post-it:': 1,
                    'Annonce:': 2,
                    'Annonce globale:': 3}

        logger.debug('Récupération du forum %s (page %d)', self.oldid, self.page)

        # Get the page
        r = session.get("/{}p{}-a".format(self.oldid, self.page))
        d = PyQuery(r.text)

        # Get the topics
        for i in d.find('div.topictitle'):
            e = PyQuery(i)
            
            id = int(re.search("/t(\d+)-.*", e("a").attr("href")).group(1))
            if id not in topicids:
                f = e.parents().eq(-2)
                locked = 1 if ("verrouillé" in f("td img").eq(0).attr("alt")) else 0
                views = int(f("td").eq(5).text())
                type = type_dic.get(e("strong").text(),0)
                title = e("a").text()

                self.children.append(Topic(self.parent, id, type, self.newid, title, locked, views))
                topicids.append(id)
            else:
                # Topic has already been exported (it's a global announcement)
                logger.warning('Le sujet %d existe déjà.', id)

    def __setstate__(self, dict):
        Node.__setstate__(self, dict)
        for t in self.children:
            topicids.append(t.id)
