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

"""
Module handling the exportation of the posts
"""

import re

from pyquery import PyQuery

from lalf.node import Node
from lalf.util import parse_date
from lalf.users import AnonymousUser, NoUser
from lalf import htmltobbcode

class NoPost(object):
    def __init__(self):
        self.post_id = 0
        self.text = ""
        self.title = ""
        self.time = 0
        self.poster = NoUser()

class Post(Node):
    """
    Node representing a post

    Attrs:
        post_id (int): The id of the post
        text (str): The content of the post in html
        title (str): The title of the post
        time (int): Time of the post (unix timestamp)
        poster (User): User who submitted the post
    """
    STATE_KEEP = ["post_id", "text", "title", "time", "poster"]

    def __init__(self, post_id, text, title, post_time, poster):
        Node.__init__(self)
        self.post_id = post_id
        self.text = text
        self.title = title
        self.time = post_time
        self.poster = poster

    def _export_(self):
        self.root.current_posts += 1
        self.ui.update()

    def _dump_(self, sqlfile):
        self.logger.debug("Exportation du message %d (sujet %d)", self.post_id, self.topic.topic_id)
        parser = htmltobbcode.Parser(self.root)
        parser.feed(self.text)
        post = parser.get_post()

        sqlfile.insert("posts", {
            "post_id" : self.post_id,
            "topic_id" : self.topic.topic_id,
            "forum_id" : self.forum.newid,
            "poster_id" : self.poster.newid,
            "post_time" : self.time,
            "poster_ip" : "::1",
            "post_subject" : self.title,
            "post_text" : post.text,
            "bbcode_bitfield" : post.bitfield,
            "bbcode_uid" : post.uid})

class TopicPage(Node):
    """
    Node representing a page of a topic
    """
    # Attributes to save
    STATE_KEEP = ["page"]

    def __init__(self, page):
        Node.__init__(self)
        self.page = page

    def _export_(self):
        self.logger.debug('Récupération des messages du sujet %d (page %d)',
                          self.topic.topic_id, self.page)

        response = self.session.get("/t{}p{}-a".format(self.topic.topic_id, self.page))
        document = PyQuery(response.text)

        pattern = re.compile(r"/u(\d+)")

        for element in document.find('tr.post'):
            e = PyQuery(element)

            post_id = int(e("td span.name a").attr("name"))

            self.logger.info('Récupération du message %d (sujet %d)',
                             post_id, self.topic.topic_id)

            match = pattern.fullmatch(e("td span.name strong a").eq(0).attr("href") or "")
            if match:
                poster = self.users[int(match.group(1))]
            else:
                poster = AnonymousUser()

            post = e("td div.postbody div").eq(0).html()
            if not post:
                self.logger.warning('Le message  %d (sujet %d) semble être vide',
                                    post_id, self.topic.topic_id)
                post = ""

            # Get title
            title = e("table td span.postdetails").contents()[1]
            # Remove "Sujet :" before the title and spaces at the end
            title = title[7:].rstrip()

            # Get the date and time of the post
            timestamp = parse_date(e("table td span.postdetails").contents()[3])

            self.add_child(Post(post_id, post, title, timestamp, poster))
