# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger("lalf")

import re
from pyquery import PyQuery
from lalf.users import Users
from lalf.ocruserspage import OcrUsersPage
from lalf import session

class OcrUsers(Users):
    def _export_(self):
        logger.info('Récupération des membres')
    
        r = session.get("/memberlist")
        result = re.search('function do_pagination_start\(\)[^\}]*start = \(start > \d+\) \? (\d+) : start;[^\}]*start = \(start - 1\) \* (\d+);[^\}]*\}', r.text)
    
        try:
            pages = int(result.group(1))
            usersperpage = int(result.group(2))
        except:
            pages = 1
            usersperpage = 0
        
        for page in range(0,pages):
            self.children.append(OcrUsersPage(self.parent, page*usersperpage))
        
    def get_users(self):
        for p in self.children:
            for c in p.children:
                yield c
