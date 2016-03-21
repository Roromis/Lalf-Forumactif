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
Module handling the writing of the sql dump file
"""

def escape(string):
    """
    Escapes special characters in a string for use in an SQL statement
    """
    return string.replace("\\", "\\\\").replace("'", "''")

class SqlFile(object):
    """
    Object used to save sql queries in an sql file

    Attrs:
        path (str): The path of the sql dump file
        prefix (str): A prefix that will be added before the table names

    Example:
        >>> with SqlFile("phpbb.sql", "phpbb_"):
        ...     sqlfile.truncate("posts")
        ...     sqlfile.insert("posts", {
        ...         "post_id": 1,
        ...         "post_subject": "Subject",
        ...         # ...
        ...     })
    """
    def __init__(self, path, prefix=""):
        self.fileobj = open(path, "w")
        self.prefix = prefix

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.fileobj.close()

    def insert(self, table, entry):
        """
        Add an insert statement to the dump file

        Attrs:
            table (str):
            entry (dict): Dictionnary associating column names to their values
        """
        columns = []
        values = []
        for column, value in entry.items():
            columns.append(column)
            values.append("'{}'".format(escape(str(value))))

        self.fileobj.write('INSERT INTO {prefix}{table} ({columns}) VALUES ({values});\n'.format(
            prefix=self.prefix,
            table=table,
            columns=", ".join(columns),
            values=", ".join(values)))

    def truncate(self, table):
        """
        Add truncate statement to the dump file
        """
        self.fileobj.write('TRUNCATE TABLE {prefix}{table};\n'.format(
            prefix=self.prefix,
            table=table))
