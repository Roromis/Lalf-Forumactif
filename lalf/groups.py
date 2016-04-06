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
Module handling the exportation of groups
"""

import re

from lxml import html

from lalf.node import Node, Page, PaginatedNode, ParsingError
from lalf.util import pages, Counter, clean_url

TYPES = {
    "Groupe fermé": 1,
    "Groupe invisible": 2,
    "Groupe ouvert": 4
}

class GroupPage(Page):
    """
    Node representing a page of a group
    """

    def __init__(self, page_id):
        Page.__init__(self, page_id)

    def _export_(self):
        self.logger.debug('Récupération du groupe %d (page %d)', self.group.id, self.id)
        params = {
            "start": self.id
        }
        response = self.session.get(r"/g{}-a".format(self.group.id), params=params)
        document = html.fromstring(response.content)

        pattern = re.compile(r"/u(\d+)")

        for link in document.cssselect("a"):
            match = pattern.fullmatch(clean_url(link.get("href", "")))
            if match:
                user = self.users.get(int(match.group(1)))
                if self.group not in user.groups:
                    user.groups.append(self.group)

@Node.expose(self="group")
class Group(PaginatedNode):
    """
    Node representing a group
    """
    def __init__(self, group_id, name, description, leader_name, colour, group_type):
        PaginatedNode.__init__(self, group_id)
        self.name = name
        self.description = description
        self.leader_name = leader_name
        self.colour = colour
        self.type = group_type

        self.newid = None

    def _export_(self):
        self.logger.info('Récupération du groupe %d', self.id)

        if self.id == 1:
            # Administrators group
            self.newid = 5
            self.leader_name = self.config["admin_name"]
        else:
            self.newid = self.groups.count.newid()

        response = self.session.get("/g{}-a".format(self.id))
        for page in pages(response.content):
            self.add_page(GroupPage(page))

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

class Groups(Node):
    """
    Node used to export the groups
    """
    def __init__(self):
        Node.__init__(self, "groups")
        # There are 7 groups already defined in phpbb, start at 8
        self.count = Counter(8)

    def __setstate__(self, state):
        Node.__setstate__(self, state)

    def remove_children(self):
        Node.remove_children(self)
        self.count.reset()

    def _export_(self):
        self.logger.info("Récupération des groupes")

        params = {
            "part": "users_groups",
            "sub" : "groups"
        }
        response = self.session.get_admin("/admin/index.forum", params=params)
        document = html.fromstring(response.content)

        urlpattern = re.compile(r"/g(\d+)-.*")
        stylepattern = re.compile("color:#(.{3,6})")

        for row in document.cssselect('table tr'):
            cols = row.cssselect("td")

            if not cols:
                continue

            try:
                link = cols[2].cssselect("a")[0]
                name = link.text_content()
                description = cols[3].text_content()
                leader_name = cols[4].text_content()
                group_type = TYPES.get(cols[6].text_content(), 1)
            except IndexError:
                raise ParsingError(document)

            urlmatch = urlpattern.fullmatch(link.get("href", ""))
            if not urlmatch:
                continue

            group_id = int(urlmatch.group(1))

            stylematch = stylepattern.fullmatch(link.get("style", ""))
            if stylematch:
                colour = stylematch.group(1)
                if colour == "000":
                    colour = ""
            else:
                colour = ""

            if description == "Personal User":
                break

            self.add_child(Group(group_id, name, description, leader_name, colour, group_type))
