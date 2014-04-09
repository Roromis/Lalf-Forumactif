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
            logger.debug('Récupération : membre %d', id)

            name = e("td a").eq(1).text()
            posts = int(e("td").eq(6).text())
            
            date = e("td").eq(4).text().split("/")
            date = time.mktime(time.struct_time((int(date[2]),int(date[1]),int(date[0]),0,0,0,0,0,0)))

            self.children.append(OcrUser(self.parent, id, n, name, posts, date))
            
            n += 1
                        
    def __setstate__(self, dict):
        UsersPage.__setstate__(self, dict)
        self.children_exported = False
