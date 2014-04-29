#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger("lalf")
logger.setLevel(logging.DEBUG)

# Log format
#formatter = logging.Formatter('%(levelname)-8s : %(message)s')

import sys

from lalf.bb import load, BB
from lalf import config
from lalf import ui
from lalf import session
from lalf.__version__ import __version__

def main():
    # File output
    filehandler = logging.FileHandler('debug.log')
    filehandler.setLevel(logging.DEBUG)
    logger.addHandler(filehandler)
    
    config.read("config.cfg")
    ui.init()

    logger.info("Lalf %s", __version__)
    
    bb = load()

    try:
        bb.export()
    except Exception as e:
        bb.save()
        logger.exception("""Une erreur est survenue. Essayez de relancer le script. Si vous rencontrez la même erreur ("{exception}"), créez un rapport de bug à l'adresse suivante SI ELLE N'A PAS ENCORE ÉTÉ SIGNALÉE :
https://github.com/Roromis/Lalf-Forumactif/issues""".format(exception=repr(e)))
        sys.exit()

    ui.update()

    for user in bb.get_users():
        user.confirm_email()

    bb.save()

    logging.info("Génération du fichier SQL")
    with open("phpbb.sql", "w") as f:
        bb.dump(f)

    logging.info("L'exportation a été effectuée avec succés.")

        
if __name__ == "__main__":
    main()
