import logging
logger = logging.getLogger("lalf")

import re
from pyquery import PyQuery
import session
from node import Node
from smileyspage import SmileysPage

class Smileys(Node):
    def _export_(self):
        logger.info('Récupération des émoticones')

        params = {
            "part" : "themes",
            "sub" : "avatars",
            "mode" : "smilies"
        }
        r = session.get_admin("/admin/index.forum", params=params)    
        result = re.search('function do_pagination_start\(\)[^\}]*start = \(start > \d+\) \? (\d+) : start;[^\}]*start = \(start - 1\) \* (\d+);[^\}]*\}', r.text)

        try:
            pages = int(result.group(1))
            smileysperpage = int(result.group(2))
        except:
            pages = 1
            smileysperpage = 0

        for page in range(0,pages):
            self.children.append(SmileysPage(self.parent, page*smileysperpage))
