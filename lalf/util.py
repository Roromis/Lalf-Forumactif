# -*- coding: utf-8 -*-

import os

root = None
possible_roots = [
    os.path.join(os.path.expanduser("~"), "Lalf"),
    "."
    ]

class NoConfigurationFile(Exception):
    """
    Exception raised when the configuration file does not exists
    """
    
    def __init__(self, filename):
        """
        filename -- path of the configuration file that could not be found
        """
        self.filename = filename

    def __str__(self):
        root, ext = os.path.splitext(self.filename)
        examplefilename = "{root}.example{ext}".format(root=root, ext=ext)
        return """Le fichier de configuration ({filename}) n'existe pas.
Créez-le en vous inspirant du fichier {example} et placez le dans l'un de ces dossiers :
{roots}""".format(filename=self.filename, example=examplefilename, roots=", ".join([os.path.realpath(r) for r in possible_roots]))

def find_root():
    global possible_roots
    
    for r in possible_roots:
        if os.path.isfile(os.path.join(r, "config.cfg")):
            return r

    raise NoConfigurationFile("config.cfg")

def path(*args):
    """
    path(dir_1, ..., dir_n, file) returns the path
    "~/Lalf/dir_1/.../dir_n/file" and ensures that the directory
    "~/Lalf/dir1/.../dir_n/" exists.
    """
    global root

    if root == None:
        root = find_root()
    
    if len(args) == 0:
        dirname = root
        filename = root
    else:
        dirname = os.path.join(root, *args[:-1])
        filename = os.path.join(root, *args)

    if not os.path.isdir(dirname):
        os.makedirs(dirname)
        
    return filename

def month(s):
    """
    Converts an abbreviated french month name to an int
    """
    if s.startswith("Ja"):
        return 1 
    elif s.startswith("F"):
        return 2
    elif s.startswith("Mar"):
        return 3
    elif s.startswith("Av"):
        return 4
    elif s.startswith("Mai"):
        return 5
    elif s.startswith("Juin"):
        return 6
    elif s.startswith("Juil"):
        return 7
    elif s.startswith("Ao"):
        return 8
    elif s.startswith("S"):
        return 9
    elif s.startswith("O"):
        return 10
    elif s.startswith("N"):
        return 11
    elif s.startswith("D"):
        return 12

def clean_filename(filename):
    """
    Returns filename, with the illegal characers (?<>|*/":;) removed
    """
    chars = [
        (['?', '<', '>', '|', '*', '/', '"'], ''),
        ([':', ';'], ',')
    ]
    for c,c2 in chars:
        for c1 in c:
            filename = filename.replace(c1, c2)
    return filename

def clean(s):
    """Removes all accents from the string"""
    if isinstance(s,str):
        s = unicode(s,"utf8","replace")
        s = unicodedata.normalize('NFD',s)
        return s.encode('ascii','ignore')
