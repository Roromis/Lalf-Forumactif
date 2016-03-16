# -*- coding: utf-8 -*-
#
# This file is part of Lalf.
#
# Lalf is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Foobar is distributed in the hope that it will be useful,
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
logger = logging.getLogger("lalf")

import re
import pickle
from pyquery import PyQuery

from lalf.node import Node
from lalf.forums import Forums
from lalf.users import Users
from lalf.ocrusers import OcrUsers
from lalf.smileys import Smileys
from lalf.config import config
from lalf import phpbb
from lalf import sql
from lalf import session
from lalf import counters

class BB(Node):
    """
    The BB node is the root of the tree representing the forum.
    """
    
    """
    Attributes to save
    """
    STATE_KEEP = ["nbposts", "nbtopics", "nbusers"]
    
    def __init__(self):
        Node.__init__(self, None)

    def _export_(self):
        # Get stats
        logger.info('Récupération des statistiques')
        r = session.get("/statistics")
        d = PyQuery(r.text)
    
        for i in d.find("table.forumline tr"):
            e = PyQuery(i)
            
            try:
                if e("td.row2 span").eq(0).text() == "Messages":
                    self.nbposts = int(e("td.row1 span").eq(0).text())
                elif e("td.row2 span").eq(0).text() == "Nombre de sujets ouvert dans le forum":
                    self.nbtopics = int(e("td.row1 span").eq(0).text())
                elif e("td.row2 span").eq(0).text() == "Nombre d'utilisateurs":
                    self.nbusers = int(e("td.row1 span").eq(0).text())
            except:
                continue
        
        logger.debug('Messages : %d', self.nbposts)
        logger.debug('Sujets : %d', self.nbtopics)
        logger.debug('Membres : %d', self.nbusers)
        
        counters.topictotal = self.nbtopics
        counters.usertotal = self.nbusers
        counters.posttotal = self.nbposts
        
        # Add the children nodes, which respectively handle the
        # exportation of the users, the smileys and the message
        self.smileys = Smileys(self)
        if config["use_ocr"]:
            # Use Optical Character Recognition to get the users'
            # emails
            self.users = OcrUsers(self)
        else:
            self.users = Users(self)
        self.forums = Forums(self)

        self.children.append(self.smileys)
        self.children.append(self.users)
        self.children.append(self.forums)

    def __setstate__(self, dict):
        Node.__setstate__(self, dict)
        counters.topictotal = self.nbtopics
        counters.usertotal = self.nbusers
        counters.posttotal = self.nbposts

        self.smileys = self.children[0]
        self.users = self.children[1]
        self.forums = self.children[2]

    def save(self):
        logger.info("Sauvegarde de l'état courant.")
        with open("save.pickle", "wb") as f:
            pickle.dump(self, f)
    
    def get_forums(self):
        return self.forums.children

    def get_users(self):
        return self.users.get_users()
            
    def get_smileys(self):
        return self.smileys.smileys

    def _dump_(self, file):
        # Clean tables
        sql.truncate(file, "forums")
        sql.truncate(file, "acl_groups")

        sql.truncate(file, "topics")
        sql.truncate(file, "topics_posted")

        sql.truncate(file, "posts")
        sql.truncate(file, "privmsgs")

        # Add bbcodes tags
        sql.truncate(file, "bbcodes")
        for bbcode in phpbb.bbcodes:
            sql.insert(file, "bbcodes", bbcode)

def load():
    """
    Returns the BB node contained in the file save.pickle.
    """
    try:
        with open("save.pickle", "rb") as f:
            bb = pickle.load(f)
    except FileNotFoundError:
        bb = BB()
    except EOFError:
        logger.warning("Erreur lors du chargement de la sauvegarde. Réinitialisation.")
        bb = BB()
    return bb
