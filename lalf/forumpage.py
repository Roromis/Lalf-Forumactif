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
    
    def __init__(self, parent, id, newid, type, page):
        """
        id -- id in the old forum
        newid -- id in the new forum
        type -- c if the forum is a category, else f
        page -- offset
        """
        Node.__init__(self, parent)
        self.id = id
        self.newid = newid
        self.type = type
        self.page = page

    def _export_(self):
        logger.debug('Récupération du forum %s%s (page %d)', self.type, self.id, self.page)

        # Get the page
        r = session.get("/{type}{id}p{page}-a".format(type=self.type, id=self.id, page=self.page))
        d = PyQuery(r.text)

        # Get the topics
        for i in d.find('div.topictitle'):
            e = PyQuery(i)
            
            id = int(re.search("/t(\d+)-.*", e("a").attr("href")).group(1))
            if id not in topicids:
                f = e.parents().eq(-2)
                locked = u"verrouillé" in f("td img").eq(0).attr("alt")
                views = int(f("td").eq(5).text())
                type = e("strong").text()
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
