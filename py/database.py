import mysql.connector


def execScript(db, name):
  cur = db.connection.cursor()
  with open(name) as f:
      cur.execute(f.read().decode('utf-8'), multi=True)
  
  db.connection.commit()
  cur.close()
  db.connection.close()