import logging
logger = logging.getLogger("lalf")

import re
import random
import hashlib
from pyquery import PyQuery

from lalf.node import Node
from lalf import ui
from lalf import sql
from lalf import phpbb
from lalf import session
from lalf import counters

class Post(Node):
    STATE_KEEP = ["id", "post", "title", "topic", "timestamp", "author"]

    def __init__(self, parent, id, post, title, topic, timestamp, author):
        Node.__init__(self, parent)
        self.id = id
        self.post = post
        self.title = title
        self.topic = topic
        self.timestamp = timestamp
        self.author = author
        self.exported = True
        self.children_exported = True

        counters.postnumber += 1
        ui.update()

    def _export_(self):
        return
    
    def __setstate__(self, dict):
        Node.__setstate__(self, dict)
        counters.postnumber += 1

    def _dump_(self, file):
        users = self.parent.parent.parent.children[0]

        post, uid, bitfield, checksum = phpbb.format_post(self.post)
        sql.insert(file, "posts", {
            "post_id" : self.id,
            "topic_id" : self.parent.id,
            "forum_id" : self.parent.parent.newid,
            "poster_id" : users.get_newid(self.author),
            "post_time" : self.timestamp,
            "poster_ip" : "127.0.0.1",
            "post_username" : self.author,
            "post_subject" : self.title,
            "post_text" : post,
            "bbcode_uid" : uid,
            "post_checksum" : checksum,
            "bbcode_bitfield" : bitfield})
