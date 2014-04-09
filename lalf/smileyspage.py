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
