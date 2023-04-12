import sqlite3

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
    sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(
        table, ", ".join(flds), ", ".join(["?"] * len(flds))
    )
    db = sqlite3.connect(dbs)
    db.execute(sql, vals)
    db.commit()
    db.close()


# sql = """
# CREATE TABLE PBPostsTags (
#   id INTEGER PRIMARY KEY AUTOINCREMENT,
#   id_post INTEGER,
#   id_tag INTEGER
# );
# """

# import sqlite3

# dbs = "db/database.db"
# db = sqlite3.connect(dbs)
# db.execute(sql)
# db.commit()
# db.close()
