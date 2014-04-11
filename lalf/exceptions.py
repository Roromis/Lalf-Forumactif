"""
Module containing the exceptions raised by the script
"""

import logging
logger = logging.getLogger("lalf")

import os.path
import traceback

class NoConfigurationFile(Exception):
    """
    Exception raised when the configuration file does not exists
    """
    
    def __init__(self, filename):
        """
        filename -- path of the configuration file that could not be found
        """
        self.filename = filename

    def __str__(self):
        root, ext = os.path.splitext(self.filename)
        examplefilename = "{root}.example{ext}".format(root=root, ext=ext)
        return """Le fichier de configuration ({filename}) n'existe pas.
    Créez-le en vous inspirant du fichier {example}.""".format(filename=self.filename, example=examplefilename)

class InvalidConfigurationFile(Exception):
    """
    Exception raised when the configuration file is invalid
    """
    
    def __init__(self, filename, exception):
        """
        filename -- path of the configuration file
        exception -- exception raised by the parser
        """
        self.filename = filename
        self.exception = exception

    def __str__(self):
        root, ext = os.path.splitext(self.filename)
        examplefilename = "{root}.example{ext}".format(root=root, ext=ext)
        message = """Le fichier de configuration ({filename}) est invalide.
Modifiez-le en vous inspirant du fichier {example}.""".format(filename=self.filename, example=examplefilename)
        return message

class UnableToConnect(Exception):
    """
    Exception raised when the user cannot connect
    """

    def __str__(self):
        message = "Impossible de se connecter. Vérifiez les identifiants de l'administrateur"
        return message

class MemberPageBlocked(Exception):
    """
    Exception raised when the member page is blocked
    """

    def __str__(self):
        message = """Vous avez été bloqué par forumactif. Attendez d'être débloqué avant de relancer le script (environ 24h).

Pour savoir si vous êtes bloqué, essayez d'accéder à la deuxième page de la gestion des utilisateurs dans votre panneau d'administration (Utilisateurs & Groupes > Gestion des utilisateurs). Si vous êtes bloqué, vous allez être redirigé vers la page d'accueil de votre panneau d'administration.

Pour ne pas avoir à attendre, utilisez l'otion use_ocr."""
        return message

class GocrNotInstalled(Exception):
    """
    Exception raised when the gocr executable cannot be found
    """

    def __str__(self):
        message = """L'exécutable de gocr ({exe}) n'existe pas. Vérifiez que gocr est bien installé est que le chemin est correctement configuré dans le fichier config.cfg.""".format(exe=config["gocr"])
        return message
