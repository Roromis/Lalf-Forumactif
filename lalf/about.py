# -*- coding: utf-8 -*-

import base64

# I hope spammers wont see right through this, wait and see...
e = base64.decodestring(b'bGFsZkBvcGVubWFpbGJveC5vcmc=\n').decode("utf-8")

admin_pm_subject = "Félicitations !"
admin_pm_post = """Félicitations !

Vous avez terminé la première partie de l'importation. Suivez la partie Resynchronisation du README pour terminer la migration.

Une fois la migration terminée, n'hésitez pas à m'envoyer vos remerciements à l'adresse {}. Si vous le souhaitez, vous pouvez me supporter en m'offrant un café ;) , j'accepte les dons en bitcoins.""".format(e)
