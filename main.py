#!/usr/bin/env python

verbose = True

import logging
logger = logging.getLogger("lalf")
logger.setLevel(logging.DEBUG)

# Log format
#formatter = logging.Formatter('%(levelname)-8s : %(message)s')

# File output
filehandler = logging.FileHandler('debug.log')
filehandler.setLevel(logging.DEBUG)
#filehandler.setFormatter(formatter)
logger.addHandler(filehandler)

import config
import sys
import session
from bb import load as bbload
import ui

def main():
    config.read("config.cfg")
    ui.init()
    """# Console output
    consolehandler = logging.StreamHandler()
    if config.config['verbose']:
        consolehandler.setLevel(logging.DEBUG)
    else:
        formatter = logging.Formatter('%(message)s')
        consolehandler.setLevel(logging.INFO)
        consolehandler.setFormatter(formatter)
    logger.addHandler(consolehandler)
"""
    bb = bbload()

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

    logging.info("Exportation terminée")

    logging.info("Génération du fichier SQL")
    with open("phpbb.sql", "w") as f:
        bb.dump(f)

    logging.info("L'exportation a été effectuée avec succés.")

        
if __name__ == "__main__":
    main()
