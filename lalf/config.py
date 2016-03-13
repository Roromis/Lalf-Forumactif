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

import logging
logger = logging.getLogger("lalf")

import os.path
import configparser

from lalf.exceptions import *

"""
Dictionnary containing the configuration
"""
config = {
    "url" : "",
    "admin_name" : "",
    "admin_password" : "",
    "table_prefix" : "",
    "use_ocr" : True,
    "gocr" : "",
    "temporary_theme": "",
    "verbose" : False
}

def read(filename):
    """
    Read the configuration from filename and write it in the config
    dictionnary
    """
    cfg = configparser.ConfigParser()
    with open(filename, "r") as f:
        cfg.read_file(f)

    try:
        for k,v in config.items():
            if type(v) == bool:
                config[k] = cfg.getboolean("Configuration", k)
            else:
                config[k] = cfg.get("Configuration", k)
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        raise InvalidConfigurationFile(filename, e)
