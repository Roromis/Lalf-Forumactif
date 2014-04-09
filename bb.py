import logging
logger = logging.getLogger("lalf")

import re
from pyquery import PyQuery
import session
import pickle
from node import Node
from forums import Forums
from users import Users
from ocrusers import OcrUsers
from smileys import Smileys
from config import config
import phpbb
import sql

nbusers = 0
nbtopics = 0
nbposts = 0

class BB(Node):

    """
    Attributes to save
    """
    STATE_KEEP = ["nbposts", "nbtopics", "nbusers"]
    
    def __init__(self):
        Node.__init__(self, None)
        self.nbposts = 0
        self.nbtopics = 0
        self.nbusers = 0

    def _export_(self):
        global nbusers
        global nbtopics
        global nbposts
        
        # Récupère les statistiques
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
        
        nbusers = self.nbusers
        nbtopics = self.nbtopics
        nbposts = self.nbposts
        
        logger.debug('Messages : %d', self.nbposts)
        logger.debug('Sujets : %d', self.nbtopics)
        logger.debug('Membres : %d', self.nbusers)

        # Ajoute les noeuds fils, qui gère respectivement
        # l'exportation des utilisateurs, des smileys et des messages
        if config["use_ocr"]:
            self.children.append(OcrUsers(self))
        else:
            self.children.append(Users(self))
        self.children.append(Smileys(self))
        self.children.append(Forums(self))

    def __setstate__(self, dict):
        global nbusers
        global nbtopics
        global nbposts
        Node.__setstate__(self, dict)
        nbusers = self.nbusers
        nbtopics = self.nbtopics
        nbposts = self.nbposts

    def save(self):
        logger.info("Sauvegarde de l'état courant.")
        with open("save.pickle", "wb") as f:
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
        # Add bbcodes
        for bbcode in phpbb.bbcodes:
            sql.insert(file, "bbcodes", bbcode)

def load():
    try:
        with open("save.pickle", "rb") as f:
            bb = pickle.load(f)
    except FileNotFoundError:
        bb = BB()
    except EOFError:
        logger.warning("Erreur lors du chargement de la sauvegarde. Réinitialisation.")
        bb = BB()
    return bb
