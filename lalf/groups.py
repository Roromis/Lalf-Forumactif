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
Module handling the exportation of users (DEPRECATED)

This is the module that previously handled the exporation of
users. Using it can (and probably will) prevent you from having access
to the users list of your administration panel during 24h (thus
preventing you from exporting them).

The ocrusers module now handles the exportation, using this users
module to create the entries in the sql file.
"""

import re

from pyquery import PyQuery

from lalf.node import Node
from lalf.util import pages, Counter

TYPES = {
    "Groupe fermé": 1,
    "Groupe invisible": 2,
    "Groupe ouvert": 4
}

class GroupPage(Node):
    """
    Node representing a page of a group
    """

    STATE_KEEP = ["page"]

    def __init__(self, page):
        Node.__init__(self)
        self.page = page

    def _export_(self):
        self.logger.debug('Récupération du groupe %d (page %d)', self.group.oldid, self.page)
        params = {
            "start": self.page
        }
        response = self.session.get(r"/g{}-a".format(self.group.oldid), params=params)
        document = PyQuery(response.text)

        pattern = re.compile(r"/u(\d+)")

        for element in document.find("a"):
            url = element.get("href", "")
            match = pattern.fullmatch(url)
            if match:
                user = self.users[int(match.group(1))]
                if self.group not in user.groups:
                    user.groups.append(self.group)

@Node.expose(self="group")
class Group(Node):
    """
    Node representing a group
    """

    STATE_KEEP = ["oldid", "newid", "name", "description", "leader_name", "colour", "type"]

    def __init__(self, oldid, name, description, leader_name, colour, group_type):
        Node.__init__(self)
        self.oldid = oldid
        self.name = name
        self.description = description
        self.leader_name = leader_name
        self.colour = colour
        self.type = group_type

        self.newid = None

    def _export_(self):
        self.logger.info('Récupération du groupe %d', self.oldid)

        if self.oldid == 1:
            # Administrators group
            self.newid = 5
            self.leader_name = self.config["admin_name"]
        else:
            self.newid = self.groups_count.value
            self.groups_count += 1

        response = self.session.get("/g{}-a".format(self.oldid))
        for page in pages(response.text):
            self.add_child(GroupPage(page))

    def _dump_(self, sqlfile):
        if self.newid > 7:
            # Do not create the administrators group
            display = 0 if self.type == 2 else 1
            sqlfile.insert("groups", {
                "group_id": self.newid,
                "group_type": self.type,
                "group_name": self.name,
                "group_desc": self.description,
                "group_display": display,
                "group_colour": self.colour
            })

@Node.expose(count="groups_count")
class Groups(Node):
    """
    Node used to export the groups
    """

    STATE_KEEP = ["count"]

    def __init__(self):
        Node.__init__(self)
        # There are 7 groups already defined in phpbb, start at 8
        self.count = Counter(8)

    def _export_(self):
        self.logger.info("Récupération des groupes")

        params = {
            "part": "users_groups",
            "sub" : "groups"
        }
        response = self.session.get_admin("/admin/index.forum", params=params)
        document = PyQuery(response.text)

        urlpattern = re.compile(r"/g(\d+)-.*")
        stylepattern = re.compile("color:#(.{3,6})")

        for element in document('table > tr'):
            e = PyQuery(element)

            link = e("td a").eq(1)

            urlmatch = urlpattern.fullmatch(link.attr("href"))
            stylematch = stylepattern.fullmatch(link.attr("style"))
            if urlmatch and stylematch:
                oldid = int(urlmatch.group(1))
                colour = stylematch.group(1)
                if colour == "000":
                    colour = ""
                name = link.text()
                description = e("td").eq(3).text()
                leader_name = e("td").eq(4).text()
                group_type = TYPES.get(e("td").eq(6).text(), 1)

                if description == "Personal User":
                    break

                self.add_child(Group(oldid, name, description, leader_name, colour, group_type))
