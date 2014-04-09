from binascii import crc32

from lalf.config import config

def escape(str):
    return str.replace("\\", "\\\\").replace("'", "''")

def email_hash(email):
	return str(crc32(email.encode("utf-8"))&0xffffffff) + str(len(email))

def insert(file, table, d):
    keys = []
    values = []
    for k,v in d.items():
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
