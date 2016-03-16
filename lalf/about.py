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

import base64

e = base64.b64decode(b'bGFsZkBvcGVubWFpbGJveC5vcmc=\n').decode("utf-8")

admin_pm_subject = "Félicitations !"
admin_pm_post = """Félicitations !

Vous avez terminé la première partie de l'importation. Suivez la
partie Resynchronisation du README pour terminer la migration.

Une fois la migration terminée, n'hésitez pas à m'envoyer vos
remerciements à l'adresse {}. Si vous le souhaitez, vous pouvez me
supporter en m'offrant un café ;) , j'accepte les dons en
bitcoins.""".format(e)
