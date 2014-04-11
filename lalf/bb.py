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
from lalf.util import path
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
        if config["use_ocr"]:
            # Use Optical Character Recognition to get the users'
            # emails
            self.children.append(OcrUsers(self))
        else:
            self.children.append(Users(self))
        self.children.append(Smileys(self))
        self.children.append(Forums(self))

    def __setstate__(self, dict):
        Node.__setstate__(self, dict)
        counters.topictotal = self.nbtopics
        counters.usertotal = self.nbusers
        counters.posttotal = self.nbposts

    def save(self):
        logger.info("Sauvegarde de l'état courant.")
        with open(path("save.pickle"), "wb") as f:
            pickle.dump(self, f)
    
    def get_forums(self):
        for c in self.children[2].children:
            yield c

    def get_users(self):
        return self.children[0].get_users()
            
    def get_smileys(self):
        for p in self.children[0].children:
            for c in p.children:
                yield p

    def _dump_(self, file):
        # Add bbcodes tags
        sql.truncate(file, "bbcodes")
        for bbcode in phpbb.bbcodes:
            sql.insert(file, "bbcodes", bbcode)

def load():
    """
    Returns the BB node contained in the file save.pickle.
    """
    try:
        with open(path("save.pickle"), "rb") as f:
            bb = pickle.load(f)
    except FileNotFoundError:
        bb = BB()
    except EOFError:
        logger.warning("Erreur lors du chargement de la sauvegarde. Réinitialisation.")
        bb = BB()
    return bb
