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

    logger.info("Lalf %s", __version__)
    logger.debug("OS : %s", sys.platform)

    bb = load()

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

    for user in bb.users.values():
        user.confirm_email()

    bb.save()

    with SqlFile("phpbb.sql") as sqlfile:
        bb.dump(sqlfile)

    logger.info("L'exportation a été effectuée avec succés.")


if __name__ == "__main__":
    main()
