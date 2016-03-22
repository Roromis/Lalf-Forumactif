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

# TODO : do not use globals
topicids = []

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
        topic_id (int): The id of the topic
        topic_type (int): The type of the topic
            0 if it is a normal topic
            1 if it is a note
            2 if it is an announcement
            3 if it is a global announcement
        title (str): The title of the topic
        locked (int): 1 if the topic is locked, else 0
        views (int): The number of views of the topic
    """
    # Attributes to save
    STATE_KEEP = ["topic_id", "topic_type", "title", "locked", "views"]

    def __init__(self, topic_id, topic_type, title, locked, views):
        Node.__init__(self)
        self.topic_id = topic_id
        self.topic_type = topic_type
        self.title = title
        self.locked = locked
        self.views = views

    def _export_(self):
        self.logger.debug('Récupération du sujet %d', self.topic_id)

        self.root.current_topics += 1
        self.ui.update()

        response = self.session.get("/t{}-a".format(self.topic_id))
        for page in pages(response.text):
            self.add_child(TopicPage(page))

    def get_posts(self):
        """
        Iterator on the posts of the topic
        """
        for page in self.children:
            for post in page.children:
                yield post

    def _dump_(self, sqlfile):
        first_post = self.children[0].children[0]
        last_post = self.children[-1].children[-1]
        replies = sum(1 for _ in self.get_posts()) - 1

        sqlfile.insert("topics", {
            "topic_id" : self.topic_id,
            "forum_id" : self.forum.newid,
            "topic_title" : self.title,
            "topic_poster" : self.root.users.get_newid(first_post.author),
            "topic_time" : first_post.time,
            "topic_views" : self.views,
            "topic_replies" : replies,
            "topic_replies_real" : replies,
            "topic_status" : self.locked,
            "topic_type" : self.topic_type,
            "topic_first_post_id" : first_post.post_id,
            "topic_first_poster_name" : first_post.author,
            #"topic_first_post_colour" (TODO)
            "topic_last_post_id" : last_post.post_id,
            "topic_last_poster_id" : self.root.users.get_newid(last_post.author),
            "topic_last_poster_name" : last_post.author,
            #"topic_last_poster_colour" (TODO)
            "topic_last_post_subject" : last_post.title,
            "topic_last_post_time" : last_post.time
        })

        for username in set(post.author for post in self.get_posts()):
            sqlfile.insert("topics_posted", {
                "user_id" : self.root.users.get_newid(username),
                "topic_id" : self.topic_id,
                "topic_posted" : 1
            })

class ForumPage(Node):
    """
    Node representing a page of a forum

    Attrs:
        page (int): The index of the first topic of the page
    """
    # Attributes to save
    STATE_KEEP = ["page"]

    def __init__(self, page):
        Node.__init__(self)
        self.page = page

    def _export_(self):
        self.logger.debug('Récupération du forum %s (page %d)', self.forum.oldid, self.page)

        # Download the page
        response = self.session.get("/{}p{}-a".format(self.forum.oldid, self.page))
        document = PyQuery(response.text)

        # Get the topics
        for element in document.find('div.topictitle'):
            e = PyQuery(element)

            topic_id = int(re.search(r"/t(\d+)-.*", e("a").attr("href")).group(1))
            if topic_id not in topicids:
                f = e.parents().eq(-2)
                locked = 1 if ("verrouillé" in f("td img").eq(0).attr("alt")) else 0
                views = int(f("td").eq(5).text())
                topic_type = TOPIC_TYPES.get(e("strong").text(), 0)
                title = e("a").text()

                self.add_child(Topic(topic_id, topic_type, title, locked, views))
                topicids.append(topic_id)
            else:
                # Topic has already been exported (it's a global announcement)
                self.logger.warning('Le sujet %d existe déjà.', topic_id)

    def __setstate__(self, state):
        Node.__setstate__(self, state)
        for topic in self.children:
            topicids.append(topic.topic_id)
