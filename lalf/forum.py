import logging
logger = logging.getLogger("lalf")

import os
import unicodedata
import re
import imghdr
from pyquery import PyQuery

from lalf.node import Node
from lalf.forumpage import ForumPage
from lalf import phpbb
from lalf import sql
from lalf import session

def clean(s):
    """Removes all accents from the string"""
    if isinstance(s,str):
        s = unicode(s,"utf8","replace")
        s = unicodedata.normalize('NFD',s)
        return s.encode('ascii','ignore')

class Forum(Node):

    """
    Attributes to save
    """
    STATE_KEEP = ["id", "newid", "type", "parentid", "title", "description", "icon", "left_id", "right_id"]
    
    def __init__(self, parent, id, newid, left_id, type, parentid, title):
        """
        id -- id in the old forum
        newid -- id in the new forum
        type -- c if the forum is a category, else f
        parentid -- parent forum (0 if it is a categoryà
        title -- title of the forum
        description -- description of the forum
        icon -- url of the forum icon
        """
        Node.__init__(self, parent)
        self.id = id
        self.newid = newid
        self.left_id = left_id
        self.right_id = 0
        self.type = type
        self.parentid = parentid
        self.title = title
        self.description = ""
        self.icon = ""

    def _export_(self):
        # Télécharge la page de configuration du forum
        params = {
            "part" : "general",
            "sub" : "general",
            "mode" : "edit",
            "fid" : self.type+str(self.id)
        }
        r = session.get_admin("/admin/index.forum", params=params)
        d = PyQuery(r.text)

        # Description
        try:
            self.description = d("textarea").text()
        except:
            pass

        # Icone
        for i in d("input"):
            if i.get("name", "") == "image":
                self.icon = i.text

        if self.icon:
            logger.debug("Téléchargement de l'icône du forum {}".format(self.newid))
            r = session.session.get(self.icon)
            ext = imghdr.what(r.content)
            
            if ext is None:
                logger.warning("Le format de l'icône du forum {}, utilisation de l'extension par défaut".format(self.newid))
                ext = os.path.splitext(self.icon)[1]
            else:
                ext = "."+ext

            if not os.path.isdir("images/forums"):
                os.makedirs("images/forums")
            self.icon = "images/forums/{id}{ext}".format(id=self.newid, ext=ext)
            with open(self.icon, "wb") as f:
                f.write(r.content)
        else:
            self.icon = ""
        
        # Contenu
        r = session.get("/{type}{id}-a".format(type=self.type, id=self.id))
        result = re.search('function do_pagination_start\(\)[^\}]*start = \(start > \d+\) \? (\d+) : start;[^\}]*start = \(start - 1\) \* (\d+);[^\}]*\}', r.text)

        try:
            pages = int(result.group(1))
            topicsperpages = int(result.group(2))
        except:
            pages = 1
            topicsperpages = 0

        for page in range(0, pages):
            self.children.append(ForumPage(self, self.id, self.newid, self.type, page*topicsperpages))

    def get_topics(self):
        for p in self.children:
            for c in p.children:
                yield c

    def _dump_(self, file):
        if self.type == "f":
            type = 1
        else:
            type = 0
            
        sql.insert(file, "forums", {
            "forum_id" : self.newid,
            "parent_id" : self.parentid,
            "left_id" : self.left_id,
            "right_id" : self.right_id,
            "forum_name" : self.title,
            "forum_desc" : self.description,
            "forum_type" : type,
            "forum_image" : self.icon
            })
        
        for acl in phpbb.default_forum_acl(self.newid):
            sql.insert(file, "acl_groups", acl)
