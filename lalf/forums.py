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
Module handling the exportation of the forums
"""

import re

from lxml import html, etree

from lalf.node import Node, PaginatedNode, ParsingError
from lalf.topics import ForumPage, Topic, TOPIC_TYPES
from lalf.posts import NoPost
from lalf.util import pages, Counter, clean_url
from lalf import htmltobbcode

def default_forum_acl(forumid):
    for gid, perm in ((1, 17), # guests: readonly
                      (2, 21), # registered: standard w/ polls
                      (3, 21), # registered+COPPA: standard w/ polls
                      (4, 14), # global mods: full access
                      (4, 11), # global mods: standard moderation
                      (5, 14), # admins: full access
                      (5, 10), # admins: full moderation
                      (6, 19), # bots: bot access
                     ):
        yield {
            "group_id" : gid,
            "forum_id" : forumid,
            "auth_option_id" : 0,
            "auth_role_id" : perm,
            "auth_setting" : 0
        }

@Node.expose(self="forum")
class Forum(PaginatedNode):
    """
    Node representing a forum

    Attrs:
        id (str): The id in the old forum
        newid (int): The id in the new forum
        left_id (int): Left id of the forum in the nested set model (see
                       https://en.wikipedia.org/wiki/Nested_set_model)
        right_id (int): Right id of the forum in the nested set model
        parent (Forum): The parent forum (or None)
        title (str): The title of the forum

        description (str): The description of the forum
        icon (str): The url of the forum icon
    """
    # Attributes to save
    STATE_KEEP = ["newid", "parent", "title", "description", "icon", "left_id",
                  "right_id", "status", "num_topics", "num_posts", "type"]

    def __init__(self, forum_id, parent, title, num_topics, num_posts):
        PaginatedNode.__init__(self, forum_id)
        self.parent = parent
        self.title = title.replace('"', '&quot;')

        if self.id[0] == "f":
            self.type = 1
        else:
            self.type = 0

        self.num_topics = num_topics
        self.num_posts = num_posts

        self.newid = None
        self.left_id = None
        self.right_id = None
        self.description = ""
        self.icon = ""
        self.status = 0

    def get_topics(self):
        """
        Returns the topics of this forum
        """
        return self.get_children()

    def get_posts(self):
        """
        Returns the posts of this forum
        """
        for topic in self.get_topics():
            for post in topic.get_posts():
                yield post

    def _export_(self):
        self.logger.info('Récupération du forum %s', self.id)

        self.newid = self.forums.count.newid()

        response = self.session.get("/{}-a".format(self.id))

        # Get subforums descriptions, number of topics, ...
        self.forums.get_subforums_infos(response.content)

        for page in pages(response.content):
            self.add_page(ForumPage(page))

    def _dump_(self, sqlfile):
        # Get forum_parents field
        entry = "i:{};a:2:{{i:0;s:{}:\"{}\";i:1;i:{};}}"
        entries = []
        parent = self.parent
        while parent.newid > 0:
            title = parent.title
            entries.append(entry.format(
                parent.newid, len(parent.title), title, parent.type))
            parent = parent.parent

        parents = "a:{}:{{{}}}".format(len(entries), "".join(reversed(entries)))

        parser = htmltobbcode.Parser(self.root)
        parser.feed(self.description)
        description = parser.get_post()

        num_posts = sum(1 for post in self.get_posts())
        num_topics = sum(1 for post in self.get_topics())

        if num_posts == 0:
            last_post = NoPost()
        else:
            last_post = max(self.get_posts(), key=lambda post: post.time)

        sqlfile.insert("forums", {
            "forum_id" : self.newid,
            "parent_id" : self.parent.newid,
            "left_id" : self.left_id,
            "right_id" : self.right_id,
            "forum_parents" : parents,
            "forum_name" : self.title,
            "forum_desc" : description.text,
            "forum_desc_bitfield" : description.bitfield,
            "forum_desc_uid" : description.uid,
            "forum_type" : self.type,
            "forum_image" : self.icon,
            "forum_status" : self.status,
            "forum_posts" : num_posts,
            "forum_topics" : num_topics,
            "forum_topics_real" : num_topics,
            "forum_last_post_id" : last_post.id,
            "forum_last_poster_id" : last_post.poster.newid,
            "forum_last_post_subject" : last_post.title,
            "forum_last_post_time" : last_post.time,
            "forum_last_poster_name" : last_post.poster.name,
            "forum_last_poster_colour" : last_post.poster.colour
        })

        for acl in default_forum_acl(self.newid):
            sqlfile.insert("acl_groups", acl)

class ForumRoot(Node):
    STATE_KEEP = ["id", "newid", "left_id", "right_id"]
    def __init__(self):
        Node.__init__(self, 0)
        self.newid = 0
        self.left_id = 0
        self.right_id = 1

@Node.expose("forum")
class Announcements(Node):
    """
    Node used to export the global announcements

    Attrs:
        forum_id (int): The index of the forum used to export the global
            announcements (any existing forum will do).
    """
    STATE_KEEP = ["forum", "forum_id"]

    def __init__(self, forum_id):
        Node.__init__(self, "announcements")
        self.forum = ForumRoot()
        self.forum_id = forum_id

    def get_topics(self):
        """
        Returns the topics of this forum
        """
        return self.get_children()

    def get_posts(self):
        """
        Returns the posts of this forum
        """
        for topic in self.get_topics():
            for post in topic.get_posts():
                yield post

    def _export_(self):
        # TODO : code duplication with topics.py...
        self.logger.info('Récupération des annonces globales')

        # Download the page
        response = self.session.get("/{}-a".format(self.forum_id))
        document = html.fromstring(response.content)

        idpattern = re.compile(r"/t(\d+)-.*")

        # Get the topics
        for div in document.cssselect('div.topictitle'):
            try:
                row = div.xpath("ancestor::tr")[-1]
                cols = row.cssselect("td")
                link = div.cssselect("a")[0]
                status = cols[0].cssselect("img")[0].get("alt")
                views = int(cols[5].text_content())
            except (IndexError, ValueError):
                raise ParsingError(document)

            try:
                topic_type = div.cssselect("strong")[0].text_content()
                topic_type = TOPIC_TYPES.get(topic_type, 0)
            except IndexError:
                topic_type = 0

            if topic_type != 3:
                continue

            match = idpattern.fullmatch(clean_url(link.get("href")))
            topic_id = int(match.group(1))

            locked = 1 if ("verrouillé" in status) else 0
            title = link.text_content()

            self.add_child(Topic(topic_id, topic_type, title, locked, views))

class Forums(Node):
    """
    Node used to export the forums
    """

    STATE_KEEP = ["count", "announcements"]

    def __init__(self):
        Node.__init__(self, "forums")
        self.count = Counter(1)
        self.announcements = None

    def __setstate__(self, state):
        Node.__setstate__(self, state)

    def remove_children(self):
        Node.remove_children(self)
        self.count.reset()

    def _export_children(self, element, parent=None):
        """
        Export the forums shown in an html element
        """
        idpattern = re.compile("([cf]\d+)_open")

        for div in element.xpath("div"):
            match = idpattern.fullmatch(div.get("id"))
            if match:
                forum_id = match.group(1)

                if self.announcements is None and forum_id[0] == "f":
                    self.announcements = Announcements(forum_id)
                    self.add_child(self.announcements)

                row = div.xpath("table[1]//tr[1]")[0]
                cols = row.cssselect("td")

                # Get title, number of topics and number of posts
                title = cols[1].text_content().strip()

                num_topics = int(cols[2].text_content())
                num_posts = int(cols[3].text_content())

                # Add forum to children
                forum = Forum(forum_id, parent, title, num_topics, num_posts)
                self.add_child(forum)

                # Export children and set left and right ids
                forum.left_id = parent.right_id
                forum.right_id = forum.left_id + 1
                self._export_children(div, forum)
                parent.right_id = forum.right_id + 1

    def _export_(self):
        self.logger.info('Récupération des forums')

        # Get the page of the administration panel listing the forums
        params = {
            "part" : "general",
            "sub" : "general",
            "mode" : "forum"
        }
        response = self.session.get_admin("/admin/index.forum", params=params)
        document = html.fromstring(response.content)

        root = document.cssselect("#root_open")[0]
        self._export_children(root, ForumRoot())

        # Get subforums descriptions
        response = self.session.get("/forum")
        self.get_subforums_infos(response.content)

    def get_subforums_infos(self, content):
        """
        Get informations (description, number of topics and posts, ...) about
        the forums listed on a page
        """
        document = html.fromstring(content)

        idpattern = re.compile(r"/([fc]\d+)-.*")

        for link in document.cssselect("a.forumlink"):
            match = idpattern.fullmatch(clean_url(link.get("href")))
            if not match:
                continue

            forum_id = match.group(1)
            forum = self.get(forum_id)

            row = link.xpath("ancestor::tr")[-1]
            cols = row.cssselect("td")

            # Get forum status
            alt = cols[0].cssselect("img")[0].get("alt")
            forum.status = 1 if "verrouillé" in alt else 0

            # Get subforum description
            forum.description = etree.tostring(cols[1].xpath("span")[0], encoding='unicode', with_tail=False)
