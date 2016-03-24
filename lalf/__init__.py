#!/usr/bin/env python3
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

import logging
import sys

from lalf.bb import load
from lalf.sql import SqlFile
from lalf.config import read as read_config
from lalf.ui import UI
from lalf import session
from lalf.__version__ import __version__

def main():
    logger = logging.getLogger("lalf")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # File output
    filehandler = logging.FileHandler('debug.log')
    filehandler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(levelname)-8s : %(message)s')
    filehandler.setFormatter(formatter)

    logger.addHandler(filehandler)

    config = read_config("config.cfg")
    ui = UI()

    logger.info("Lalf %s", __version__)
    logger.debug("OS : %s", sys.platform)

    if not config["use_ocr"]:
        logger.warning(
            "Il est vivement conseillé d'utiliser la reconaissance de caractère "
            "pour récupérer les adresse email des utilisateurs.")

    bb = load(config, ui)
    ui.bb = bb

    try:
        bb.export()
    except BaseException as e:
        bb.save()
        logger.exception(
            "Une erreur est survenue. Essayez de relancer le script. "
            "Si vous rencontrez la même erreur (%s), créez un rapport "
            "de bug à l'adresse suivante SI ELLE N'A PAS ENCORE ÉTÉ SIGNALÉE :\n"
            "https://github.com/Roromis/Lalf-Forumactif/issues", repr(e))
        sys.exit()

    ui.update()

    for user in bb.user_names.values():
        user.confirm_email()

    bb.save()

    logging.info("Génération du fichier SQL")
    with SqlFile("phpbb.sql", config["table_prefix"]) as sqlfile:
        bb.dump(sqlfile)

    logging.info("L'exportation a été effectuée avec succés.")


if __name__ == "__main__":
    main()
