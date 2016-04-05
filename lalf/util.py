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
import random
from string import ascii_letters, digits
import time
import datetime
from urllib.parse import urlparse, urlunparse

from pyquery import PyQuery

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

class Counter(object):
    """
    Counter acting as a reference to an integer

    Example:
        >>> n = Counter(5)
        >>> c = n
        >>> n.value, c.value
        5, 5
        >>> c += 1
        >>> n.value, c.value
        6, 6
    """
    def __init__(self, value=0):
        self.value = value

    def __iadd__(self, other):
        self.value += other
        return self

    def __isub__(self, other):
        self.value -= other
        return self

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

def pages(html):
    """
    Iterator on the page numbers

    Args:
        html (str): The content of the first page (of a forum, topic, ...)
    """
    document = PyQuery(html)

    # Search for the pagination code
    match = re.search(
        r'function do_pagination_start\(\)[^\}]*'
        r'start = \(start > \d+\) \? (\d+) : start;[^\}]*'
        r'start = \(start - 1\) \* (\d+);[^\}]*\}', document("script").text())

    if match:
        number = int(match.group(1))
        itemsperpage = int(match.group(2))
    else:
        number = 1
        itemsperpage = 0

    for page in range(0, number):
        yield page*itemsperpage

def random_string():
    """
    Generate a random string of length 8
    """
    return ''.join([random.choice(ascii_letters + digits) for n in range(8)])

def parse_date(string):
    """
    Convert a date to a timestamp
    """
    post_date, post_time = re.split(" [-à] ", string)
    hours, minutes = post_time.split(":")
    post_time = datetime.time(int(hours), int(minutes))

    if post_date == "Aujourd'hui":
        post_date = datetime.date.today()
    elif post_date == "Hier":
        post_date = datetime.date.today() - datetime.timedelta(1)
    else:
        post_date = post_date.split(" ")
        post_date = datetime.date(int(post_date[3]), month(post_date[2]), int(post_date[1]))

    return int(time.mktime(datetime.datetime.combine(post_date, post_time).timetuple()))

def parse_admin_date(string):
    """
    Convert a date of the administrator panel to a timestamp
    """
    date = string.split(" ")
    try:
        return int(time.mktime(time.struct_time(
            (int(date[2]), month(date[1]), int(date[0]), 0, 0, 0, 0, 0, 0))))
    except IndexError:
        return 0

def parse_userlist_date(string):
    """
    Convert a date of the list of users to a timestamp
    """
    date = string.split("/")
    try:
        return int(time.mktime(time.struct_time(
                (int(date[2]), int(date[1]), int(date[0]), 0, 0, 0, 0, 0, 0))))
    except IndexError:
        return 0

def clean_url(string):
    """
    Remove GET parameters and fragment from a url
    """
    url = urlparse(string)
    return urlunparse((url.scheme, url.netloc, url.path, '', '', ''))
