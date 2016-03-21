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

import subprocess
from PIL import Image

from lalf.config import config

class GocrNotInstalled(Exception):
    """
    Exception raised when the gocr executable cannot be found
    """

    def __str__(self):
        return (
            "L'exécutable de gocr ({exe}) n'existe pas. Vérifiez que gocr est bien installé et "
            "que le chemin est correctement configuré dans le fichier config.cfg."
        ).format(exe=config["gocr"])

def toolong(img):
    """
    Returns true if the email displayed in the image img is too long to
    be displayed entirely
    """
    with Image.open(img) as image:
        width, height = image.size

        for i in range(width-6,width):
            for j in range(0,height):
                if image.getpixel((i, j)) != (255, 255, 255):
                    return True

    return False

def totext(img):
    """
    Returns the string contained in the image img
    """
    try:
        return subprocess.check_output([config["gocr"], "-i", img], universal_newlines=True).strip()
    except FileNotFoundError:
        raise GocrNotInstalled()
