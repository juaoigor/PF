import sqlite3

dbs = 'db/database.db'


def doBackup():
    import shutil
    import calendar
    import time
    gmt = time.gmtime()
    ts = calendar.timegm(gmt)
    shutil.copyfile(dbs, '{}_{}'.format(dbs, ts))


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


def sqlExec(sql):
    db = sqlite3.connect(dbs)
    db.execute(sql)
    db.commit()
    db.close()


def InsertValues(table, flds, vals):
    sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(
        table, ", ".join(flds), ", ".join(['?'] * len(flds)))
    db = sqlite3.connect(dbs)
    db.execute(sql, vals)
    db.commit()
    db.close()


def DedaConhecidos():

    import sqlite3
    dbs = 'db/database.db'
    db = sqlite3.connect(dbs)
    # ALIMENTACAO PESSOAL
    db.execute(
        'UPDATE Despesas set id_conta = 5 where texto like "%IFOOD%DDU%"')
    db.execute(
        'UPDATE Despesas set id_conta = 5 where texto like "%SODEXO%DDU%"')
    db.execute(
        'UPDATE Despesas set id_conta = 5 where texto like "%NUTRICAR%DDU%"')
    db.execute('UPDATE Despesas set id_conta = 5 where texto like "%OLGA RI%"')
    db.execute(
        'UPDATE Despesas set id_conta = 5 where texto like "%LUGAR 166%"')
    db.execute(
        'UPDATE Despesas set id_conta = 9 where texto like "%RASCAL%DDF%"')
    db.execute(
        'UPDATE Despesas set id_conta = 9 where texto like "%SL CAFES DO%"')
    # LIVING LAZER
    db.execute(
        'UPDATE Despesas set id_conta = 9 where texto like "%IFOOD%DDF%"')
    db.execute(
        'UPDATE Despesas set id_conta = 9 where texto like "%OFNER%DDF%"')
    db.execute(
        'UPDATE Despesas set id_conta = 9 where texto like "%OFNER%DDU%"')
    db.execute(
        'UPDATE Despesas set id_conta = 9 where texto like "%TEMPERO DAS GERAIS%"'
    )
    db.execute('UPDATE Despesas set id_conta = 9 where texto like "%JOAKINS%"')
    db.execute(
        'UPDATE Despesas set id_conta = 9 where texto like "%BACIO DI LATTE%DDF%"'
    )
    db.execute(
        'UPDATE Despesas set id_conta = 9 where texto like "%PASTEL%DDF%"')
    db.execute(
        'UPDATE Despesas set id_conta = 9 where texto like "%PASTEL%DDU%"')
    db.execute(
        'UPDATE Despesas set id_conta = 9 where texto like "%CUCINA%PIZZARIA%"'
    )
    db.execute(
        'UPDATE Despesas set id_conta = 9 where texto like "%RASCAL%DDU%"')
    db.execute(
        'UPDATE Despesas set id_conta = 9 where texto like "%OURO CHOPP DDU%"')
    db.execute(
        'UPDATE Despesas set id_conta = 9 where texto like "%PAGALECRISBEBIDAS%"'
    )
    # LIVING MERCADO
    db.execute(
        'UPDATE Despesas set id_conta = 11 where texto like "%SAMS%DDF%"')
    db.execute(
        'UPDATE Despesas set id_conta = 11 where texto like "%SAMS%DDU%"')
    db.execute(
        'UPDATE Despesas set id_conta = 11 where texto like "%PAO DE ACUCAR%"')
    db.execute(
        'UPDATE Despesas set id_conta = 11 where texto like "%ST%MARCHE%"')
    db.execute(
        'UPDATE Despesas set id_conta = 11 where texto like "%CARNES%DAYT%"')
    db.execute(
        'UPDATE Despesas set id_conta = 11 where texto like "%COMPANHIA BRASILEIRA%"'
    )
    db.execute(
        'UPDATE Despesas set id_conta = 5 where texto like "%NUTRICAR%DDF%"')
    db.execute(
        'UPDATE Despesas set id_conta = 5 where texto like "%CARREFOUR%"')
    db.execute(
        'UPDATE Despesas set id_conta = 5 where texto like "%MINUTO PA%"')
    # LIVING MENSAL
    db.execute('UPDATE Despesas set id_conta = 7 where texto like "%NETFLIX%"')
    db.execute(
        'UPDATE Despesas set id_conta = 7 where texto like "%APPLE%BILL%"')
    db.execute(
        'UPDATE Despesas set id_conta = 7 where texto like "%AMAZON%PRIME%"')
    db.execute(
        'UPDATE Despesas set id_conta = 7 where texto like "%AMAZON%DIGITAL%"')
    db.execute(
        'UPDATE Despesas set id_conta = 7 where texto like "%NETSERVICOS%"')
    db.execute(
        'UPDATE Despesas set id_conta = 7 where texto like "%CLAROMVEL%"')
    db.execute(
        'UPDATE Despesas set id_conta = 7 where texto like "%ENELSPELETROP%"')
    db.execute(
        'UPDATE Despesas set id_conta = 7 where texto like "%ANUIDADE DIFERENCIAD%"'
    )
    db.execute(
        'UPDATE Despesas set id_conta = 7 where texto like "%SEGURO CARTAO%"')
    # FILHOS PRESENTES
    db.execute('UPDATE Despesas set id_conta = 16 where texto like "%PBKIDS%"')
    db.execute(
        'UPDATE Despesas set id_conta = 16 where texto like "%RI HAPPY%"')
    # SAUDE MENSAL
    db.execute('UPDATE Despesas set id_conta = 15 where texto like "%FARMA%"')
    db.execute('UPDATE Despesas set id_conta = 15 where texto like "%DROGA%"')
    db.execute(
        'UPDATE Despesas set id_conta = 15 where texto like "%DROG%PAULO%"')
    # COMPRAS CASA
    db.execute(
        'UPDATE Despesas set id_conta = 12 where texto like "%SODIMAC%"')
    db.execute(
        'UPDATE Despesas set id_conta = 12 where texto like "%WESTWING%"')
    db.execute('UPDATE Despesas set id_conta = 12 where texto like "%LEROY%"')
    db.execute(
        'UPDATE Despesas set id_conta = 12 where texto like "%FAST SHOP%"')
    db.execute(
        'UPDATE Despesas set id_conta = 12 where texto like "%GALERIA9%"')
    db.execute(
        'UPDATE Despesas set id_conta = 12 where texto like "%LEO MADEIRAS%"')
    db.execute('UPDATE Despesas set id_conta = 12 where texto like "%WW NOW%"')
    db.execute(
        'UPDATE Despesas set id_conta = 12 where texto like "%LA CASA DI M%"')
    db.execute('UPDATE Despesas set id_conta = 12 where texto like "%ELO7%"')
    db.execute('UPDATE Despesas set id_conta = 12 where texto like "%MOBLY%"')
    db.execute(
        'UPDATE Despesas set id_conta = 12 where texto like "%HOME DEC%"')
    db.execute(
        'UPDATE Despesas set id_conta = 12 where texto like "%RCHLO LOJA%"')
    db.execute(
        'UPDATE Despesas set id_conta = 12 where texto like "%BRASTEMP%"')
    db.execute(
        'UPDATE Despesas set id_conta = 12 where texto like "%MMARTAN%"')
    # TRANSPORTE MENSAK
    db.execute('UPDATE Despesas set id_conta = 4 where texto like "%UBER%"')
    db.execute(
        'UPDATE Despesas set id_conta = 4 where texto like "%ESTACIONAMENTO%"')
    db.execute('UPDATE Despesas set id_conta = 4 where texto like "%ESTAPAR%"')
    db.execute(
        'UPDATE Despesas set id_conta = 4 where texto like "%AUTO POSTO%"')
    # LIVING FERIAS
    db.execute(
        'UPDATE Despesas set id_conta = 10 where texto like "%GOL%AEREAS%"')
    db.execute(
        'UPDATE Despesas set id_conta = 10 where texto like "%TRAVEL PARTNER%"'
    )
    db.execute(
        'UPDATE Despesas set id_conta = 10 where texto like "%PATACHOCAS%"')
    db.execute(
        'UPDATE Despesas set id_conta = 10 where texto like "%WINDSOR%"')
    db.execute(
        'UPDATE Despesas set id_conta = 10 where texto like "%AEROLINEAS%"')
    db.execute(
        'UPDATE Despesas set id_conta = 10 where texto like "%AG DE TURISMO%"')
    db.execute(
        'UPDATE Despesas set id_conta = 10 where texto like "%BRITISH AIRWAYS%"'
    )
    db.execute(
        'UPDATE Despesas set id_conta = 10 where texto like "%PALACIO TANGARA%"'
    )
    db.execute(
        'UPDATE Despesas set id_conta = 10 where texto like "%BOOKING%"')
    # DEBUTO
    db.execute(
        'UPDATE Despesas set id_conta = 9999 where texto like "%DEBITO%FATURA%CARTAO%"'
    )
    db.execute(
        'UPDATE Despesas set id_conta = 9999 where texto like "%DEB%FATURA%EM%"'
    )

    db.commit()
    db.close()

    import sqlite3
    dbs = 'db/database.db'
    db = sqlite3.connect(dbs)
    db.execute(
        'UPDATE Contas set conta = "Receitas -> Salario -> Fixo" where ID = 1')
    db.execute(
        'UPDATE Contas set conta = "Receitas -> Salario -> Variavel" where ID = 2'
    )
    db.execute(
        'UPDATE Contas set conta = "Investimentos -> Renda -> Investimentos" where ID = 3'
    )
    db.commit()
    db.close()

    import sqlite3
    dbs = 'db/database.db'

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

    import datetime

    def isDateVal(s):
        try:
            date = datetime.datetime.strptime(s, '%d/%m/%y')
        except ValueError as err:
            return False
        else:
            return True

    r = sqlQuery("SELECT * FROM Despesas")
    for l in r:
        if isDateVal(l['texto'][:8]):
            dt = datetime.datetime.strptime(l['texto'][:8],
                                            '%d/%m/%y').strftime("%y-%m-%d")
            st = '{}{}'.format(dt, l['texto'][8:])
            sql = 'UPDATE Despesas set texto = "{}" where id = {}'.format(
                st, l['id'])
            sqlExec(sql)

    sql = """
  DROP TABLE IF EXISTS AutoUpdate;
  CREATE TABLE AutoUpdate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_conta INTEGER,
    texto TEXT
  );

  INSERT INTO AutoUpdate (id_conta, texto) values (5,'%IFOOD%DDU%');
  INSERT INTO AutoUpdate (id_conta, texto) values (5,'%SODEXO%DDU%');
  INSERT INTO AutoUpdate (id_conta, texto) values (5,'%NUTRICAR%DDU%');
  INSERT INTO AutoUpdate (id_conta, texto) values (5,'%OLGA RI%');
  INSERT INTO AutoUpdate (id_conta, texto) values (5,'%LUGAR 166%');
  INSERT INTO AutoUpdate (id_conta, texto) values (9,'%RASCAL%DDF%');
  INSERT INTO AutoUpdate (id_conta, texto) values (9,'%SL CAFES DO%');
  INSERT INTO AutoUpdate (id_conta, texto) values (9,'%IFOOD%DDF%');
  INSERT INTO AutoUpdate (id_conta, texto) values (9,'%OFNER%');
  INSERT INTO AutoUpdate (id_conta, texto) values (9,'%TEMPERO DAS GERAIS%');
  INSERT INTO AutoUpdate (id_conta, texto) values (9,'%JOAKINS%');
  INSERT INTO AutoUpdate (id_conta, texto) values (9,'%BACIO DI LATTE%DDF%');
  INSERT INTO AutoUpdate (id_conta, texto) values (9,'%PASTEL%DDF%');
  INSERT INTO AutoUpdate (id_conta, texto) values (9,'%PASTEL%DDU%');
  INSERT INTO AutoUpdate (id_conta, texto) values (9,'%CUCINA%PIZZARIA%');
  INSERT INTO AutoUpdate (id_conta, texto) values (9,'%RASCAL%DDU%');
  INSERT INTO AutoUpdate (id_conta, texto) values (9,'%OURO CHOPP DDU%');
  INSERT INTO AutoUpdate (id_conta, texto) values (9,'%PAGALECRISBEBIDAS%');
  INSERT INTO AutoUpdate (id_conta, texto) values (11,'%SAMS%');
  INSERT INTO AutoUpdate (id_conta, texto) values (11,'%PAO DE ACUCAR%');
  INSERT INTO AutoUpdate (id_conta, texto) values (11,'%ST%MARCHE%');
  INSERT INTO AutoUpdate (id_conta, texto) values (11,'%CARNES%DAYT%');
  INSERT INTO AutoUpdate (id_conta, texto) values (11,'%COMPANHIA BRASILEIRA%');
  INSERT INTO AutoUpdate (id_conta, texto) values (5,'%NUTRICAR%DDF%');
  INSERT INTO AutoUpdate (id_conta, texto) values (5,'%CARREFOUR%');
  INSERT INTO AutoUpdate (id_conta, texto) values (5,'%MINUTO PA%');
  INSERT INTO AutoUpdate (id_conta, texto) values (7,'%NETFLIX%');
  INSERT INTO AutoUpdate (id_conta, texto) values (7,'%APPLE%BILL%');
  INSERT INTO AutoUpdate (id_conta, texto) values (7,'%AMAZON%PRIME%');
  INSERT INTO AutoUpdate (id_conta, texto) values (7,'%AMAZON%DIGITAL%');
  INSERT INTO AutoUpdate (id_conta, texto) values (7,'%NETSERVICOS%');
  INSERT INTO AutoUpdate (id_conta, texto) values (7,'%CLAROMVEL%');
  INSERT INTO AutoUpdate (id_conta, texto) values (7,'%ENELSPELETROP%');
  INSERT INTO AutoUpdate (id_conta, texto) values (7,'%ANUIDADE DIFERENCIAD%');
  INSERT INTO AutoUpdate (id_conta, texto) values (7,'%SEGURO CARTAO%');
  INSERT INTO AutoUpdate (id_conta, texto) values (16,'%PBKIDS%');
  INSERT INTO AutoUpdate (id_conta, texto) values (16,'%RI HAPPY%');
  INSERT INTO AutoUpdate (id_conta, texto) values (15,'%FARMA%');
  INSERT INTO AutoUpdate (id_conta, texto) values (15,'%DROGA%');
  INSERT INTO AutoUpdate (id_conta, texto) values (15,'%DROG%PAULO%');
  INSERT INTO AutoUpdate (id_conta, texto) values (12,'%SODIMAC%');
  INSERT INTO AutoUpdate (id_conta, texto) values (12,'%WESTWING%');
  INSERT INTO AutoUpdate (id_conta, texto) values (12,'%LEROY%');
  INSERT INTO AutoUpdate (id_conta, texto) values (12,'%FAST SHOP%');
  INSERT INTO AutoUpdate (id_conta, texto) values (12,'%GALERIA9%');
  INSERT INTO AutoUpdate (id_conta, texto) values (12,'%LEO MADEIRAS%');
  INSERT INTO AutoUpdate (id_conta, texto) values (12,'%WW NOW%');
  INSERT INTO AutoUpdate (id_conta, texto) values (12,'%LA CASA DI M%');
  INSERT INTO AutoUpdate (id_conta, texto) values (12,'%ELO7%');
  INSERT INTO AutoUpdate (id_conta, texto) values (12,'%MOBLY%');
  INSERT INTO AutoUpdate (id_conta, texto) values (12,'%HOME DEC%');
  INSERT INTO AutoUpdate (id_conta, texto) values (12,'%RCHLO LOJA%');
  INSERT INTO AutoUpdate (id_conta, texto) values (12,'%BRASTEMP%');
  INSERT INTO AutoUpdate (id_conta, texto) values (12,'%MMARTAN%');
  INSERT INTO AutoUpdate (id_conta, texto) values (4,'%UBER%');
  INSERT INTO AutoUpdate (id_conta, texto) values (4,'%ESTACIONAMENTO%');
  INSERT INTO AutoUpdate (id_conta, texto) values (4,'%ESTAPAR%');
  INSERT INTO AutoUpdate (id_conta, texto) values (4,'%AUTO POSTO%');
  INSERT INTO AutoUpdate (id_conta, texto) values (10,'%GOL%AEREAS%');
  INSERT INTO AutoUpdate (id_conta, texto) values (10,'%TRAVEL PARTNER%');
  INSERT INTO AutoUpdate (id_conta, texto) values (10,'%PATACHOCAS%');
  INSERT INTO AutoUpdate (id_conta, texto) values (10,'%WINDSOR%');
  INSERT INTO AutoUpdate (id_conta, texto) values (10,'%AEROLINEAS%');
  INSERT INTO AutoUpdate (id_conta, texto) values (10,'%AG DE TURISMO%');
  INSERT INTO AutoUpdate (id_conta, texto) values (10,'%BRITISH AIRWAYS%');
  INSERT INTO AutoUpdate (id_conta, texto) values (10,'%PALACIO TANGARA%');
  INSERT INTO AutoUpdate (id_conta, texto) values (10,'%BOOKING%');
  INSERT INTO AutoUpdate (id_conta, texto) values (9999,'%DEBITO%FATURA%CARTAO%');
  INSERT INTO AutoUpdate (id_conta, texto) values (9999,'%DEB%FATURA%EM%');
  """

    db = sqlite3.connect(dbs)
    cursor = db.cursor()
    cursor.executescript(sql)
    db.commit()
    db.close()

    import sqlite3
    sql = 'update Despesas SET datahora = DATE(datahora, "-1 year") WHERE DATE(datahora) >= DATE("2022-12-01")'
    dbs = 'db/database.db'
    db = sqlite3.connect(dbs)
    db.execute(sql)
    db.commit()
    db.close()

    import sqlite3
    sql = 'update Despesas SET datahora = "2022-10-30" WHERE id >= 3237'
    dbs = 'db/database.db'
    db = sqlite3.connect(dbs)
    db.execute(sql)
    db.commit()
    db.close()

    import sqlite3
    sql = 'ALTER Table Contas ADD Saldo INTEGER DEFAULT 0'
    dbs = 'db/database.db'
    db = sqlite3.connect(dbs)
    db.execute(sql)
    db.commit()
    db.close()

    import sqlite3
    sql = """
    CREATE TABLE Saldos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      id_conta INTEGER,
      datahora TEXT,
      valor DOUBLE
    );"""
    dbs = 'db/database.db'
    db = sqlite3.connect(dbs)
    db.execute(sql)
    db.commit()
    db.close()
