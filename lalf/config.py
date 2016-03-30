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
Module handling the configuration
"""

import configparser
import os.path

# Options defined in the config file
STRINGS = ["url", "admin_name", "admin_password", "table_prefix", "gocr", "temporary_theme",
           "phpbb_url", "default_lang"]
BOOLEANS = ["export_smilies", "rewrite_links"]

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

def read(filename):
    """
    Read the configuration from filename and write it in the config
    dictionnary
    """
    if not os.path.isfile(filename):
        raise NoConfigurationFile(filename)

    cfg = configparser.ConfigParser()
    with open(filename, "r") as fileobj:
        cfg.read_file(fileobj)

    config = {}

    try:
        for option in STRINGS:
            config[option] = cfg.get("Configuration", option)

        for option in BOOLEANS:
            config[option] = cfg.getboolean("Configuration", option)
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        raise InvalidConfigurationFile(filename, e)

    return config
