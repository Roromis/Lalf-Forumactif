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
            for c in self.children:
                c.export()
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
        
        for c in self.children:
            c.dump(file)

    def _dump_(self, file):
        return
