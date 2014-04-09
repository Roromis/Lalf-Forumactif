import logging
logger = logging.getLogger("lalf")

import re
import time
from pyquery import PyQuery
import urllib.parse
import session
from userspage import UsersPage
from ocruser import OcrUser
from exceptions import *
import phpbb

def month(s):
    if s.startswith("Ja"):
        return 1 
    elif s.startswith("F"):
        return 2
    elif s.startswith("Mar"):
        return 3
    elif s.startswith("Av"):
        return 4
    elif s.startswith("Mai"):
        return 5
    elif s.startswith("Juin"):
        return 6
    elif s.startswith("Juil"):
        return 7
    elif s.startswith("Ao"):
        return 8
    elif s.startswith("S"):
        return 9
    elif s.startswith("O"):
        return 10
    elif s.startswith("N"):
        return 11
    elif s.startswith("D"):
        return 12
    
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
