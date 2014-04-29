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

import png
import subprocess

from lalf.exceptions import *
from lalf.config import config

def toolong(img):
    """
    Returns true if the email displayed in the image img is too long to
    be displayed entirely
    """
    reader = png.Reader(filename=img)
    w, h, pixels, metadata = reader.read_flat()

    for i in range(w-6,w):
        for j in range(0,h):
            if pixels[i+j*w] != 0:
                return True
    return False

def totext(img):
    """
    Returns the string contained in the image img
    """
    try:
        return subprocess.check_output([config.gocr, "-i", img], universal_newlines=True).strip()
    except FileNotFoundError:
        raise GocrNotInstalled()
