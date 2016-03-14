# -*- coding: utf-8 -*-
#
# This file is part of Lalf.
#
# Lalf is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lalf.  If not, see <http://www.gnu.org/licenses/>.

class Node(object):
    """
    Node of the forum.

    It has the following attributes :
    children -- 
    """

    """
    Attributes to save
    """
    NODE_KEEP = ["children", "parent", "exported", "children_exported"]
    STATE_KEEP = []
    
    def __init__(self, parent=None):
        self.children = []
        self.parent = parent
        self.exported = False
        self.children_exported = False
        
    def export(self):
        """
        Export the node and its children (this method calls the _export_
        method and should not be overwritten)
        """
        if not self.exported:
            self.children = []
            self._export_()
            self.exported = True
        
        if not self.children_exported:
            for child in self.children:
                child.export()
            self.children_exported = True

    def _export_(self):
        """
        Export the node.

        This method should export the data of a node, and initialize its
        children (and put them in the children list). It should not
        export the children.
        """
        raise NotImplementedError("_export_ is a virtual method of Node and should be implemented by its subclasses.")
            
    def __getstate__(self):
        odict = self.__dict__.copy()

        for k in self.__dict__:
            if not (k in self.NODE_KEEP or k in self.STATE_KEEP):
                del odict[k]
        
        return odict

    def __setstate__(self, dict):
        self.__dict__.update(dict)

    def dump(self, file):
        """
        Write a SQL dump of the node in file
        """
        self._dump_(file)
        
        for child in self.children:
            child.dump(file)

    def _dump_(self, file):
        return
