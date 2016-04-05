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
Module handling the connections to the forum
"""

import logging
import time
from urllib.parse import urlparse, urlunparse

import requests
from pyquery import PyQuery

class UnableToConnect(Exception):
    """
    Exception raised when the script failed to connect to the forum
    """

    def __str__(self):
        return "Impossible de se connecter. Vérifiez les identifiants de l'administrateur"

class Session(object):
    """
    Object handling the connections to the forum
    """
    def __init__(self, config):
        self.logger = logging.getLogger("lalf.session.Session")

        self.config = config
        self.session = requests.Session()
        self.sid = None
        self.tid = None

    def url(self, path):
        """
        Returns the full url corresponding to the path given in argument.
        """
        return urlunparse(("http", self.config["url"], path, '', '', ''))

    def _get(self, path, **kwargs):
        """
        Download a file
        """
        # Set the temporary theme
        if self.config["temporary_theme"] != '' and path[:6] != '/admin':
            if "params" not in kwargs:
                kwargs["params"] = {}

            kwargs["params"]["change_temp"] = self.config["temporary_theme"]

        # Set a "normal" user agent
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0")

        return self.session.get(self.url(path), **kwargs)

    def connect(self):
        """
        Connect to the forum and initialize session, sid and tid.
        """
        self.logger.debug('Connection au forum')

        # Reset session
        self.session.close()
        self.sid = None
        self.tid = None

        self.session = requests.Session()
        self.session.keep_alive = False

        # Log in
        params = {
            'autologin': 1,
            'login': 'Connexion',
            'password': self.config["admin_password"],
            'username': self.config["admin_name"],
            'redirect': ""}
        self._get("/login", params=params)

        # Check that the user is connected
        self.logger.debug('Récupération du sid')
        for name, value in self.session.cookies.items():
            if name[-3:] == "sid":
                self.sid = value

        if self.sid is None:
            self.logger.critical('Échec de la connection.')
            raise UnableToConnect()

        if self.tid is None:
            self.logger.debug('Récupération du tid')

            response = self._get('/admin/index.forum')
            try:
                self.tid = urlparse(response.url).query.split("=")[1]
            except IndexError:
                self.logger.critical('Impossible de récupérer le tid.')
                raise UnableToConnect()

    def connected(self, html=None):
        """
        Check if the user successfuly connected.

        Parameters :
        html -- source of the last downloaded page
        """
        if self.sid:
            if html:
                document = PyQuery(html)
                for element in document(".mainmenu"):
                    if element.get("href", "") == "/login":
                        return False
            return True
        return False

    def get(self, path, **kwargs):
        """
        Download a page of the forum
        """
        response = self._get(path, **kwargs)

        failures = 0
        while response.status_code >= 300 or not self.connected(response.content):
            if failures >= 4:
                # The connection failed four times, there must be something wrong
                raise UnableToConnect()
            failures += 1

            if failures >= 2:
                # The connection failed two times, wait
                self.logger.info(
                    "La connexion a échoué au moins deux fois, attend 30 "
                    "secondes avant de réessayer.")
                time.sleep(30)

            try:
                self.connect()
            except UnableToConnect:
                continue
            response = self._get(path, **kwargs)

        return response

    def get_admin(self, path, **kwargs):
        """
        Download a page of the forum's administration panel
        """
        if not self.tid:
            self.connect()

        if "params" not in kwargs:
            kwargs["params"] = {}

        kwargs["params"]["extended_admin"] = 1
        kwargs["params"]["tid"] = self.tid

        return self.get(path, **kwargs)

    def get_image(self, image, **kwargs):
        """
        Download an image
        """
        url = urlparse(image)

        if url.scheme == '' or url.netloc == '':
            image = self.url(image)

        return self.session.get(image, **kwargs)
