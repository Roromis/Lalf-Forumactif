import logging
logger = logging.getLogger("lalf")

import re
from pyquery import PyQuery
import time
import session
from user import User
import ocr
import ui

number = 0

def month(s):
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

chars = [
    (['?', '<', '>', '|', '*', '/', '"'], ''),
    ([':', ';'], ',')
    ]

def clean_filename(filename):
    for c,c2 in chars:
        for c1 in c:
            filename = filename.replace(c1, c2)
    return filename

class OcrUser(User):
    STATE_KEEP = ["id", "newid", "name", "mail", "posts", "date", "lastvisit", "trust", "img"]

    def __init__(self, parent, id, newid, name, posts, date):
        """
        id -- id of the user in the old forum
        newid -- id of the user in the new forum
        name -- username
        mail -- email address
        posts -- number of posts
        date -- subscription date (timestamp)
        lastvisit -- date of last visit (timestamp)
        trust -- level of trust in the email (3 if we are sure that
          the email is correct, 2 if it is probable, 1 if it is not, 0 if
          none was found)
        img -- path of the image containing the email
        """
        User.__init__(self, parent, id, newid, name, None, posts, date, 0, incuser=False)
        self.trust = 0
        self.exported = False
        self.children_exported = True
        self.img = "usermails/{username}.png".format(username=clean_filename(self.name))

    def validate_email(self):
        """
        Validate the email address found by checking that searching for
        the users who have the address self.mail returns the user
        self.name.
        """
        params = {
            "part" : "users_groups",
            "sub" : "users",
            "username" : self.mail,
            "submituser" : "Ok",
            "sort" : "user_id",
            "order" : "ASC"
        }
        r = session.get_admin("/admin/index.forum", params=params)
        
        d = PyQuery(r.text)

        for i in d('tbody tr'):
            e = PyQuery(i)

            if e("td a").eq(0).text() == self.name:
                return True

        return False
        
    def _export_(self, inc=True):
        if inc:
            self.inc()
        
        # Search for users with name self.name
        try:
            encodedname = self.name.encode("latin1")
        except:
            encodedname = self.name
        
        params = {
            "part" : "users_groups",
            "sub" : "users",
            "username" : encodedname,
            "submituser" : "Ok",
            "sort" : "user_id",
            "order" : "ASC"
        }
        r = session.get_admin("/admin/index.forum", params=params)

        d = PyQuery(r.text)

        for i in d('tbody tr'):
            e = PyQuery(i)
            if e("td a").eq(0).text() == self.name:
                # The user was found
                self.mail = e("td a").eq(1).text()
                if self.mail == "":
                    # The administration panel has been blocked yet,
                    # the email is replaced by an image, get it
                    r = session.get(e("td a img").eq(0).attr("src"))
                    dirname = os.path.dirname(self.img)
                    if not os.path.isdir(dirname):
                        os.makedirs(dirname, exist_ok=True)
                    with open(self.img, "wb") as f:
                        f.write(r.content)

                    # Pass it through the OCR
                    self.mail = ocr.totext(self.img)
                    if ocr.toolong(self.img):
                        # The image is too small for the email, the
                        # user will have to give it
                        self.trust = 1
                    elif self.validate_email():
                        self.trust = 3
                    else:
                        self.trust = 2
                else:
                    # The administration panel hasn't been blocked
                    # yet, the email is available
                    self.mail 
                    self.trust = 3
                
                lastvisit = e("td").eq(4).text()
            
                if lastvisit != "":
                    lastvisit = lastvisit.split(" ")
                    self.lastvisit = time.mktime(time.struct_time((int(lastvisit[2]),month(lastvisit[1]),int(lastvisit[0]),0,0,0,0,0,0)))
                else:
                    self.lastvisit = 0
        
    def confirm_email(self, r=2):
        if self.trust == 2:
            logger.info("L'adresse email de l'utilisateur {name} est probablement valide mais n'a pas pu être validée.".format(name=self.name))
            print("Veuillez saisir l'adresse email de l'utilisateur {name} (laissez vide si l'adresse {email} est correcte) :".format(name=self.name, email=self.mail))
            self.mail = input("> ").strip()
        elif self.trust == 1:
            logger.info("L'adresse email de l'utilisateur {name} est probablement invalide.".format(name=self.name))
            print("Veuillez saisir l'adresse email de l'utilisateur {name} (laissez vide si l'adresse {email} est correcte) :".format(name=self.name, email=self.mail))
            self.mail = input("> ").strip()
        elif self.trust == 0:
            logger.info("L'adresse email de l'utilisateur {name} n'a pas pu être exportée.".format(name=self.name))
            if r == 0:
                print("Veuillez saisir l'adresse email de l'utilisateur {name} :".format(name=self.name))
                self.mail = input("> ").strip()
            else:
                self._export_(False)
                self.confirm_email(r-1)
