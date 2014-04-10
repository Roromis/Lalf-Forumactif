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
