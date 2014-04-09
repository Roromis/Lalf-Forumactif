import logging
logger = logging.getLogger("lalf")

from pyquery import PyQuery
import time
import datetime

from lalf.node import Node
from lalf.post import Post
from lalf.util import month
from lalf import session
from lalf import htmltobbcode

smileys = {}

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
        r = session.get("/t{id}p{page}-a".format(id=self.id, page=self.page))
        d = PyQuery(r.text)
        
        for i in d.find('tr.post'):
            e = PyQuery(i)
                
            id = int(e("td span.name a").attr("name"))

            logger.debug('Récupération : message %d (topic %d)', id, self.id)
                
            author = e("td span.name").text()
            post = htmltobbcode.htmltobbcode(e("td div.postbody div").eq(0).html(), smileys)
                
            result = e("table td span.postdetails").text().split(" ")
            if result[-3] == "Aujourd'hui":
                title = " ".join(e("table td span.postdetails").text().split(" ")[1:-3])
                date = e("table td span.postdetails").text().split(" ")[-3:]
                timestamp = time.mktime(datetime.datetime.combine(datetime.date.today(), datetime.time(int(date[2].split(":")[0]),int(date[2].split(":")[1]))).timetuple())
            elif result[-3] == "Hier":
                title = " ".join(e("table td span.postdetails").text().split(" ")[1:-3])
                date = e("table td span.postdetails").text().split(" ")[-3:]
                timestamp = time.mktime(datetime.datetime.combine(datetime.date.today()-datetime.timedelta(1), datetime.time(int(date[2].split(":")[0]),int(date[2].split(":")[1]))).timetuple())
            else:
                title = " ".join(e("table td span.postdetails").text().split(" ")[1:-6])
                date = e("table td span.postdetails").text().split(" ")[-6:]
                timestamp = time.mktime(datetime.datetime(int(date[3]),month(date[2]),int(date[1]),int(date[5].split(":")[0]),int(date[5].split(":")[1])).timetuple())

            self.children.append(Post(self.parent, id, post, title, self.id, int(timestamp), author))
