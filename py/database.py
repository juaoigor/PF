import sqlite3
import traceback
import sys

dbs = "db/database.db"


def doBackup():
  import shutil
  import calendar
  import time

  gmt = time.gmtime()
  ts = calendar.timegm(gmt)
  shutil.copyfile(dbs, "{}_{}".format(dbs, ts))


def DataBaseReset():
  with open("sql/setup.sql", "r") as sql_file:
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


def sqlExec(sql):
  db = sqlite3.connect(dbs)
  db.execute(sql)
  db.commit()
  db.close()


def InsertValues(table, flds, vals):
  try:
    sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(
      table, ", ".join(flds), ", ".join(["?"] * len(flds)))
    print(sql)
    db = sqlite3.connect(dbs)
    db.execute(sql, vals)
    db.commit()
    db.close()
  except sqlite3.Error as er:
    print('SQLite error: %s' % (' '.join(er.args)))
    print("Exception class is: ", er.__class__)
    print('SQLite traceback: ')
    exc_type, exc_value, exc_tb = sys.exc_info()
    print(traceback.format_exception(exc_type, exc_value, exc_tb))


def getParam(param, valdef):
  r = sqlQuery("SELECT * FROM Parametros WHERE param = '{}'".format(param))
  if len(r) == 0:
    return valdef
  else:
    return r[0]['val']


# sql1 = """
# DROP TABLE IF EXISTS Parametros;
# """

# sql2 = """
# CREATE TABLE Parametros (
#   id INTEGER PRIMARY KEY AUTOINCREMENT,
#   param TEXT,
#   val TEXT
# );

# """

# import sqlite3

# dbs = "db/database.db"
# db = sqlite3.connect(dbs)
# db.execute(sql1)
# db.execute(sql2)
# db.commit()
# db.close()
