# -*- coding: utf-8 -*-
#
# This file is part of Lalf.
#
# Lalf is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lalf is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lalf.  If not, see <http://www.gnu.org/licenses/>.

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
from lalf import htmltobbcode
from lalf import session

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

        self.root.current_posts += 1
        ui.update()

    def _export_(self):
        return

    def _dump_(self, file):
        users = self.parent.parent.parent.users
        smileys = self.parent.parent.parent.get_smileys()

        uid = phpbb.uid()
        parser = htmltobbcode.Parser(smileys, uid)
        parser.feed(self.post)
        post = parser.output
        bitfield = parser.get_bitfield()
        checksum = parser.get_checksum()

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
