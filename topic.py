import logging
logger = logging.getLogger("lalf")
from pyquery import PyQuery
import re

import session
from node import Node
from topicpage import TopicPage
import ui
import sql

number = 0

class Topic(Node):

    """
    Attributes to save
    """
    STATE_KEEP = ["id", "type", "forum", "title", "locked", "views", "posted"]
    
    def __init__(self, parent, id, type, forum, title, locked, views):
        Node.__init__(self, parent)
        self.id = id
        self.type = type
        self.forum = forum
        self.title = title
        self.locked = locked
        self.views = views
        self.posted = {}

    def _export_(self):
        # Incrémente le nombre de sujets
        global number
        number += 1
        ui.update()
        
        logger.debug('Récupération : messages du topic %d', self.id)

        r = session.get("/t{id}-a".format(id=self.id))
        result = re.search('function do_pagination_start\(\)[^\}]*start = \(start > \d+\) \? (\d+) : start;[^\}]*start = \(start - 1\) \* (\d+);[^\}]*\}', r.text)

        try:
            pages = int(result.group(1))
            topicsperpage = int(result.group(2))
        except:
            pages = 1
            topicsperpage = 0
        
        for page in range(0,pages):
            self.children.append(TopicPage(self, self.id, page*topicsperpage))

    def __setstate__(self, dict):
        global number
        Node.__setstate__(self, dict)
        number += 1

    def get_posts(self):
        for p in self.children:
            for c in p.children:
                yield c

    def _dump_(self, file):
        users = self.parent.parent.children[0]
        posts = list(self.get_posts())

        posts[0]
        sql.insert(file, "topics", {
            "topic_id" : self.id,
            "topic_type" : self.type,
            "forum_id" : self.forum,
            "topic_first_post_id" : posts[0].id,
            "topic_first_poster_name" : posts[0].author,
            "topic_last_post_id" : posts[-1].id,
            "topic_last_poster_id" : users.get_newid(posts[-1].author),
            "topic_last_poster_name" : posts[-1].author,
            "topic_last_post_subject" : posts[-1].title,
            "topic_last_post_time" : posts[-1].timestamp,
            "topic_poster" : users.get_newid(posts[0].author),
            "topic_time" : posts[0].timestamp,
            "topic_title" : self.title,
            "topic_replies" : len(posts)-1,
            "topic_replies_real" : len(posts)-1,
            "topic_views" : self.views,
            "topic_status" : self.locked})

        posted = {}
        for u in users.get_users():
            posted[u.name] = 0
        
        for p in self.get_posts():
            posted[p.author] = 1

        for user, posted in posted.items():
            sql.insert(file, "topics_posted", {
                "user_id" : users.get_newid(user),
                "topic_id" : self.id,
                "topic_posted" : posted
            })