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
Module defining the Node base class
"""

import logging
from collections import OrderedDict

# TODO : save and encrypt document
class ParsingError(Exception):
    """
    Exception raised when an error is encoutered while parsing a page
    """
    def __init__(self, document):
        Exception.__init__(self)
        self.document = document

    def __str__(self):
        return (
            "Erreur de parsing"
        )

class Node(object):
    """
    Node of the forum.

    Attrs:
       children (Dict[Any, Node]): The children of the node
       exposed_attrs [Dict(str, (Node, str))]: Dictionnary containing the attributes
           exposed by parent nodes. This should not be used directly, see @Node.expose.
       exported (bool): True if the node has been exported
    """

    # Attributes to save
    NODE_KEEP = ["id", "children", "exposed_attrs", "exported"]
    STATE_KEEP = []

    # Attributes exposed to the node's children (used by @Node.expose decorator)
    EXPOSE = []

    @staticmethod
    def expose(*args, **kwargs):
        """
        Decorator allowing to make some node attributes visible to its descendants

        Attrs:
            *args: Names of attributes that will be visible to the node's descendants
            **kwargs: Associate the names of attributes that will be exposed to their new name

        Example:
            >>> @Node.expose("list", self="root", id="root_id")
            ... class Root(Node):
            ...     def __init__(self):
            ...         self.list = []
            ...         self.id = 0
            >>> r = Root()
            >>> c = Node()
            >>> r.add_child(c)
            >>> c.root == r
            True
            >>> c.root_id == r.id
            True
            >>> c.list.append(1)
            >>> r.list
            [1]

            The result would be the same if c was not a direct descendant of r
        """
        def decorator(cls):
            cls.EXPOSE = [(attr, attr) for attr in args] + list(kwargs.items())
            return cls
        return decorator

    def __init__(self, node_id):
        self.logger = logging.getLogger("{}.{}".format(self.__class__.__module__,
                                                       self.__class__.__name__))

        self.id = node_id
        self.children = OrderedDict()
        self.exposed_attrs = {}

        self.exported = False

    def __getattr__(self, name):
        if name == "exposed_attrs" or name not in self.exposed_attrs:
            raise AttributeError(
                "'{}' object has no attribute '{}'".format(self.__class__.__name__, name))

        obj, attr = self.exposed_attrs[name]
        if attr == "self":
            return obj
        else:
            return getattr(obj, attr)

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.logger = logging.getLogger("{}.{}".format(self.__class__.__module__,
                                                       self.__class__.__name__))

    def __getstate__(self):
        odict = self.__dict__.copy()

        for k in self.__dict__:
            if not (k in self.NODE_KEEP or k in self.STATE_KEEP):
                del odict[k]

        return odict

    def get_children(self):
        return self.children.values()

    def get(self, child_id):
        return self.children[child_id]

    def first(self):
        return next(iter(self.children.values()))

    def last(self):
        return next(reversed(self.children.values()))

    def add_child(self, child):
        """
        Add a child to the node
        """
        if child.id in self.children:
            self.logger.warning("Child of id %s already exists, skipping", str(child.id))
        else:
            self.children[child.id] = child

            child.exposed_attrs.update(self.exposed_attrs)
            for attr, name in self.__class__.EXPOSE:
                child.exposed_attrs[name] = (self, attr)

    def remove_children(self):
        """
        Remove the children
        """
        self.children.clear()

    def export_children(self):
        """
        Export the children of the node
        """
        for child in self.children.values():
            child.export()

    def export(self):
        """
        Export the node and its children (this method calls the _export_
        method and should not be overwritten)
        """
        if not self.exported:
            self.remove_children()
            self._export_()
            self.exported = True

        self.export_children()

    def _export_(self):
        """
        Export the node.

        This method should export the data of a node, and initialize its
        children (and put them in the children list). It should not
        export the children.
        """
        return

    def dump(self, sqlfile):
        """
        Write a SQL dump of the node in file
        """
        self._dump_(sqlfile)

        for child in self.children.values():
            child.dump(sqlfile)

    def _dump_(self, sqlfile):
        return

class Page(Node):
    NODE_KEEP = Node.NODE_KEEP + ["parent"]

    def __init__(self, node_id):
        Node.__init__(self, node_id)
        self.parent = None

    def add_child(self, child):
        self.parent.add_child(child)

class PaginatedNode(Node):
    NODE_KEEP = Node.NODE_KEEP + ["pages"]

    def __init__(self, node_id):
        Node.__init__(self, node_id)
        self.pages = OrderedDict()

    def add_page(self, page):
        """
        Add a page to the node
        """
        if page.id in self.pages:
            self.logger.warning("Page %s already exists, skipping", str(page.id))
        else:
            self.pages[page.id] = page

            page.parent = self
            page.exposed_attrs.update(self.exposed_attrs)
            for attr, name in self.__class__.EXPOSE:
                page.exposed_attrs[name] = (self, attr)

    def remove_children(self):
        """
        Remove the children
        """
        self.pages.clear()
        Node.remove_children(self)

    def export_children(self):
        """
        Export the children of the node
        """
        for page in self.pages.values():
            page.export()

        Node.export_children(self)
