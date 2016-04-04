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
from lalf.groups import Groups
from lalf.users import Users
from lalf.smilies import Smilies
from lalf import phpbb
from lalf.session import Session
from lalf.linkrewriter import LinkRewriter
from lalf.util import parse_date
from lalf.ui import UI
from lalf.config import read as read_config

CONFIG_PATH = "config.cfg"

@Node.expose("config", "session", "ui", "smilies", "users", "forums",
             "announcements", self="root")
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
                  "startdate", "record_online_date", "record_online_users",
                  "site_name", "site_desc", "forums", "announcements"]

    def __init__(self):
        Node.__init__(self, "root")

        self.config = read_config(CONFIG_PATH)
        self.session = Session(self.config)
        self.ui = UI(self)

        # Statistics
        self.total_posts = 0
        self.total_topics = 0
        self.total_users = 0

        self.current_posts = 0
        self.current_topics = 0
        self.current_users = 0

        self.startdate = 0
        self.record_online_date = 0
        self.record_online_users = 0

        self.site_name = ""
        self.site_desc = ""

        self.dump_time = 0

        self.announcements = []

        self.linkrewriter = LinkRewriter(self)

    def __setstate__(self, state):
        Node.__setstate__(self, state)
        self.config = read_config(CONFIG_PATH)
        self.session = Session(self.config)
        self.ui = UI(self)
        self.linkrewriter = LinkRewriter(self)
        # TODO : recompute current counts

    @property
    def smilies(self):
        return self.get("smilies")

    @property
    def users(self):
        return self.get("users")

    @property
    def forums(self):
        return self.get("forums")

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
        for forum in self.forums.get_children():
            for topic in forum.get_topics():
                yield topic

    def get_posts(self):
        """
        Iterator on the posts of the forum
        """
        for topic in self.get_topics():
            for post in topic.get_posts():
                yield post

    def _export_(self):
        self.logger.info('Récupération des statistiques')
        response = self.session.get("/statistics")
        document = PyQuery(response.text)

        # Go through the table of statistics and save the relevant
        # ones
        stats = {}
        for element in document.find("table.forumline tr"):
            e = PyQuery(element)

            stats[e("td span").eq(0).text()] = e("td span").eq(1).text()
            stats[e("td span").eq(2).text()] = e("td span").eq(3).text()

        self.total_posts = int(stats["Messages"])
        self.total_topics = int(stats["Nombre de sujets ouvert dans le forum"])
        self.total_users = int(stats["Nombre d'utilisateurs"])

        self.startdate = parse_date(stats["Ouverture du forum"])
        self.record_online_date = parse_date(stats["Date du record de connexions"])
        self.record_online_users = int(
            stats["Nombre record d'utilisateurs connectés en même temps"])

        self.site_name = document("div.maintitle").eq(0).text().strip(" \n")
        self.site_desc = document("div.maintitle").siblings("span.gen").eq(0).text().strip(" \n")

        self.logger.debug('Messages : %d', self.total_posts)
        self.logger.debug('Sujets : %d', self.total_topics)
        self.logger.debug('Membres : %d', self.total_users)

        # Add the children nodes, which respectively handle the
        # exportation of the smilies, the users and the message
        self.add_child(Smilies())
        self.add_child(Users())
        self.add_child(Groups())
        self.add_child(Forums())

    def _dump_(self, sqlfile):
        self.logger.info("Création du fichier phpbb.sql")
        self.dump_time = int(time.time())

        sqlfile.prefix = self.config["table_prefix"]

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

        # Update configuration and statistics
        sqlfile.set_config("board_startdate", self.startdate)
        sqlfile.set_config("default_lang", self.config["default_lang"])
        sqlfile.set_config("record_online_date", self.record_online_date)
        sqlfile.set_config("record_online_users", self.record_online_users)
        sqlfile.set_config("sitename", self.site_name)
        sqlfile.set_config("site_desc", self.site_desc)

        num_posts = sum(1 for _ in self.get_posts())
        num_topics = sum(1 for _ in self.get_topics())
        num_users = sum(1 for _ in self.users.get_children())

        sqlfile.set_config("num_posts", num_posts)
        sqlfile.set_config("num_topics", num_topics)
        sqlfile.set_config("num_users", num_users)

        newest_user = self.users.last()

        sqlfile.set_config("newest_user_id", newest_user.newid)
        sqlfile.set_config("newest_username", newest_user.name)
        sqlfile.set_config("newest_user_colour", newest_user.colour)

        # Add bbcodes tags
        for bbcode in phpbb.BBCODES:
            sqlfile.insert("bbcodes", bbcode)

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
