from flask import render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask import Flask

import sys
import traceback
import logging
import random
import os
import json

from datetime import datetime
from dateutil.relativedelta import relativedelta

sys.path.insert(0, "/home/juaoigor/pf")
sys.path.insert(0, "/home/juaoigor/pf/py")
sys.path.insert(0, "/home/runner/PF")
sys.path.insert(0, "/home/runner/PF/py")
sys.path.insert(0, r"C:\dev\Projects\Python\Pessoal\py")

from database import sqlQuery, sqlExec, InsertValues

app = Flask(__name__)
app.secret_key = "financas"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.abspath(os.getcwd()),
                                           "upload")
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/")
@app.route("/index.html")
def index():
  if "loggedin" in session:
    return render_template("index.html")
  return redirect(url_for("login"))


@app.route("/login/", methods=["GET", "POST"])
def login():
  if request.method == "POST":
    if (request.form["username"] == "juaoigor"
        and request.form["password"] == "site"):
      session["loggedin"] = True
      return render_template("index.html")
    else:
      return render_template("login.html")
  else:
    return render_template("login.html")


@app.route("/config/autoupdate", methods=["GET", "POST"])
def configAutoupdate():
  from database import sqlQuery, sqlExec, InsertValues

  modo = "I"

  eid = 0
  rs = ""
  if request.method == "GET":
    if request.args.get("mode") == "edit":
      modo = "E"
      eid = request.args.get("id")
      rs = sqlQuery("SELECT * FROM autoupdate WHERE id = {}".format(eid))[0]
    elif request.args.get("exec") == "1":
      r = sqlQuery("SELECT * FROM AutoUpdate")
      for l in r:
        sql = 'UPDATE Despesas set id_conta = {} WHERE texto like "{}" and texto not like "%EDITADO%"'.format(
          l["id_conta"], l["texto"])
        sqlExec(sql)
  elif request.method == "POST" and "Inserir" in request.form:
    InsertValues(
      "autoupdate",
      ["texto", "id_conta"],
      [request.form["texto"], request.form["conta"]],
    )
  elif request.method == "POST" and "Update" in request.form:
    sql = "UPDATE autoupdate set texto = '{}', id_conta = {} where id = {}".format(
      request.form["texto"], request.form["conta"], request.form["id"])
    sqlExec(sql)
  elif request.method == "POST" and "Apagar" in request.form:
    sql = "DELETE FROM autoupdate WHERE id = {}".format(request.form["id"])
    sqlExec(sql)
  labels = sqlQuery(
    "SELECT id, conta from Contas WHERE Saldo = 0 ORDER BY conta")

  tb = sqlQuery(
    "SELECT t1.id, t1.texto, t1.id_conta, t2.conta FROM autoupdate t1, contas t2 where t1.id_conta = t2.id order by conta, texto"
  )
  return render_template("config.autoupdate.html",
                         labels=labels,
                         modo=modo,
                         tb=tb,
                         rs=rs)


@app.route("/config/contas", methods=["GET", "POST"])
def configContas():
  try:
    from database import sqlQuery, sqlExec, InsertValues

    modo = "I"

    eid = 0
    rs = ""
    if request.method == "GET":
      if request.args.get("mode") == "edit":
        modo = "E"
        eid = request.args.get("id")
        rs = sqlQuery("SELECT * FROM Contas WHERE id = {}".format(eid))[0]
    elif request.method == "POST" and "Criar" in request.form:
      if request.form["Criar"] == "Criar":
        InsertValues(
          "Contas",
          ["conta", "recdes", "fixvar", "inv", "saldo", "Antigas"],
          [
            request.form["conta"], request.form["RecDes"],
            request.form["FixVar"], request.form["Invest"],
            request.form["Saldo"], request.form["Antigas"]
          ],
        )
    elif request.method == "POST" and "Update" in request.form:
      sql = "UPDATE Contas set Conta = '{}', RecDes = {}, FixVar = {}, Inv = {}, Saldo = {}, Antigas = {} where id = {}".format(
        request.form["conta"], request.form["RecDes"], request.form["FixVar"],
        request.form["Invest"], request.form["Saldo"], request.form["Antigas"],
        request.form["id"])
      sqlExec(sql)
    from database import sqlQuery

    tb = sqlQuery("SELECT * FROM Contas ORDER BY conta")
    return render_template("config.contas.html", modo=modo, tb=tb, rs=rs)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/config/debug", methods=["GET", "POST"])
def configDebug():
  info = {}

  import os

  info["FOLDER"] = os.getcwd()
  return render_template("config.debug.html", info=info)


@app.route("/config/parametros", methods=["GET", "POST"])
def configParametros():
  try:
    from database import sqlQuery, sqlExec, InsertValues
    modo = "I"
    eid = 0
    rs = ""
    if request.method == "POST":
      print(request.form)

    if request.method == "GET":
      if request.args.get("mode") == "edit":
        modo = "E"
        eid = request.args.get("id")
        rs = sqlQuery("SELECT * FROM Parametros WHERE id = {}".format(eid))[0]
    elif request.method == "POST" and "Criar" in request.form:
      if request.form["Criar"] == "Criar":
        InsertValues("Parametros", ["param", "val"],
                     [request.form["param"], request.form["val"]])
    elif request.method == "POST" and "Update" in request.form:
      sql = "UPDATE Parametros set param = '{}', val = '{}' where id = {}".format(
        request.form["param"], request.form["val"], request.form["id"])
      sqlExec(sql)
    tb = sqlQuery("SELECT * FROM Parametros order by Param")
    return render_template("config.parametros.html", modo=modo, tb=tb, rs=rs)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/config/riscos", methods=["GET", "POST"])
def configRiscos():
  try:
    from database import sqlQuery, sqlExec, InsertValues
    modo = "I"
    eid = 0
    rs = ""
    if request.method == "POST":
      print(request.form)

    if request.method == "GET":
      if request.args.get("mode") == "edit":
        modo = "E"
        eid = request.args.get("id")
        rs = sqlQuery("SELECT * FROM Riscos WHERE id = {}".format(eid))[0]
    elif request.method == "POST" and "Criar" in request.form:
      if request.form["Criar"] == "Criar":
        InsertValues("Riscos", ["risco", "categ"],
                     [request.form["risco"], request.form["categoria"]])
    elif request.method == "POST" and "Update" in request.form:
      sql = "UPDATE Riscos set risco = '{}', categ = '{}' where id = {}".format(
        request.form["risco"], request.form["categoria"], request.form["id"])
      sqlExec(sql)
    tb = sqlQuery("SELECT * FROM Riscos order by Categ, Risco")
    return render_template("config.riscos.html", modo=modo, tb=tb, rs=rs)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/config/setup", methods=["GET", "POST"])
def configSetup():
  if request.method == "POST":
    if request.form["Setup"] == "Setup":
      from database import DataBaseReset

      DataBaseReset()
  if request.method == "GET":
    if request.args.get("train") != None:
      if request.args.get("train") == "1":
        from fUtils import LabelTrain

        LabelTrain()
    if request.args.get("backup") != None:
      if request.args.get("backup") == "1":
        from database import doBackup

        doBackup()
  return render_template("config.setup.html")


@app.route("/config/sql", methods=["GET", "POST"])
def configSQL():
  try:
    rs = []
    modo = "n"
    from database import sqlQuery, sqlExec, InsertValues
    if request.method == "POST":
      if request.method == "POST" and "Query" in request.form:
        if request.form["Query"] == "Query":
          rs = sqlQuery(request.form["texto"])
          modo = "q"
      elif request.method == "POST" and "Executar" in request.form:
        if request.form["Executar"] == "Executar":
          rs = sqlExec(request.form["texto"])

    return render_template("config.sql.html", rs=rs, modo=modo)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/config/taxas", methods=["GET", "POST"])
def configTaxas():
  try:
    from database import sqlQuery, sqlExec, InsertValues
    modo = "I"
    eid = 0
    rs = ""
    if request.method == "POST":
      print(request.form)

    if request.method == "GET":
      if request.args.get("mode") == "edit":
        modo = "E"
        eid = request.args.get("id")
        rs = sqlQuery("SELECT * FROM Taxas WHERE id = {}".format(eid))[0]
    elif request.method == "POST" and "Criar" in request.form:
      if request.form["Criar"] == "Criar":
        InsertValues("Taxas", ["datahora", "indice", "valor"], [
          request.form["data"], request.form["indice"], request.form["valor"]
        ])
    elif request.method == "POST" and "Update" in request.form:
      sql = "UPDATE Taxas set datahora = '{}', indice = '{}', valor = {} where id = {}".format(
        request.form["data"], request.form["indice"], request.form["valor"],
        request.form["id"])
      sqlExec(sql)
    tb = sqlQuery("SELECT * FROM Taxas ORDER BY datahora, indice")
    return render_template("config.taxas.html", modo=modo, tb=tb, rs=rs)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/config/transfers", methods=["GET", "POST"])
def configTransfers():
  try:
    from database import sqlQuery, sqlExec, InsertValues
    modo = "I"
    eid = 0
    rs = ""
    if request.method == "GET":
      if request.args.get("mode") == "edit":
        modo = "E"
        eid = request.args.get("id")
        rs = sqlQuery("SELECT * FROM Transfers WHERE id = {}".format(eid))[0]
    elif request.method == "POST" and "Criar" in request.form:
      if request.form["Criar"] == "Criar":
        InsertValues("Transfers",
                     ["id_conta_de", "id_conta_para", "dia", "texto"], [
                       request.form["conta_de"],
                       request.form["conta_para"],
                       request.form["dia"],
                       request.form["texto"],
                     ])
    elif request.method == "POST" and "Update" in request.form:
      sql = "UPDATE Transfers set id_conta_de = '{}', id_conta_para = {}, dia = {}, texto = '{}' where id = {}".format(
        request.form["conta_de"], request.form["conta_para"],
        request.form["dia"], request.form["texto"], request.form["id"])
      sqlExec(sql)
    labels = sqlQuery(
      "SELECT id, conta from Contas WHERE Saldo = 0 ORDER BY conta")
    contas = {}
    for l in labels:
      contas[l["id"]] = l["Conta"]
    tb = sqlQuery("SELECT * FROM Transfers ORDER BY texto")
    return render_template("config.transfers.html",
                           modo=modo,
                           tb=tb,
                           contas=contas,
                           labels=labels,
                           rs=rs)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/despesas/classificar", methods=["GET", "POST"])
def despesasClassificar():
  sqlFilt = "SELECT * FROM Despesas WHERE id_conta = 0 ORDER BY datahora, abs(valor) desc LIMIT 50"
  if request.method == "POST" and "Salvar" in request.form:
    if request.form["Salvar"] == "Salvar":
      from database import sqlExec

      for i in range(0, 999):
        if "{}_ID".format(i) in request.form:
          if int(request.form["{}_Conta".format(i)]) > 0:
            sql = "UPDATE Despesas SET id_conta = {} WHERE id = {}".format(
              request.form["{}_Conta".format(i)],
              request.form["{}_ID".format(i)],
            )
            sqlExec(sql)
      return redirect(url_for("despesasResumo"))
  elif request.method == "GET":
    if request.args.get("Filtrar") != None:
      if request.args.get("Filtrar") == "Filtrar":
        if request.args.get("texto") != "":
          if request.args.get("todos") != None:
            sqlFilt = "SELECT * FROM Despesas WHERE texto like '%{}%' ORDER BY datahora, abs(valor) desc LIMIT 1000".format(
              request.args.get("texto"))
          else:
            sqlFilt = "SELECT * FROM Despesas WHERE id_conta = 0 and texto like '%{}%' ORDER BY datahora, abs(valor) desc LIMIT 1000".format(
              request.args.get("texto"))
  from database import sqlQuery

  tb = sqlQuery(sqlFilt)
  labels = sqlQuery(
    "SELECT id, conta from Contas WHERE Saldo = 0 ORDER BY Inv, RecDes, conta")
  return render_template("despesas.classificar.html", tb=tb, labels=labels)


@app.route("/despesas/classnlp", methods=["GET", "POST"])
def despesasClassNLP():
  if request.method == "POST":
    if request.form["Update"] == "Update":
      for i in range(0, 999):
        if "c_{}".format(i) in request.form:
          if int(request.form["c_{}".format(i)]) != 0:
            sql = "UPDATE Despesas set id_conta = {} WHERE id = {}".format(
              request.form["c_{}".format(i)],
              request.form["id_{}".format(i)],
            )
            from database import sqlExec

            sqlExec(sql)
  from fUtils import getProbLabelBulk

  tb = getProbLabelBulk()

  return render_template("despesas.classnlp.html", tb=tb)


@app.route("/despesas/classnlpcat", methods=["GET", "POST"])
def despesasClassNLPCat():
  if request.method == "POST":
    if request.form["Update"] == "Update":
      from database import sqlQuery, sqlExec

      sql = 'SELECT id from Contas where Conta = "{}"'.format(
        request.form["conta"])
      id_conta = sqlQuery(sql)[0]["id"]
      for i in range(0, 999):
        if "check_{}".format(i) in request.form:
          sql = "UPDATE Despesas set id_conta = {} WHERE id = {}".format(
            id_conta, request.form["id_{}".format(i)])
          sqlExec(sql)
  from fUtils import getProbLabelBulkCat

  tb = getProbLabelBulkCat()

  return render_template("despesas.classnlpcat.html", tb=tb)


@app.route("/despesas/crescimento", methods=["GET", "POST"])
def despesasCrescimento():
  try:
    mes = (datetime.now() + relativedelta(months=-0)).month
    ano = (datetime.now() + relativedelta(months=-0)).year

    conta = 'Despesas'
    if request.method == "POST":
      conta = request.form["conta"]

    from JP_Despesas import geraRelatorioCrescimento
    res, contas, anual = geraRelatorioCrescimento(conta, mes, ano)
    print(anual)

    return render_template("despesas.crescimento.html",
                           res=res,
                           contas=contas,
                           conta=conta,
                           anual=anual)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/despesas/duplicados", methods=["GET", "POST"])
def despesasDuplicados():
  try:
    if request.method == "GET":
      if request.args.get("modo") != None:
        nid = int(request.args.get("id"))
        nmodo = request.args.get("modo")
        if nmodo == 'remover':
          sql = "DELETE FROM Despesas WHERE id = {}".format(nid)
          sqlExec(sql)
    from JP_Despesas import getDuplicates
    tb_dt, tb_sdt = getDuplicates()

    return render_template("despesas.duplicados.html",
                           tb_dt=tb_dt,
                           tb_sdt=tb_sdt)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/despesas/editar", methods=["GET", "POST"])
def despesasEditar():
  eid = 0
  backto = ""
  if request.method == "GET":
    eid = request.args.get("id")
    backto = request.args.get("backto")
  elif request.method == "POST":
    from database import sqlExec

    if "Apagar" in request.form:
      sql = "DELETE FROM Despesas WHERE ID = {}".format(request.form["id"])
      sqlExec(sql)
      return redirect(url_for(request.form["backTo"]))
    elif "Editar" in request.form:
      sql = 'UPDATE Despesas set datahora = "{}", id_conta = {}, texto = "{}", valor = {} WHERE ID = {}'.format(
        request.form["datahora"],
        request.form["conta"],
        request.form["texto"],
        request.form["valor"],
        request.form["id"],
      )
      sqlExec(sql)
      return redirect(url_for(request.form["backTo"]))
  from database import sqlQuery

  sql = 'SELECT * from Despesas where id = "{}"'.format(eid)
  rs = sqlQuery(sql)[0]

  labels = sqlQuery(
    "SELECT id, conta from Contas WHERE Saldo = 0 ORDER BY conta")

  return render_template("despesas.editar.html",
                         rs=rs,
                         backto=backto,
                         labels=labels)


@app.route("/despesas/transfer", methods=["GET", "POST"])
def despesasTransfer():
  eid = 0
  backto = ""
  if request.method == "GET":
    eid = request.args.get("id")
    backto = request.args.get("backto")
  elif request.method == "POST":
    from database import InsertValues
    eid = request.form["id"]
    if "Transferir" in request.form:
      InsertValues("Despesas", [
        "id_conta", "id_cartao", "id_bem", "id_pessoa", "datahora", "texto",
        "valor"
      ], [
        request.form["conta"], 1, 1, 1, request.form["datahora"],
        "{} (TRANSF: {})".format(request.form["texto"], request.form["obs"]),
        "{}".format(-1 * float(request.form["valor"]))
      ])
      InsertValues("Despesas", [
        "id_conta", "id_cartao", "id_bem", "id_pessoa", "datahora", "texto",
        "valor"
      ], [
        request.form["contaDestino"], 1, 1, 1, request.form["datahora"],
        "{} (TRANSF: {})".format(request.form["texto"], request.form["obs"]),
        "{}".format(float(request.form["valor"]))
      ])
      return redirect(url_for(request.form["backTo"]))

  from database import sqlQuery
  sql = 'SELECT * from Despesas where id = "{}"'.format(eid)
  rs = sqlQuery(sql)[0]
  labels = sqlQuery(
    "SELECT id, conta from Contas WHERE Saldo = 0 ORDER BY conta")

  return render_template("despesas.transfer.html",
                         rs=rs,
                         backto=backto,
                         labels=labels)


@app.route("/despesas/editarcontames", methods=["GET", "POST"])
def despesasEditarContaMes():
  mes = 0
  ano = 0
  conta = 0
  if request.method == "GET":
    mes = int(request.args.get("mes"))
    ano = int(request.args.get("ano"))
    conta = int(request.args.get("conta"))
  elif request.method == "POST":
    if request.form["Update"] == "Update":
      from database import sqlExec

      for i in range(0, 999):
        if "id_{}".format(i) in request.form:
          sql = 'UPDATE Despesas set id_conta = {}, texto = "{}" where id = {}'.format(
            request.form["conta_{}".format(i)],
            request.form["texto_{}".format(i)],
            request.form["id_{}".format(i)],
          )
          sqlExec(sql)
      return redirect(url_for("relatorio"))
  from database import sqlQuery

  labels = sqlQuery(
    "SELECT id, conta from Contas WHERE Saldo = 0 ORDER BY conta")

  # mes, ano, conta = 5, 2023, 52
  r = sqlQuery(
    "SELECT t1.id, t1.datahora, t1.texto, t1.id_conta, t1.valor FROM Despesas t1 where cast(strftime('%Y', t1.datahora) as integer) = {} and cast(strftime('%m', t1.datahora) as integer) = {} and t1.id_conta = {} order by t1.datahora, t1.texto"
    .format(ano, mes, conta))
  tot = 0
  for i in range(0, len(r)):
    tot = tot + r[i]['valor']
    r[i]['tot'] = tot

  return render_template("despesas.editarcontames.html",
                         tb=r,
                         labels=labels,
                         id_conta=conta)


@app.route("/despesas/ignorados", methods=["GET", "POST"])
def despesasIgnorados():
  from database import sqlQuery

  r = sqlQuery(
    "SELECT * FROM Despesas t1 where t1.id_conta = 9999 order by t1.datahora")
  return render_template("despesas.ignorados.html", tb=r)


@app.route("/despesas/importar", methods=["GET", "POST"])
def despesasImportar():
  try:
    if request.method == "POST" and "Processar" in request.form:
      if request.form["Processar"] == "Processar":
        from fUtils import despProcessarTexto

        r = despProcessarTexto(request.form["texto"])
        return render_template("despesas.importar.html", tb=r)
    if request.method == "POST" and "Inserir" in request.form:
      if request.form["Inserir"] == "Inserir":
        from database import InsertValues, sqlExec, sqlQuery
        from fUtils import str2date, date2str
        for i in range(0, 999):
          if "{}_Data".format(i) in request.form:
            if "{}_Inserir".format(i) in request.form:
              if request.form["{}_Inserir".format(i)] == 'on':
                InsertValues(
                  "Despesas",
                  [
                    "id_conta", "id_cartao", "id_bem", "id_pessoa", "datahora",
                    "texto", "valor"
                  ],
                  [
                    0,
                    1,
                    1,
                    1,
                    date2str(
                      str2date(request.form["{}_Data".format(i)], "%d/%m/%Y"),
                      "%Y-%m-%d",
                    ),
                    request.form["{}_Texto".format(i)],
                    request.form["{}_Valor".format(i)],
                  ],
                )
        r = sqlQuery("SELECT * FROM AutoUpdate")
        for l in r:
          sql = 'UPDATE Despesas set id_conta = {} WHERE id_conta = 0 and texto like "{}" and texto not like "%EDITADO%"'.format(
            l["id_conta"], l["texto"])
          sqlExec(sql)
        return redirect(url_for("despesasResumo"))
    else:
      return render_template("despesas.importar.html")
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/despesas/nlp", methods=["GET", "POST"])
def despesasNLP():
  from database import sqlQuery

  nid = 0
  if request.method == "GET":
    if request.args.get("id") != None:
      nid = int(request.args.get("id"))
  if nid == 0:
    nid = sqlQuery(
      "SELECT id from Despesas WHERE id_conta = 0 order by id")[0]["id"]
  linfo = sqlQuery("SELECT * from Despesas WHERE id = {}".format(nid))[0]
  lprox = sqlQuery(
    "SELECT id from Despesas WHERE id_conta = 0 and id > {} order by id".
    format(nid))[0]
  from fUtils import getProbLabel

  tb = getProbLabel(nid)
  return render_template("despesas.nlp.html", tb=tb, linfo=linfo, lprox=lprox)


@app.route("/despesas/resumo", methods=["GET", "POST"])
def despesasResumo():
  from database import sqlQuery, sqlExec, InsertValues

  mes = (datetime.now() + relativedelta(months=-1)).month
  ano = (datetime.now() + relativedelta(months=-1)).year

  if request.method == "GET":
    if request.args.get("mes") is not None:
      mes = int(request.args.get("mes"))
    if request.args.get("ano") is not None:
      ano = int(request.args.get("ano"))
  if request.method == "POST" and "Update" in request.form:
    if request.form["Update"] == "Update":
      mes = int(request.form["mes"])
      ano = int(request.form["ano"])

      for i in range(0, 999):
        if "id_{}".format(i) in request.form:
          if int(request.form["conta_{}".format(i)]) != 0:
            sql = "UPDATE Despesas set id_conta = {} WHERE id = {}".format(
              request.form["conta_{}".format(i)],
              request.form["id_{}".format(i)],
            )
            sqlExec(sql)
      return redirect(url_for("despesasResumo", mes=mes, ano=ano))
  if request.method == "POST" and "Transfer" in request.form:
    if request.form["Transfer"] == "Transfer":
      mes = int(request.form["mes"])
      ano = int(request.form["ano"])

      InsertValues("Despesas", [
        "id_conta", "id_cartao", "id_bem", "id_pessoa", "id_transfer",
        "datahora", "texto", "valor"
      ], [
        request.form["contaOrigem"], 1, 1, 1, request.form["id_transfer"],
        request.form["data"], "(TRANSFER) {}".format(request.form["texto"]),
        "{}".format(float(request.form["valor"]) * -1)
      ])
      InsertValues("Despesas", [
        "id_conta", "id_cartao", "id_bem", "id_pessoa", "id_transfer",
        "datahora", "texto", "valor"
      ], [
        request.form["contaDestino"], 1, 1, 1, request.form["id_transfer"],
        request.form["data"], "(TRANSFER) {}".format(
          request.form["texto"]), "{}".format(float(request.form["valor"]))
      ])

      return redirect(url_for("despesasResumo", mes=mes, ano=ano))
  labels = sqlQuery(
    "SELECT id, conta from Contas WHERE Saldo = 0 ORDER BY conta")
  pessoas = sqlQuery("SELECT id, nome from Pessoas ORDER BY Nome")
  bens = sqlQuery("SELECT id, nome from Bens ORDER BY Nome")

  contas = {}
  for l in labels:
    contas[l["id"]] = l["Conta"]
  transfers = sqlQuery(
    "SELECT * from Transfers t1 WHERE  0 = (SELECT Count(*) FROM Despesas t2 WHERE t1.id = t2.id_transfer AND cast(strftime('%Y', t2.datahora) as integer) = {} and cast(strftime('%m', t2.datahora) as integer) = {}) ORDER BY t1.texto"
    .format(ano, mes))

  ant = datetime(int(ano), int(mes), 1) + relativedelta(months=-1)
  anta = datetime(int(ano), int(mes), 1) + relativedelta(months=-12)
  anta6 = datetime(int(ano), int(mes), 1) + relativedelta(months=-6)
  pos = datetime(int(ano), int(mes), 1) + relativedelta(months=1)
  posa = datetime(int(ano), int(mes), 1) + relativedelta(months=12)
  posa6 = datetime(int(ano), int(mes), 1) + relativedelta(months=6)
  links = {
    "ant": r"/despesas/resumo?mes={}&ano={}".format(ant.month, ant.year),
    "pos": r"/despesas/resumo?mes={}&ano={}".format(pos.month, pos.year),
    "anta": r"/despesas/resumo?mes={}&ano={}".format(anta.month, anta.year),
    "posa": r"/despesas/resumo?mes={}&ano={}".format(posa.month, posa.year),
    "anta6": r"/despesas/resumo?mes={}&ano={}".format(anta6.month, anta6.year),
    "posa6": r"/despesas/resumo?mes={}&ano={}".format(posa6.month, posa6.year),
    "atual": r"/despesas/resumo",
  }

  from fUtils import MontaTabelaResumo

  return render_template(
    "despesas.resumo.html",
    labels=labels,
    pessoas=pessoas,
    bens=bens,
    links=links,
    transfers=transfers,
    contas=contas,
    tb=MontaTabelaResumo(mes, ano),
    ano=ano,
    mes=str(mes).zfill(2),
  )


@app.route("/despesas/resumoconta", methods=["GET", "POST"])
def despesasResumoconta():
  from database import sqlQuery, sqlExec

  if request.method == "POST" and "Salvar" in request.form:
    if request.form["Salvar"] == "Salvar":
      for i in range(0, 999):
        if "{}_ID".format(i) in request.form:
          if int(request.form["{}_Conta".format(i)]) > 0:
            sql = 'UPDATE Despesas SET id_conta = {}, texto = "{}" WHERE id = {}'.format(
              request.form["{}_Conta".format(i)],
              request.form["{}_texto".format(i)],
              request.form["{}_ID".format(i)],
            )
            sqlExec(sql)
      return redirect(url_for("relatorio"))
  conta = 0
  if request.method == "GET":
    if request.args.get("conta") is not None:
      conta = int(request.args.get("conta"))
  labels = sqlQuery(
    "SELECT id, conta from Contas WHERE Saldo = 0 ORDER BY conta")
  tb = sqlQuery(
    "SELECT * from Despesas WHERE id_conta = {} order by datahora".format(
      conta))
  return render_template("despesas.resumoconta.html", tb=tb, labels=labels)


@app.route("/investimentos/bonds", methods=["GET", "POST"])
def investimentosBonds():
  try:
    from database import sqlQuery, sqlExec, InsertValues
    modo = "I"
    eid = 0
    rs = ""
    if request.method == "POST":
      print(request.form)

    if request.method == "GET":
      if request.args.get("mode") == "edit":
        modo = "E"
        eid = request.args.get("id")
        rs = sqlQuery("SELECT * FROM Bonds WHERE id = {}".format(eid))[0]
    elif request.method == "POST" and "Criar" in request.form:
      if request.form["Criar"] == "Criar":
        InsertValues("Bonds", ["bond", "startdate", "startindex"], [
          request.form["bond"], request.form["startdate"],
          request.form["startindex"]
        ])
    elif request.method == "POST" and "Update" in request.form:
      sql = "UPDATE Bonds set bond = '{}', startdate = '{}', startindex = {} where id = {}".format(
        request.form["bond"], request.form["startdate"],
        request.form["startindex"], request.form["id"])
      sqlExec(sql)
    tb = sqlQuery("SELECT * FROM Bonds ORDER BY Bond, StartDate")

    return render_template("investimentos.bonds.html", modo=modo, tb=tb, rs=rs)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/investimentos/bondsflows", methods=["GET", "POST"])
def investimentosBondsFlows():
  try:
    from database import sqlQuery, sqlExec, InsertValues
    modo = "I"
    eid = 0
    rs = ""
    if request.method == "POST":
      print(request.form)

    if request.method == "GET":
      if request.args.get("mode") == "edit":
        modo = "E"
        eid = request.args.get("id")
        rs = sqlQuery("SELECT * FROM BondsFlows WHERE id = {}".format(eid))[0]
    elif request.method == "POST" and "Criar" in request.form:
      if request.form["Criar"] == "Criar":
        InsertValues("BondsFlows",
                     ["idbond", "data", "tipo", "yield", "yieldper", "amtz"], [
                       request.form["bond"], request.form["data"],
                       request.form["tipo"], request.form["yield"],
                       request.form["yieldper"], request.form["amtz"]
                     ])
    elif request.method == "POST" and "Update" in request.form:
      sql = "UPDATE BondsFlows set idbond = {}, data = '{}', tipo = '{}', yield = {}, yieldper = {}, amtz = {} where id = {}".format(
        request.form["bond"], request.form["data"], request.form["tipo"],
        request.form["yield"], request.form["yieldper"], request.form["amtz"],
        request.form["id"])
      sqlExec(sql)
    elif request.method == "POST" and "Bulk" in request.form:
      for l in request.form["Obs"].split("#"):
        r = l.split(";")
        if len(r) == 6:
          InsertValues("BondsFlows",
                       ["idbond", "data", "tipo", "yield", "yieldper", "amtz"],
                       [r[0], r[1], r[2], r[3], r[4], r[5]])

    tb = sqlQuery(
      "SELECT t1.*, t2.bond FROM BondsFlows t1, Bonds t2 where t1.idbond = t2.id ORDER BY t2.Bond, t1.data, t1.tipo"
    )
    bonds = sqlQuery("SELECT * FROM Bonds ORDER BY Bond, StartDate")
    return render_template("investimentos.bondsflows.html",
                           modo=modo,
                           tb=tb,
                           rs=rs,
                           bonds=bonds)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/investimentos/carteira", methods=["GET", "POST"])
def investimentosCarteira():
  try:
    from database import sqlQuery, sqlExec, InsertValues
    modo = "I"
    eid = 0
    rs = ""
    tb1 = []
    if request.method == "POST":
      print(request.form)

    if request.method == "GET":
      if request.args.get("mode") == "edit":
        modo = "E"
        eid = request.args.get("id")
        rs = sqlQuery(
          "SELECT * FROM BondsCarteira WHERE id = {}".format(eid))[0]
      elif request.args.get("mode") == "view":
        modo = "V"
        eid = request.args.get("id")
        from JP_Invest import GeraRelatorioFC
        tb1 = GeraRelatorioFC(eid)

    elif request.method == "POST" and "Criar" in request.form:
      if request.form["Criar"] == "Criar":
        InsertValues("BondsCarteira", ["idbond", "data", "qtde", "cx"], [
          request.form["bond"], request.form["date"], request.form["qtde"],
          request.form["cx"]
        ])
    elif request.method == "POST" and "Update" in request.form:
      sql = "UPDATE BondsCarteira set idbond = {}, data = '{}', qtde = {}, cx = {} where id = {}".format(
        request.form["bond"], request.form["date"], request.form["qtde"],
        request.form["cx"], request.form["id"])
      sqlExec(sql)
    tb = sqlQuery(
      "SELECT t1.*, t2.bond FROM BondsCarteira t1, Bonds t2 where t1.idbond = t2.id ORDER BY t1.data, t2.Bond"
    )
    bonds = sqlQuery("SELECT * FROM Bonds ORDER BY Bond, StartDate")

    tb_res = sqlQuery(
      "SELECT t2.bond, SUM(t1.qtde) AS qtde FROM BondsCarteira t1, Bonds t2 where t1.idbond = t2.id GROUP BY t2.bond HAVING SUM(t1.qtde) <> 0  ORDER BY t2.bond"
    )

    return render_template("investimentos.carteira.html",
                           modo=modo,
                           tb=tb,
                           rs=rs,
                           bonds=bonds,
                           tb1=tb1,
                           tb_res=tb_res)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/investimentos/saldos", methods=["GET", "POST"])
def investimentosSaldos():
  try:
    from database import sqlQuery, InsertValues, sqlExec

    mes = (datetime.now() + relativedelta(months=-1)).month
    ano = (datetime.now() + relativedelta(months=-1)).year

    if request.method == "GET":
      if request.args.get("mes") is not None:
        mes = int(request.args.get("mes"))
      if request.args.get("ano") is not None:
        ano = int(request.args.get("ano"))
    if request.method == "POST" and "Update" in request.form:
      if request.form["Update"] == "Update":
        mes = int(request.form["mes"])
        ano = int(request.form["ano"])
        for i in range(0, 999):
          if "{}_ID_CONTA".format(i) in request.form:
            if int(request.form["{}_ID_CONTA".format(i)]) > 0:
              if str(request.form["{}_VALOR".format(i)]) != "":
                if str(request.form["{}_ID_SALDO".format(i)]) == "":
                  InsertValues(
                    "Saldos",
                    ["id_conta", "datahora", "valor"],
                    [
                      request.form["{}_ID_CONTA".format(i)],
                      request.form["{}_DATA".format(i)],
                      str(request.form["{}_VALOR".format(i)]).replace(",", ""),
                    ],
                  )
                else:
                  sql = "UPDATE Saldos SET Valor = {} WHERE id = {}".format(
                    str(request.form["{}_VALOR".format(i)]).replace(",", ""),
                    request.form["{}_ID_SALDO".format(i)],
                  )
                  sqlExec(sql)
    labels = sqlQuery(
      "SELECT id, conta from Contas WHERE Saldo = 1 ORDER BY conta")

    ant = datetime(int(ano), int(mes), 1) + relativedelta(months=-1)
    anta = datetime(int(ano), int(mes), 1) + relativedelta(months=-12)
    anta6 = datetime(int(ano), int(mes), 1) + relativedelta(months=-6)
    pos = datetime(int(ano), int(mes), 1) + relativedelta(months=1)
    posa = datetime(int(ano), int(mes), 1) + relativedelta(months=12)
    posa6 = datetime(int(ano), int(mes), 1) + relativedelta(months=6)
    links = {
      "ant":
      r"/investimentos/saldos?mes={}&ano={}".format(ant.month, ant.year),
      "pos":
      r"/investimentos/saldos?mes={}&ano={}".format(pos.month, pos.year),
      "anta":
      r"/investimentos/saldos?mes={}&ano={}".format(anta.month, anta.year),
      "posa":
      r"/investimentos/saldos?mes={}&ano={}".format(posa.month, posa.year),
      "anta6":
      r"/investimentos/saldos?mes={}&ano={}".format(anta6.month, anta6.year),
      "posa6":
      r"/investimentos/saldos?mes={}&ano={}".format(posa6.month, posa6.year),
      "atual":
      r"/investimentos/saldos",
    }

    r = sqlQuery(
      "SELECT t1.id, t1.datahora, t1.id_conta, t1.valor FROM Saldos t1, Contas t2 WHERE t1.id_conta = t2.ID AND t2.Saldo = 1 and cast(strftime('%Y', t1.datahora) as integer) = {} and cast(strftime('%m', t1.datahora) as integer) = {} order by t1.datahora, t2.conta"
      .format(ano, mes))
    vals = {}
    ids = {}

    from fUtils import isfloat
    for l in r:
      if isfloat(l["valor"]):
        vals[int(l["id_conta"])] = "{:0,.2f}".format(l["valor"])
      else:
        vals[int(l["id_conta"])] = l["valor"]

      ids[int(l["id_conta"])] = l["id"]
    return render_template(
      "investimentos.saldos.html",
      vals=vals,
      ids=ids,
      labels=labels,
      links=links,
      ano=ano,
      mes=str(mes).zfill(2),
    )
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/investimentos/relatorios", methods=["GET", "POST"])
def investimentosRelatorios():
  try:
    mes = (datetime.now() + relativedelta(months=-0)).month
    ano = (datetime.now() + relativedelta(months=-0)).year
    if request.method == "GET":
      if request.args.get("mes") is not None:
        mes = int(request.args.get("mes"))
      if request.args.get("ano") is not None:
        ano = int(request.args.get("ano"))

    ant = datetime(int(ano), int(mes), 1) + relativedelta(months=-1)
    anta = datetime(int(ano), int(mes), 1) + relativedelta(months=-12)
    anta6 = datetime(int(ano), int(mes), 1) + relativedelta(months=-6)
    pos = datetime(int(ano), int(mes), 1) + relativedelta(months=1)
    posa = datetime(int(ano), int(mes), 1) + relativedelta(months=12)
    posa6 = datetime(int(ano), int(mes), 1) + relativedelta(months=6)
    links = {
      "ant":
      r"/investimentos/relatorios?mes={}&ano={}".format(ant.month, ant.year),
      "pos":
      r"/investimentos/relatorios?mes={}&ano={}".format(pos.month, pos.year),
      "anta":
      r"/investimentos/relatorios?mes={}&ano={}".format(anta.month, anta.year),
      "posa":
      r"/investimentos/relatorios?mes={}&ano={}".format(posa.month, posa.year),
      "anta6":
      r"/investimentos/relatorios?mes={}&ano={}".format(
        anta6.month, anta6.year),
      "posa6":
      r"/investimentos/relatorios?mes={}&ano={}".format(
        posa6.month, posa6.year),
      "atual":
      r"/investimentos/relatorios",
    }

    from JP_Invest import geraRelatorio
    rel, blocos, part_invest, part_invest_bens, mensal, valtbl, gcats = geraRelatorio(
      mes, ano)
    return render_template("investimentos.relatorios.html",
                           links=links,
                           rel=rel,
                           blocos=blocos,
                           part_invest=part_invest,
                           part_invest_bens=part_invest_bens,
                           mensal=mensal,
                           valtbl=valtbl,
                           gcats=gcats)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/investimentos/riscos", methods=["GET", "POST"])
def investimentosRiscos():
  try:
    from database import sqlQuery, sqlExec, InsertValues
    modo = "I"
    eid = 0
    rs = ""
    if request.method == "POST":
      print(request.form)

    if request.method == "GET":
      if request.args.get("mode") == "edit":
        modo = "E"
        eid = request.args.get("id")
        rs = sqlQuery("SELECT * FROM RiscosC WHERE id = {}".format(eid))[0]
      elif request.args.get("mode") == "addig":
        rs = sqlQuery(
          "SELECT * FROM Riscos WHERE categ = '{}' and risco = 'Ignora'".
          format(request.args.get("cat")))[0]
        idRisco = rs['id']
        rs = sqlQuery("SELECT * FROM contas WHERE Conta = '{}'".format(
          request.args.get("conta")))[0]
        idConta = rs['id']
        InsertValues("RiscosC", ["idConta", "idRisco"], [idConta, idRisco])

    elif request.method == "POST" and "Criar" in request.form:
      if request.form["Criar"] == "Criar":
        InsertValues("RiscosC", ["idConta", "idRisco"],
                     [request.form["conta"], request.form["risco"]])
    elif request.method == "POST" and "Update" in request.form:
      sql = "UPDATE RiscosC set idconta = '{}', idrisco = '{}' where id = {}".format(
        request.form["conta"], request.form["risco"], request.form["id"])
      sqlExec(sql)

    from JP_Invest import GeraSemCadastro
    semcad = GeraSemCadastro()

    contas = sqlQuery("SELECT * FROM Contas where saldo = 1 order by Conta")
    riscos = sqlQuery("SELECT * FROM Riscos order by Categ, Risco")
    tb = sqlQuery(
      "SELECT t1.id, t2.Conta, t3.Risco, t3.Categ FROM RiscosC t1, Contas t2, Riscos t3 where t1.idConta = t2.id and t1.idRisco = t3.id ORDER BY t3.Categ, t2.Conta"
    )

    return render_template("investimentos.riscos.html",
                           modo=modo,
                           tb=tb,
                           rs=rs,
                           contas=contas,
                           riscos=riscos,
                           semcad=semcad)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/investimentos/fluxo", methods=["GET", "POST"])
def investimentosFluxo():
  try:
    ano = (datetime.now() + relativedelta(months=-1)).year

    if request.method == "GET":
      if request.args.get("mode") == "view":
        ano = request.args.get("ano")

    from JP_Invest import GeraRelatorioFC
    tb1 = GeraRelatorioFC(0)

    from JP_Invest import GeraRelatorioFCAno
    tb2a, tb2b = GeraRelatorioFCAno(ano)

    return render_template("investimentos.fluxo.html",
                           tb1=tb1,
                           tb2a=tb2a,
                           tb2b=tb2b,
                           ano=ano)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/despesas/relatorio", methods=["GET", "POST"])
def despesasRelatorio():
  try:
    from JP_Despesas import geraRelatorio

    mes = (datetime.now() + relativedelta(months=-0)).month
    ano = (datetime.now() + relativedelta(months=-0)).year
    if request.method == "GET":
      if request.args.get("mes") is not None:
        mes = int(request.args.get("mes"))
      if request.args.get("ano") is not None:
        ano = int(request.args.get("ano"))

    ant = datetime(int(ano), int(mes), 1) + relativedelta(months=-1)
    anta = datetime(int(ano), int(mes), 1) + relativedelta(months=-12)
    anta6 = datetime(int(ano), int(mes), 1) + relativedelta(months=-6)
    pos = datetime(int(ano), int(mes), 1) + relativedelta(months=1)
    posa = datetime(int(ano), int(mes), 1) + relativedelta(months=12)
    posa6 = datetime(int(ano), int(mes), 1) + relativedelta(months=6)
    links = {
      "ant":
      r"/despesas/relatorio?mes={}&ano={}".format(ant.month, ant.year),
      "pos":
      r"/despesas/relatorio?mes={}&ano={}".format(pos.month, pos.year),
      "anta":
      r"/despesas/relatorio?mes={}&ano={}".format(anta.month, anta.year),
      "posa":
      r"/despesas/relatorio?mes={}&ano={}".format(posa.month, posa.year),
      "anta6":
      r"/despesas/relatorio?mes={}&ano={}".format(anta6.month, anta6.year),
      "posa6":
      r"/despesas/relatorio?mes={}&ano={}".format(posa6.month, posa6.year),
      "atual":
      r"/despesas/relatorio",
    }

    rel, contas, graph, evol_pct, pie, pie12, savs = geraRelatorio(mes, ano)
    return render_template("relatorio.html",
                           links=links,
                           rel=rel,
                           contas=contas,
                           graph=graph,
                           evol_pct=evol_pct,
                           pie=pie,
                           pie12=pie12,
                           savs=savs)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/pbook/tags", methods=["GET", "POST"])
def pbookTags():
  try:
    from database import sqlQuery, sqlExec, InsertValues
    modo = "I"
    eid = 0
    rs = ""
    if request.method == "GET":
      if request.args.get("mode") == "edit":
        modo = "E"
        eid = request.args.get("id")
        rs = sqlQuery("SELECT * FROM PBTags WHERE id = {}".format(eid))[0]
    elif request.method == "POST" and "Criar" in request.form:
      if request.form["Criar"] == "Criar":
        InsertValues("PBTags", ["Texto"], [request.form["Tag"]])
    elif request.method == "POST" and "Update" in request.form:
      sql = "UPDATE PBTags set texto = '{}' where id = {}".format(
        request.form["Tag"], request.form["id"])
      sqlExec(sql)
    tb = sqlQuery("SELECT * FROM PBTags ORDER BY Texto")
    return render_template("pbook.tags.html", modo=modo, tb=tb, rs=rs)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/pbook/posts", methods=["GET", "POST"])
def pbookPosts():
  try:
    modo = "I"
    eid = 0
    rs = ""
    if request.method == "GET":
      if request.args.get("mode") == "edit":
        modo = "E"
        eid = request.args.get("id")
        rs = sqlQuery("SELECT * FROM PBPosts WHERE id = {}".format(eid))[0]
    elif request.method == "POST" and "Criar" in request.form:
      if request.form["Criar"] == "Criar":
        InsertValues(
          "PBPosts", ["datahora", "Texto"],
          [datetime.now().strftime('%Y-%m-%d'), request.form["Texto"]])
    elif request.method == "POST" and "Update" in request.form:
      sql = "UPDATE PBPosts set texto = '{}' where id = {}".format(
        request.form["Texto"], request.form["id"])
      sqlExec(sql)
    elif request.method == "POST" and "Delete" in request.form:
      sql = "DELETE FROM PBPostsTags WHERE id_post = {}".format(
        request.form["id"])
      sqlExec(sql)
      sql = "DELETE FROM PBPosts WHERE id = {}".format(request.form["id"])
      sqlExec(sql)
    tb = sqlQuery("SELECT * FROM PBPosts ORDER BY Texto")
    return render_template("pbook.posts.html", modo=modo, tb=tb, rs=rs)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/pbook/timeline", methods=["GET", "POST"])
def pbookTimeline():
  try:
    if request.method == "POST" and "action" in request.form:
      if request.form["action"] == "ADD_TAG":
        InsertValues("PBPostsTags", ["id_post", "id_tag"],
                     [request.form["id"], request.form["tag"]])

    filt = ""
    if request.method == "GET" and "filter" in request.args:
      filt = request.args.get('filter')

    from JP_PBook import getPosts
    tb = getPosts(filt)

    return render_template("pbook.timeline.html", tb=tb, filt=filt)
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = "".join("\r\n<br>!! " + line for line in lines)
    logging.exception("message")
    return render_template("error.html", msg=msg)


@app.route("/uploader", methods=["GET", "POST"])
def uploader():
  if request.method == 'POST':
    d = dict(request.files)
    f = d['image']
    fname = f.filename

    fn = "{}.{}".format(
      ''.join((random.choice('qazwsxedcrfvtgbyhnujmikolp123456789')
               for i in range(48))),
      fname.split(".")[1])
    fs = os.path.join(os.path.join(os.path.abspath(os.getcwd()), "upload"), fn)
    f.save(fs)
    ret = {}
    ret['success'] = 1
    ret['file'] = {"url": "/upload/{}".format(fn)}
  else:
    ret = {}
    ret['success'] = 0

  return json.dumps(ret)


@app.route('/upload/<path:filename>')
def download(filename):
  return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# app.run(host="0.0.0.0", port=81)
#app.run(host='0.0.0.0', port= 81, debug=True, )
