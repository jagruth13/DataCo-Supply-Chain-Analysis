import sqlite3
from sqlite3 import Error
import pandas as pd

def create_connection(db_file, delete_db=False):
    import os
    if delete_db and os.path.exists(db_file):
        os.remove(db_file)

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA foreign_keys = 1")
    except Error as e:
        print(e)

    return conn


db_filename = 'DataCoSupply.db'
conn = create_connection(db_filename)
rows = pd.read_sql_query('SELECT name FROM sqlite_master WHERE type=\'table\';',conn)
print(rows)
for row in rows.name.items():
    print("Table Name:"+row[1]+"\n")
    table = pd.read_sql_query("pragma table_info('{}');".format(row[1]),conn)
    print(table)
    print("\n")
