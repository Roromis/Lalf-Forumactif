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

from pyquery import PyQuery

from lalf.node import Node
from lalf.topics import ForumPage
from lalf.util import pages
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
class Forum(Node):
    """
    Node representing a forum

    Attrs:
        oldid (str): The id in the old forum
        newid (int): The id in the new forum
        left_id (int): Left id of the forum in the nested set model (see
                       https://en.wikipedia.org/wiki/Nested_set_model)
        right_id (int): Right id of the forum in the nested set model
        parent_id (int): The id of the parent forum (0 if it is a category)
        title (str): The title of the forum

        description (str): The description of the forum
        icon (str): The url of the forum icon
    """
    # Attributes to save
    STATE_KEEP = ["oldid", "newid", "parent_id", "title", "description", "icon", "left_id",
                  "right_id", "status", "num_topics", "num_posts"]

    def __init__(self, oldid, newid, left_id, parent_id, title):
        Node.__init__(self)
        self.oldid = oldid
        self.newid = newid
        self.left_id = left_id
        self.right_id = 0
        self.parent_id = parent_id
        self.title = title

        self.description = ""
        self.icon = ""
        self.status = 0
        self.num_topics = None
        self.num_posts = None

    def _export_(self):
        self.logger.info('Récupération du forum %s', self.oldid)

        response = self.session.get("/{}-a".format(self.oldid))

        # Get subforums descriptions, number of topics, ...
        self.forums_node.get_subforums_infos(response.text)

        for page in pages(response.text):
            self.add_child(ForumPage(page))

    def get_topics(self):
        """
        Returns the topics of this forum
        """
        for page in self.children:
            for topic in page.children:
                yield topic

    def _dump_(self, sqlfile):
        if self.oldid[0] == "f":
            forum_type = 1
        else:
            forum_type = 0

        parser = htmltobbcode.Parser(self.root)
        parser.feed(self.description)
        description = parser.get_post()

        # TODO : add statistics
        sqlfile.insert("forums", {
            "forum_id" : self.newid,
            "parent_id" : self.parent_id,
            "left_id" : self.left_id,
            "right_id" : self.right_id,
            #"forum_parents" : (TODO)
            "forum_name" : self.title,
            "forum_desc" : description.text,
            "forum_desc_bitfield" : description.bitfield,
            "forum_desc_uid" : description.uid,
            "forum_type" : forum_type,
            "forum_image" : self.icon,
            "forum_status" : self.status,
            #"forum_posts" : (TODO)
            #"forum_topics" : (TODO)
            #"forum_topics_real" : (TODO)
            #"forum_last_post_id" : (TODO)
            #"forum_last_poster_id" : (TODO)
            #"forum_last_post_time" : (TODO)
            #"forum_last_poster_name" : (TODO)
            #"forum_last_poster_colour" : (TODO)
        })

        for acl in default_forum_acl(self.newid):
            sqlfile.insert("acl_groups", acl)

@Node.expose(self="forums_node")
class Forums(Node):
    """
    Node used to export the forums
    """
    def _export_(self):
        self.logger.info('Récupération des forums')

        # Get the first forum
        # TODO : what if it does not exist?
        response = self.session.get("/a-f1/")
        document = PyQuery(response.text)

        # Get the forums hierarchy by parsing the content of the jumpbox

        # List containing at the index i the last forum met at depth i
        depths = []

        # The id of the next forum (ids have to be changed because
        # categories and forums may have the same id in forumactif,
        # but not in phpbb)
        newid = 1

        # Variable used to determine the left and right ids of the
        # forums in the nested set model which is used internally by
        # phpbb (see https://en.wikipedia.org/wiki/Nested_set_model)
        nested_id = 1

        for element in document.find("select option"):
            forum_id = element.get("value", "-1")
            if forum_id != "-1":
                match = re.search('(((\\||\xa0)(\xa0\xa0\xa0))*)\\|--([^<]+)', element.text)
                if match is None:
                    continue

                title = match.group(5)
                depth = len(re.findall('(\\||\xa0)\xa0\xa0\xa0', element.text))

                if depth <= 0:
                    parent_id = 0
                else:
                    parent_id = depths[depth-1].newid

                for _ in range(depth, len(depths)):
                    forum = depths.pop()
                    forum.right_id = nested_id
                    nested_id += 1

                forum = Forum(forum_id, newid, nested_id, parent_id, title)
                self.forums[forum_id] = forum
                depths.append(forum)
                self.add_child(forum)
                newid += 1
                nested_id += 1

        for _ in range(0, len(depths)):
            forum = depths.pop()
            forum.right_id = nested_id
            nested_id += 1

        # Get subforums descriptions, number of topics, ...
        response = self.session.get("/forum")
        self.get_subforums_infos(response.text)

    def get_subforums_infos(self, html):
        """
        Get informations (description, number of topics and posts, ...) about
        the forums listed on a page
        """
        document = PyQuery(html)

        idpattern = re.compile(r"/([fc]\d+)-.*")

        for element in document("a.forumlink"):
            e = PyQuery(element)

            match = idpattern.fullmatch(e.attr("href"))
            if not match:
                continue

            oldid = match.group(1)

            row = e.closest("tr")

            # Get forum status
            alt = row("td:nth-of-type(1) img").eq(0).attr("alt")
            self.forums[oldid].status = 1 if "verrouillé" in alt else 0

            # Get subforum description
            self.forums[oldid].description = row("td:nth-of-type(2) span").eq(1).html() or ""

            # TODO : Get subforum icon

            # Get subforum numbers of topics and posts
            self.forums[oldid].num_topics = int(row("td").eq(2).text())
            self.forums[oldid].num_posts = int(row("td").eq(3).text())
