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
logger = logging.getLogger("lalf")

import os
import time
import shlex
import struct
import platform
import subprocess

from lalf.config import config

bb = None
uihandler = None
exporting = True

def get_terminal_size():
    """ getTerminalSize()
     - get width and height of console
     - works on linux,os x,windows,cygwin(windows)
     originally retrieved from:
     http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    """
    current_os = platform.system()
    tuple_xy = None
    if current_os == 'Windows':
        tuple_xy = _get_terminal_size_windows()
        if tuple_xy is None:
            tuple_xy = _get_terminal_size_tput()
            # needed for window's python in cygwin's xterm!
    if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
        tuple_xy = _get_terminal_size_linux()
    if tuple_xy is None:
        tuple_xy = (80, 25)      # default value
    return tuple_xy


def _get_terminal_size_windows():
    try:
        from ctypes import windll, create_string_buffer
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom,
             maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
    except:
        pass


def _get_terminal_size_tput():
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    try:
        cols = int(subprocess.check_call(shlex.split('tput cols')))
        rows = int(subprocess.check_call(shlex.split('tput lines')))
        return (cols, rows)
    except:
        pass


def _get_terminal_size_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            cr = struct.unpack('hh',
                               fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
            return cr
        except:
            pass
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])

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

    if config["verbose"]:
        formatter = logging.Formatter('%(levelname)-8s : %(message)s')
        uihandler.setLevel(logging.DEBUG)
    else:
        formatter = logging.Formatter('%(message)s')
        uihandler.setLevel(logging.INFO)

    uihandler.setFormatter(formatter)
    logger.addHandler(uihandler)
