import sqlite3

db = 'db\database.db'

def DataBaseReset():
  db = sqlite3.connect(db)
  cursor = db.cursor()
  cursor.executescript('sql/setup.sql')
  db.commit()
  db.close()
  