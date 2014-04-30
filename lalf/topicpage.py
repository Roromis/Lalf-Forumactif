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

from pyquery import PyQuery
import time
import datetime
import re

from lalf.node import Node
from lalf.post import Post
from lalf.util import month
from lalf import session
from lalf import htmltobbcode

smileys = {}

class TopicPage(Node):

    """
    Attributes to save
    """
    STATE_KEEP = ["id", "page"]
    
    def __init__(self, parent, id, page):
        Node.__init__(self, parent)
        self.id = id
        self.page = page

    def _export_(self):
        logger.debug('Récupération des messages du sujet %d (page %d)', self.id, self.page)
        
        r = session.get("/t{id}p{page}-a".format(id=self.id, page=self.page))
        d = PyQuery(r.text)
        
        for i in d.find('tr.post'):
            e = PyQuery(i)
                
            id = int(e("td span.name a").attr("name"))

            logger.debug('Récupération du message %d (sujet %d, page %d)', id, self.id, self.page)
            
            author = e("td span.name").text()
            htmlpost = e("td div.postbody div").eq(0).html()
            if htmlpost:
                post = htmltobbcode.htmltobbcode(htmlpost, smileys)
            else:
                logging.warning('Le message  %d (sujet %d, page %d) semble être vide', id, self.id, self.page)
                post = ""

            title = e("table td span.postdetails").text()
            title = re.split(r'\s(?=(?:Lun|Mar|Mer|Jeu|Ven|Sam|Dim|Hier|Aujourd\'hui)\b)', title)[0]
            title = title[7:]
                
            result = e("table td span.postdetails").text().split(" ")
            if result[-3] == "Aujourd'hui":
                date = e("table td span.postdetails").text().split(" ")[-3:]
                timestamp = time.mktime(datetime.datetime.combine(datetime.date.today(), datetime.time(int(date[2].split(":")[0]),int(date[2].split(":")[1]))).timetuple())
            elif result[-3] == "Hier":
                date = e("table td span.postdetails").text().split(" ")[-3:]
                timestamp = time.mktime(datetime.datetime.combine(datetime.date.today()-datetime.timedelta(1), datetime.time(int(date[2].split(":")[0]),int(date[2].split(":")[1]))).timetuple())
            else:
                date = e("table td span.postdetails").text().split(" ")[-6:]
                timestamp = time.mktime(datetime.datetime(int(date[3]),month(date[2]),int(date[1]),int(date[5].split(":")[0]),int(date[5].split(":")[1])).timetuple())

            self.children.append(Post(self.parent, id, post, title, self.id, int(timestamp), author))
