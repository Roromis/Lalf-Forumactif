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
Module containing the BB class (the root of the forum)
"""

import logging
import pickle
import time

from pyquery import PyQuery

from lalf.node import Node
from lalf.forums import Forums
from lalf.users import Users
from lalf.ocrusers import OcrUsers
from lalf.smilies import Smilies
from lalf import phpbb
from lalf.session import Session
from lalf.linkrewriter import LinkRewriter

@Node.expose("config", "session", "ui", "smilies", "user_names", "user_ids", "forums", self="root")
class BB(Node):
    """
    The BB node is the root of the tree representing the forum.

    Attrs:
        total_posts (int) : The total number of posts to be exported
        total_topics (int) : The total number of topics to be exported
        total_users (int) : The total number of users to be exported

        current_posts (int) : The number of posts that have been exported
        current_topics (int) : The number of topics that have been exported
        current_users (int) : The number of users that have been exported

        dump_time (int): The time at the beginning of the dump
    """

    # Attributes to save
    STATE_KEEP = ["total_posts", "total_topics", "total_users",
                  "current_posts", "current_topics", "current_users",
                  "smilies", "user_names", "user_ids", "forums"]

    def __init__(self, config, ui=None):
        Node.__init__(self)

        self.config = config
        self.session = Session(self.config)
        self.ui = ui

        # Statistics
        self.total_posts = 0
        self.total_topics = 0
        self.total_users = 0

        self.current_posts = 0
        self.current_topics = 0
        self.current_users = 0

        self.dump_time = 0

        self.smilies = {}
        self.user_names = {}
        self.user_ids = {}
        self.forums = {}

        self.linkrewriter = LinkRewriter(self)

    def _export_(self):
        self.logger.info('Récupération des statistiques')
        response = self.session.get("/statistics")
        document = PyQuery(response.text)

        # Go through the table of statistics and save the relevant
        # ones
        for element in document.find("table.forumline tr"):
            e = PyQuery(element)

            if e("td.row2 span").eq(0).text() == "Messages":
                self.total_posts = int(e("td.row1 span").eq(0).text())
            elif e("td.row2 span").eq(0).text() == "Nombre de sujets ouvert dans le forum":
                self.total_topics = int(e("td.row1 span").eq(0).text())
            elif e("td.row2 span").eq(0).text() == "Nombre d'utilisateurs":
                self.total_users = int(e("td.row1 span").eq(0).text())

        self.logger.debug('Messages : %d', self.total_posts)
        self.logger.debug('Sujets : %d', self.total_topics)
        self.logger.debug('Membres : %d', self.total_users)

        # Add the children nodes, which respectively handle the
        # exportation of the smilies, the users and the message
        self.add_child(Smilies())

        if self.config["use_ocr"]:
            # Use Optical Character Recognition to get the users'
            # emails
            self.add_child(OcrUsers())
        else:
            self.add_child(Users())

        self.add_child(Forums())

    def _dump_(self, sqlfile):
        self.dump_time = int(time.time())

        # Clean tables
        sqlfile.truncate("users")
        sqlfile.truncate("user_group")
        sqlfile.truncate("bots")

        sqlfile.truncate("forums")
        sqlfile.truncate("acl_groups")

        sqlfile.truncate("topics")
        sqlfile.truncate("topics_posted")

        sqlfile.truncate("posts")
        sqlfile.truncate("privmsgs")
        sqlfile.truncate("privmsgs_to")

        sqlfile.truncate("bbcodes")

        # Add bbcodes tags
        for bbcode in phpbb.BBCODES:
            sqlfile.insert("bbcodes", bbcode)

    def __setstate__(self, state):
        Node.__setstate__(self, state)
        self.linkrewriter = LinkRewriter(self)
        # TODO : recompute current counts

    def save(self):
        """
        Dump the tree representing the forum in a pickle file
        """
        self.logger.info("Sauvegarde de l'état courant.")
        with open("save.pickle", "wb") as fileobj:
            pickle.dump(self, fileobj, 2)

    def get_topics(self):
        """
        Iterator on the topics of the forum
        """
        for forum in self.forums.values():
            for topic in forum.get_topics():
                yield topic

    def get_posts(self):
        """
        Iterator on the posts of the forum
        """
        for topic in self.get_topics():
            for post in topic.get_posts():
                yield post

def load(config, ui):
    """
    Returns the BB node contained in the file save.pickle.
    """
    logger = logging.getLogger("lalf.bb.load")

    try:
        with open("save.pickle", "rb") as fileobj:
            bb = pickle.load(fileobj)
            bb.config = config
            bb.session = Session(config)
            bb.ui = ui
    except FileNotFoundError:
        bb = BB(config, ui)
    except EOFError:
        logger.warning("Erreur lors du chargement de la sauvegarde. Réinitialisation.")
        bb = BB(config, ui)
    return bb
