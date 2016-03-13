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

from binascii import crc32

from lalf.config import config

def escape(str):
    return str.replace("\\", "\\\\").replace("'", "''")

def email_hash(email):
	return str(crc32(email.encode("utf-8"))&0xffffffff) + str(len(email))

def insert(file, table, d, ignore_keys=[]):
    keys = []
    values = []
    for k,v in d.items():
        if k not in ignore_keys:
            keys.append(k)
            values.append("'"+escape(str(v))+"'")

    file.write('INSERT INTO {prefix}{table} ({keys}) VALUES ({values});\n'.format(
        prefix=config["table_prefix"],
        table=table,
        keys=", ".join(keys),
        values=", ".join(values)))

def truncate(file, table):
    file.write('TRUNCATE TABLE {prefix}{table};\n'.format(
        prefix=config["table_prefix"],
        table=table))
