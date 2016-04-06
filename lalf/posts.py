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

from lxml import html, etree

from lalf.node import Node, Page, ParsingError
from lalf.util import parse_date, clean_url
from lalf.users import AnonymousUser, NoUser
from lalf import htmltobbcode

class NoPost(object):
    """
    Node used to represent an unexisting post in the database (for
    example if there is no posts in a forum)
    """
    def __init__(self):
        self.id = 0
        self.text = ""
        self.title = ""
        self.time = 0
        self.poster = NoUser()

class Post(Node):
    """
    Node representing a post

    Attrs:
        id (int): The id of the post
        text (str): The content of the post in html
        title (str): The title of the post
        time (int): Time of the post (unix timestamp)
        poster (User): User who submitted the post
    """
    def __init__(self, post_id, text, title, post_time, poster):
        Node.__init__(self, post_id)
        self.text = text
        self.title = title
        self.time = post_time
        self.poster = poster

    def _dump_(self, sqlfile):
        self.logger.debug("Exportation du message %d (sujet %d)", self.id, self.topic.id)
        parser = htmltobbcode.Parser(self.root)
        parser.feed(self.text)
        post = parser.get_post()

        sqlfile.insert("posts", {
            "post_id" : self.id,
            "topic_id" : self.topic.id,
            "forum_id" : self.forum.newid,
            "poster_id" : self.poster.newid,
            "post_time" : self.time,
            "poster_ip" : "::1",
            "post_subject" : self.title,
            "post_text" : post.text,
            "bbcode_bitfield" : post.bitfield,
            "bbcode_uid" : post.uid})

class TopicPage(Page):
    """
    Node representing a page of a topic
    """
    def __init__(self, page_id):
        Page.__init__(self, page_id)

    def _export_(self):
        self.logger.debug('Récupération des messages du sujet %d (page %d)',
                          self.topic.id, self.id)

        response = self.session.get("/t{}p{}-a".format(self.topic.id, self.id))
        document = html.fromstring(response.content)

        idpattern = re.compile(r"p(\d+)")
        userpattern = re.compile(r"/u(\d+)")

        for post in document.cssselect('tr.post'):
            match = idpattern.fullmatch(post.get("id"))
            post_id = int(match.group(1))
            self.logger.info('Récupération du message %d (sujet %d)',
                             post_id, self.topic.id)

            cols = post.xpath("td")

            poster = AnonymousUser()
            try:
                link = cols[0].cssselect("span.name strong a")[0]
            except IndexError:
                pass
            else:
                match = userpattern.fullmatch(clean_url(link.get("href")))
                if match:
                    poster = self.users.get(int(match.group(1)))

            try:
                text = etree.tostring(cols[1].cssselect("div.postbody div")[0], encoding='unicode', with_tail=False)
                details = cols[1].cssselect("span.postdetails")[0].xpath("child::node()")

                # Get the title of the post
                title = details[1][7:].rstrip()

                # Get the date and time of the post
                timestamp = parse_date(details[3])
            except (IndexError, ValueError):
                raise ParsingError(document)

            if not text:
                self.logger.warning('Le message  %d (sujet %d) semble être vide',
                                    post_id, self.topic.id)
                text = ""

            self.add_child(Post(post_id, text, title, timestamp, poster))
            self.post_count += 1
