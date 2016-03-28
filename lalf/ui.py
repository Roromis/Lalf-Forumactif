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
Module handling the interface
"""

import logging
from shutil import get_terminal_size
import sys

class DummyUI(object):
    """
    Interface displaying nothing, for debugging
    """
    def update(self):
        return

class Formatter(logging.Formatter):
    """
    Formatter displaying debug and info messages normally, and messages with
    level warning and above with their levelname
    """
    def __init__(self):
        self.formatter = logging.Formatter('%(message)s')
        self.warning_formatter = logging.Formatter('%(levelname)-8s : %(message)s')

    def format(self, record):
        if record.levelno > logging.INFO:
            return self.warning_formatter.format(record)
        else:
            return self.formatter.format(record)

class UI(logging.Handler):
    """
    Handler displaying the logging messages and a progress bar
    """
    def __init__(self):
        logging.Handler.__init__(self, logging.INFO)
        self.setFormatter(Formatter())

        logger = logging.getLogger("lalf")
        logger.addHandler(self)

        self.bb = None

        self.current = 0
        self.total = 0
        self.progressbar = ""
        self.width = 0

    def emit(self, record):
        message = self.format(record).split("\n", 1)

        self.update_bar()

        # Go back to to beginning of the line
        sys.stdout.write("\r")

        # Display the first line of the message and erase the end of the line
        sys.stdout.write(message[0])
        sys.stdout.write(" "*(self.width - len(message[0])))

        # Display the other lines of the message
        if len(message) > 1:
            sys.stdout.write("\n")
            sys.stdout.write(message[1])

        # Display the progress bar on the next line
        sys.stdout.write("\n")
        sys.stdout.write(self.progressbar)
        sys.stdout.flush()

    def update_bar(self):
        """
        Update the progress bar without displaying it

        Returns
            bool: True if the progress bar changed and should be redrawn
        """
        changed = False

        width, _ = get_terminal_size()

        # Drawing at the end of the row will create a newline on windows
        width -= 1

        if width != self.width:
            # The width of the terminal changed
            self.width = width
            changed = True

        # Compute progress
        if self.bb:
            current = self.bb.current_users + self.bb.current_topics + self.bb.current_posts
            total = self.bb.total_users + self.bb.total_topics + self.bb.total_posts
        else:
            current = 0
            total = 0

        if self.current != current or self.total != total:
            self.current = current
            self.total = total
            changed = True

        if changed:
            # Size of the actual progress bar
            # Leave space for two brackets, one space, and four characters for the percentage
            barsize = self.width - 7

            if total == 0:
                completedsize = 0
                uncompletedsize = barsize
                progress = 0
            else:
                # Size of the part of the progress bar that is completed
                completedsize = current * barsize // total
                if completedsize > barsize:
                    completedsize = barsize
                uncompletedsize = barsize - completedsize

                # Progress (in percents)
                progress = current * 100 // total
                if progress > 100:
                    progress = 100

            progressbar = "[{}{}] {:3}%".format("#"*completedsize, " "*uncompletedsize, progress)
            if progressbar != self.progressbar:
                self.progressbar = progressbar
                return True

        # The progress bar did not change
        return False

    def update(self):
        """
        Update and display the progress bar
        """
        if self.update_bar():
            sys.stdout.write("\r")
            sys.stdout.write(self.progressbar)
