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

import re
from pyquery import PyQuery

from lalf.node import Node
from lalf.posts import TopicPage
from lalf.util import pages

TOPIC_TYPES = {
    'Post-it:': 1,
    'Annonce:': 2,
    'Annonce globale:': 3
}

@Node.expose(self="topic")
class Topic(Node):
    """
    Node representing a topic

    Attrs:
        id (int): The id of the topic
        type (int): The type of the topic
            0 if it is a normal topic
            1 if it is a note
            2 if it is an announcement
            3 if it is a global announcement
        title (str): The title of the topic
        locked (int): 1 if the topic is locked, else 0
        views (int): The number of views of the topic
    """
    # Attributes to save
    STATE_KEEP = ["type", "title", "locked", "views"]

    def __init__(self, topic_id, topic_type, title, locked, views):
        Node.__init__(self, topic_id)
        self.type = topic_type
        self.title = title
        self.locked = locked
        self.views = views

    def get_posts(self):
        """
        Iterator on the posts of the topic
        """
        for page in self.get_children():
            for post in page.get_children():
                yield post

    def _export_(self):
        self.logger.info('Récupération du sujet %d', self.id)

        self.root.current_topics += 1
        self.ui.update()

        response = self.session.get("/t{}-a".format(self.id))
        for page in pages(response.text):
            self.add_child(TopicPage(page))

    def _dump_(self, sqlfile):
        posts = list(self.get_posts())
        first_post = posts[0]
        last_post = posts[-1]

        replies = len(posts) - 1

        sqlfile.insert("topics", {
            "topic_id" : self.id,
            "forum_id" : self.forum.newid,
            "topic_title" : self.title,
            "topic_poster" : first_post.poster.newid,
            "topic_time" : first_post.time,
            "topic_views" : self.views,
            "topic_replies" : replies,
            "topic_replies_real" : replies,
            "topic_status" : self.locked,
            "topic_type" : self.type,
            "topic_first_post_id" : first_post.id,
            "topic_first_poster_name" : first_post.poster.name,
            "topic_first_poster_colour" : first_post.poster.colour,
            "topic_last_post_id" : last_post.id,
            "topic_last_poster_id" : last_post.poster.newid,
            "topic_last_poster_name" : last_post.poster.name,
            "topic_last_poster_colour" : last_post.poster.colour,
            "topic_last_post_subject" : last_post.title,
            "topic_last_post_time" : last_post.time
        })

        for user_id in set(post.poster.newid for post in self.get_posts()):
            sqlfile.insert("topics_posted", {
                "user_id" : user_id,
                "topic_id" : self.id,
                "topic_posted" : 1
            })

class ForumPage(Node):
    """
    Node representing a page of a forum

    Attrs:
        page (int): The index of the first topic of the page
    """
    def __init__(self, page_id):
        Node.__init__(self, page_id)

    def _export_(self):
        self.logger.debug('Récupération du forum %s (page %d)', self.forum.id, self.id)

        # Download the page
        response = self.session.get("/{}p{}-a".format(self.forum.id, self.id))
        document = PyQuery(response.text)

        # Get the topics
        for element in document.find('div.topictitle'):
            e = PyQuery(element)

            topic_id = int(re.search(r"/t(\d+)-.*", e("a").attr("href")).group(1))
            if topic_id not in self.announcements:
                f = e.parents().eq(-2)
                locked = 1 if ("verrouillé" in f("td img").eq(0).attr("alt")) else 0
                views = int(f("td").eq(5).text())
                topic_type = TOPIC_TYPES.get(e("strong").text(), 0)
                title = e("a").text()

                self.add_child(Topic(topic_id, topic_type, title, locked, views))
                if topic_type >= 2:
                    # The topic is an announcement, save its id to avoid exporting it again
                    self.announcements.append(topic_id)
