import logging
logger = logging.getLogger("lalf")

import re
from pyquery import PyQuery
import session
from node import Node
from forum import Forum
import sql

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
                logger.debug('Récupération: forum %s', id)
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

    def _dump_(self, file):
        # Clean tables
        sql.truncate(file, "forums")
        sql.truncate(file, "acl_groups")

        sql.truncate(file, "topics")
        sql.truncate(file, "topics_posted")
        
        sql.truncate(file, "posts")
