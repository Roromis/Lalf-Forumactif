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
Module handling the exportation of the forums
"""

import os
import re
from io import BytesIO

from pyquery import PyQuery
from PIL import Image

from lalf.node import Node
from lalf.topics import ForumPage
from lalf.util import pages
from lalf import phpbb

@Node.expose(self="forum")
class Forum(Node):
    """
    Node representing a forum

    Attrs:
        oldid (str): The id in the old forum
        newid (int): The id in the new forum
        left_id (int): Left id of the forum in the nested set model (see
                       https://en.wikipedia.org/wiki/Nested_set_model)
        right_id (int): Right id of the forum in the nested set model
        parent_id (int): The id of the parent forum (0 if it is a category)
        title (str): The title of the forum

        description (str): The description of the forum
        icon (str): The url of the forum icon
    """
    # Attributes to save
    STATE_KEEP = ["oldid", "newid", "parent_id", "title", "description", "icon", "left_id",
                  "right_id"]

    def __init__(self, oldid, newid, left_id, parent_id, title):
        Node.__init__(self)
        self.oldid = oldid
        self.newid = newid
        self.left_id = left_id
        self.right_id = 0
        self.parent_id = parent_id
        self.title = title
        self.description = ""
        self.icon = ""

    def _export_(self):
        self.logger.debug('Récupération du forum %s', self.oldid)

        # Download the forum's page in the administration panel
        params = {
            "part" : "general",
            "sub" : "general",
            "mode" : "edit",
            "fid" : self.oldid
        }
        response = self.session.get_admin("/admin/index.forum", params=params)
        document = PyQuery(response.text)

        # Get the description
        self.description = document("textarea").text()
        if self.description is None:
            self.description = ""

        # Get the icon
        for element in document("input"):
            if element.get("name", "") == "image":
                self.icon = element.text

        if self.icon:
            self.logger.debug("Téléchargement de l'icône du forum %s", self.oldid)
            response = self.session.get_image(self.icon)

            # Get the image's format
            try:
                with Image.open(BytesIO(response.content)) as image:
                    extension = image.format.lower()
            except IOError:
                self.logger.warning("Le format de l'icône du forum %s est inconnu", self.oldid)
            else:
                # Save the image
                if not os.path.isdir(os.path.join("images", "forums")):
                    os.makedirs(os.path.join("images", "forums"))
                self.icon = os.path.join("images", "forums", "{}.{}".format(self.newid, extension))
                with open(self.icon, "wb") as fileobj:
                    fileobj.write(response.content)
        else:
            self.icon = ""

        response = self.session.get("/{}-a".format(self.oldid))
        for page in pages(response.text):
            self.add_child(ForumPage(page))

    def get_topics(self):
        """
        Returns the topics of this forum
        """
        for page in self.children:
            for topic in page.children:
                yield topic

    def _dump_(self, sqlfile):
        if self.oldid[0] == "f":
            forum_type = 1
        else:
            forum_type = 0

        # TODO : add statistics
        sqlfile.insert("forums", {
            "forum_id" : self.newid,
            "parent_id" : self.parent_id,
            "left_id" : self.left_id,
            "right_id" : self.right_id,
            "forum_name" : self.title,
            "forum_desc" : self.description,
            #"forum_desc_bitfield" (TODO)
            #"forum_desc_uid" (TODO)
            "forum_type" : forum_type,
            "forum_image" : self.icon
        })

        for acl in phpbb.default_forum_acl(self.newid):
            sqlfile.insert("acl_groups", acl)

class Forums(Node):
    """
    Node used to export the forums
    """
    def _export_(self):
        self.logger.info('Récupération des forums')

        # Get the first forum
        # TODO : what if it does not exist?
        response = self.session.get("/a-f1/")
        document = PyQuery(response.text)

        # Get the forums hierarchy by parsing the content of the jumpbox

        # List containing at the index i the last forum met at depth i
        depths = []

        # The id of the next forum (ids have to be changed because
        # categories and forums may have the same id in forumactif,
        # but not in phpbb)
        newid = 1

        # Variable used to determine the left and right ids of the
        # forums in the nested set model which is used internally by
        # phpbb (see https://en.wikipedia.org/wiki/Nested_set_model)
        nested_id = 1

        for element in document.find("select option"):
            forum_id = element.get("value", "-1")
            if forum_id != "-1":
                match = re.search('(((\\||\xa0)(\xa0\xa0\xa0))*)\\|--([^<]+)', element.text)
                if match is None:
                    continue

                title = match.group(5)
                depth = len(re.findall('(\\||\xa0)\xa0\xa0\xa0', element.text))

                if depth <= 0:
                    parent_id = 0
                else:
                    parent_id = depths[depth-1].newid

                for _ in range(depth, len(depths)):
                    forum = depths.pop()
                    forum.right_id = nested_id
                    nested_id += 1

                forum = Forum(forum_id, newid, nested_id, parent_id, title)
                depths.append(forum)
                self.add_child(forum)
                newid += 1
                nested_id += 1

        for _ in range(0, len(depths)):
            forum = depths.pop()
            forum.right_id = nested_id
            nested_id += 1
