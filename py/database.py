import sqlite3

dbs = 'db/database.db'

def DataBaseReset():
  with open('sql/setup.sql', 'r') as sql_file:
    sql_script = sql_file.read()
  
  db = sqlite3.connect(dbs)
  cursor = db.cursor()
  cursor.executescript(sql_script)
  db.commit()
  db.close()

def sqlQuery(sql):
  db = sqlite3.connect(dbs)
  db.row_factory = sqlite3.Row
  c = db.cursor()
  c.execute(sql)
  res = c.fetchall()
  d = [{k: item[k] for k in item.keys()} for item in res]
  db.close()
  return d  