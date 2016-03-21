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
from lalf.config import config
from lalf import phpbb
from lalf import sql
from lalf import session

@Node.expose(self="root")
class BB(Node):
    """
    The BB node is the root of the tree representing the forum.

    Attributes:
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
                  "current_posts", "current_topics", "current_users"]

    def __init__(self):
        Node.__init__(self)

        # Statistics
        self.total_posts = 0
        self.total_topics = 0
        self.total_users = 0

        self.current_posts = 0
        self.current_topics = 0
        self.current_users = 0

        self.dump_time = 0

    def _export_(self):
        self.logger.info('Récupération des statistiques')
        response = session.get("/statistics")
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

        if config["use_ocr"]:
            # Use Optical Character Recognition to get the users'
            # emails
            self.add_child(OcrUsers())
        else:
            self.add_child(Users())

        self.add_child(Forums())

    def _dump_(self, sqlfile):
        self.dump_time = int(time.time())

        # Clean tables
        sql.truncate(sqlfile, "users")
        sql.truncate(sqlfile, "user_group")
        sql.truncate(sqlfile, "bots")

        sql.truncate(sqlfile, "forums")
        sql.truncate(sqlfile, "acl_groups")

        sql.truncate(sqlfile, "topics")
        sql.truncate(sqlfile, "topics_posted")

        sql.truncate(sqlfile, "posts")
        sql.truncate(sqlfile, "privmsgs")
        sql.truncate(sqlfile, "privmsgs_to")

        sql.truncate(sqlfile, "bbcodes")

        # Add bbcodes tags
        for bbcode in phpbb.bbcodes:
            sql.insert(sqlfile, "bbcodes", bbcode)

    def __setstate__(self, state):
        Node.__setstate__(self, state)
        # TODO : recompute current counts

    def save(self):
        """
        Dump the tree representing the forum in a pickle file
        """
        self.logger.info("Sauvegarde de l'état courant.")
        with open("save.pickle", "wb") as fileobj:
            pickle.dump(self, fileobj)

    @property
    def smilies(self):
        """
        Smilies: The node handling the exportation of the smilies
        """
        try:
            return self.children[0]
        except IndexError:
            raise AttributeError("'BB' object has no attribute 'smilies'")

    @property
    def users(self):
        """
        Users: The node handling the exportation of the users
        """
        try:
            return self.children[1]
        except IndexError:
            raise AttributeError("'BB' object has no attribute 'users'")

    @property
    def forums(self):
        """
        Forums: The node handling the exportation of the forums
        """
        try:
            return self.children[2]
        except IndexError:
            raise AttributeError("'BB' object has no attribute 'forums'")

    def get_forums(self):
        """
        Returns a list of the forums
        """
        return self.forums.children

    def get_topics(self):
        """
        Iterator on the topics of the forum
        """
        for forum in self.get_forums():
            for topic in forum.get_topics():
                yield topic

    def get_posts(self):
        """
        Iterator on the posts of the forum
        """
        for topic in self.get_topics():
            for post in topic.get_posts():
                yield post

    def get_users(self):
        """
        Returns a list of the users
        """
        return self.users.get_users()

    def get_smilies(self):
        """
        Returns a dictionnary associating each smiley id to its informations
        """
        return self.smilies.smilies

def load():
    """
    Returns the BB node contained in the file save.pickle.
    """
    logger = logging.getLogger("lalf.bb.load")

    try:
        with open("save.pickle", "rb") as fileobj:
            bb = pickle.load(fileobj)
    except FileNotFoundError:
        bb = BB()
    except EOFError:
        logger.warning("Erreur lors du chargement de la sauvegarde. Réinitialisation.")
        bb = BB()
    return bb
