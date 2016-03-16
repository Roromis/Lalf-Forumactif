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
Module containing the exceptions raised by the script
"""

import os.path
from lalf.config import config

class NoConfigurationFile(Exception):
    """
    Exception raised when the configuration file does not exist
    """

    def __init__(self, filename):
        """
        Args:
            filename (str): The path of the configuration file that could not be found
        """
        Exception.__init__(self)

        self.filename = filename

    def __str__(self):
        root, ext = os.path.splitext(self.filename)
        examplefilename = "{root}.example{ext}".format(root=root, ext=ext)
        return (
            "Le fichier de configuration ({filename}) n'existe pas.\n"
            "Créez-le en vous inspirant du fichier {example} et placez le dans le dossier courant."
        ).format(filename=self.filename, example=examplefilename)

class InvalidConfigurationFile(Exception):
    """
    Exception raised when the configuration file is invalid
    """

    def __init__(self, filename, exception):
        """
        Args:
            filename (str): The path of the configuration file
            exception (str): The exception raised by the parser
        """
        Exception.__init__(self)

        self.filename = filename
        self.exception = exception

    def __str__(self):
        root, ext = os.path.splitext(self.filename)
        examplefilename = "{root}.example{ext}".format(root=root, ext=ext)
        return (
            "Le fichier de configuration ({filename}) est invalide.\n"
            "Modifiez-le en vous inspirant du fichier {example}."
        ).format(filename=self.filename, example=examplefilename)

class UnableToConnect(Exception):
    """
    Exception raised when the script failed to connect to the forum
    """

    def __str__(self):
        return "Impossible de se connecter. Vérifiez les identifiants de l'administrateur"

class MemberPageBlocked(Exception):
    """
    Exception raised when the member page is blocked
    """

    def __str__(self):
        return (
            "Vous avez été bloqué par forumactif. Attendez d'être débloqué avant de relancer le "
            "script (environ 24h).\n\n"

            "Pour savoir si vous êtes bloqué, essayez d'accéder à la deuxième page de la gestion "
            "des utilisateurs dans votre panneau d'administration (Utilisateurs & Groupes > "
            "Gestion des utilisateurs). Si vous êtes bloqué, vous allez être redirigé vers la page "
            "d'accueil de votre panneau d'administration.\n\n"

            "Pour ne pas avoir à attendre, utilisez l'otion use_ocr."
        )

class GocrNotInstalled(Exception):
    """
    Exception raised when the gocr executable cannot be found
    """

    def __str__(self):
        return (
            "L'exécutable de gocr ({exe}) n'existe pas. Vérifiez que gocr est bien installé et "
            "que le chemin est correctement configuré dans le fichier config.cfg."
        ).format(exe=config["gocr"])
