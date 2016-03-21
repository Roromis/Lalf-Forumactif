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
import os
from shutil import get_terminal_size
import time
import shlex
import struct
import platform
import subprocess

from lalf.config import config

bb = None
uihandler = None
exporting = True

def disp(l):
    global uihandler
    w, h = get_terminal_size()

    if uihandler:
        uihandler.display(h)

    if l:
        namewidth = max([len(i[0]) for i in l])
        numwidth = max([len(str(i[2])) for i in l])
        barwidth = w - namewidth - 2*numwidth - 5

        if barwidth < 0:
            for e in l:
                if e[2] > 0:
                    print(e[0], end="")
                    print(" "*(namewidth-len(e[0])+1), end="")
                    print(" "*(numwidth-len(str(e[1]))+1), end="")
                    print(e[1], end="")
                    print("/", end="")
                    print(e[2])
        else:
            for e in l:
                if e[2] > 0:
                    fullbar = min(barwidth, int((e[1]*barwidth)/e[2]))

                    print(e[0], end="")
                    print(" "*(namewidth-len(e[0])+1), end="")
                    print("[", end="")
                    print("#"*fullbar, end="")
                    print(" "*(barwidth-fullbar), end="")
                    print("]", end="")
                    print(" "*(numwidth-len(str(e[1]))+1), end="")
                    print(e[1], end="")
                    print("/", end="")
                    print(e[2])

def update():
    """
    Update the progress bars
    """
    if bb:
        disp([
            ("Membres", bb.current_users, bb.total_users),
            ("Sujets", bb.current_topics, bb.total_topics),
            ("Messages", bb.current_posts, bb.total_posts)
        ])
    else:
        disp([])

class UiLoggingHandler(logging.Handler):
    """
    Logging handler used to keep the last LENGTH lines of logs.
    """
    LENGTH = 200
    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level)
        self.messages = [""]*self.LENGTH
        self.next = 0

    def emit(self, record):
        message = self.format(record)
        self.messages[self.next] = message
        self.next = (self.next+1)%self.LENGTH
        update()

    def display(self, length=None):
        """
        Print the last length lines of logs.
        """
        if not length:
            length = self.LENGTH
        for i in range(self.next-length, self.next):
            print(self.messages[i])

def init():
    global uihandler
    uihandler = UiLoggingHandler()

    formatter = logging.Formatter('%(levelname)-8s : %(message)s')
    uihandler.setLevel(logging.DEBUG)

    uihandler.setFormatter(formatter)
    logger = logging.getLogger("lalf")
    logger.addHandler(uihandler)
