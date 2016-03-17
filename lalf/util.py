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
Module containing some utility functions
"""

import re

MONTHS = {
    "Ja": 1,
    "F": 2,
    "Mar": 3,
    "Av": 4,
    "Mai": 5,
    "Juin": 6,
    "Juil": 7,
    "Ao": 8,
    "S": 9,
    "O": 10,
    "N": 11,
    "D": 12
}

ILLEGAL_CHARS = ['?', '<', '>', '|', '*', '/', '\\', '"', ":", ";"]

def month(string):
    """
    Converts an abbreviated french month name to an int
    """
    for key, value in MONTHS.items():
        if string.startswith(key):
            return value

def clean_filename(filename):
    """
    Remove the illegal characters (?<>|*/\":;) from a filename
    """
    for char in ILLEGAL_CHARS:
        filename = filename.replace(char, '')

    return filename

def pages(text):
    """
    Iterator on the page numbers

    Args:
        text (str): The content of the first page (of a forum, topic, ...)
    """
    # Search for the pagination code
    match = re.search(
        r'function do_pagination_start\(\)[^\}]*'
        r'start = \(start > \d+\) \? (\d+) : start;[^\}]*'
        r'start = \(start - 1\) \* (\d+);[^\}]*\}', text)

    if match:
        number = int(match.group(1))
        itemsperpage = int(match.group(2))
    else:
        number = 1
        itemsperpage = 0

    for page in range(0, number):
        yield page*itemsperpage
