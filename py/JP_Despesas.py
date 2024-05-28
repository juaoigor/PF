import logging
import math
import numpy as np
import pandas as pd

import string

from database import sqlQuery
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta


def getContas():
  rs = sqlQuery("SELECT * from Contas order by Conta")
  contas = {}
  for r in rs:
    contas[r["Conta"]] = str(r["id"])
  return contas


def geraTabela(contas, cpiAdj, mes, ano):
  # if il is True:
  #   dd = datetime.now() + relativedelta(months=1)
  #   udate = date(dd.year , dd.month, 1) - timedelta(days=1)
  # else:
  #   udate = date(datetime.now().year , datetime.now().month, 1) - timedelta(days=1)

  udate = date(ano, mes, 1) + relativedelta(months=0) - timedelta(days=1)
  print(udate)

  r = sqlQuery(
    "SELECT datahora, cast(strftime('%Y', datahora) as integer) as Ano, cast(strftime('%m', datahora) as integer) as Mes, t2.id as conta, t2.Conta as NomeConta, sum(t1.valor) as Valor FROM Despesas t1, Contas t2 where t1.datahora <= date('{}') and t1.id_conta = t2.id and t2.saldo = 0 GROUP BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id, t2.conta ORDER BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id"
    .format(udate.strftime('%Y-%m-%d')))
  cpi = []
  if cpiAdj is True:
    from fUtils import cpiFactors
    cpi = cpiFactors()

  df = pd.DataFrame()

  for l in r:
    df.at[int(l["conta"]), "Nome"] = l["NomeConta"]
    if cpiAdj is True:
      df.at[
        int(l["conta"]),
        "{:02}/{}".format(l["Mes"],
                          int(l["Ano"]) -
                          2000)] = l["Valor"] * cpi[l['datahora']]['fator_inv']
    else:
      df.at[int(l["conta"]),
            "{:02}/{}".format(l["Mes"],
                              int(l["Ano"]) - 2000)] = l["Valor"]

  df = df.sort_values("Nome")
  df = df.fillna(0)

  # Distribui as contas passadas
  acct_zero = "Despesas -> Zero -> Zero"
  rs = sqlQuery("SELECT * FROM Contas WHERE Antigas = 1")
  acct_dist = []
  for r in rs:
    acct_dist.append(r['Conta'])

  acct_zero_id = df.index[df["Nome"] == acct_zero].tolist()[0]
  acct_dist_tot = {}
  s = 0
  for a in acct_dist:
    x = 0
    acct_id = df.index[df["Nome"] == a].tolist()[0]
    for c in df:
      if c != "Nome":
        x = x + df.at[acct_id, c]
    acct_dist_tot[a] = x
    s = s + x
  for a in acct_dist:
    acct_id = df.index[df["Nome"] == a].tolist()[0]
    for c in df:
      if c != "Nome":
        # print("Mes {} conta {} recebe {} do total {}".format(c, acct_id, (acct_dist_tot[a] / s), df.at[acct_zero_id, c]))
        df.at[acct_id,
              c] = df.at[acct_id,
                         c] + df.at[acct_zero_id, c] * (acct_dist_tot[a] / s)
  df = df.drop(acct_zero_id)

  # Segue
  z = 999
  for k, v in df.iterrows():
    nome = v["Nome"]
    anome = nome.split(" -> ")
    incluir = "{} -> {}".format(anome[0], anome[1])
    if incluir not in df["Nome"].unique():
      z = z + 1
      df = df.reindex(df.index.values.tolist() + [z])
      df = df.fillna(0)
      df.at[z, "Nome"] = incluir
      for c in df:
        if c != "Nome":
          for x, y in df.iterrows():
            atmp = y["Nome"].split(" -> ")
            tmp = "{} -> {}".format(atmp[0], atmp[1])
            if tmp == incluir:
              df.at[z, c] = df.at[z, c] + y[c]
  z = 1999
  for i in ["Receitas", "Despesas", "Investimentos"]:
    z = z + 1
    df = df.reindex(df.index.values.tolist() + [z])
    df = df.fillna(0)
    df.at[z, "Nome"] = i
    for c in df:
      if c != "Nome":
        for x, y in df.iterrows():
          atmp = y["Nome"].split(" -> ")
          if len(atmp) == 2:
            if atmp[0] == i:
              df.at[z, c] = df.at[z, c] + y[c]
  df = df.sort_values("Nome")
  df["Lvl"] = 0
  df["ToSort"] = 0

  for k, v in df.iterrows():
    df.at[k, "Lvl"] = int("{}".format(v["Nome"].count("->") + 1))
    if v["Nome"][:2] == "De":
      df.at[k, "ToSort"] = 2
    elif v["Nome"][:2] == "Re":
      df.at[k, "ToSort"] = 1
    elif v["Nome"][:2] == "In":
      df.at[k, "ToSort"] = 4

  df = df.sort_values(["ToSort", "Nome"])
  return df


def geraRelatorio(mes, ano):
  # if il is True:
  #   dd = datetime.now() + relativedelta(months=1)
  #   udate = date(dd.year , dd.month, 1) - timedelta(days=1)
  # else:
  #   udate = date(datetime.now().year , datetime.now().month, 1) - timedelta(days=1)

  udate = date(ano, mes, 1) + relativedelta(months=0) - timedelta(days=1)

  contas = getContas()
  df = geraTabela(contas, False, mes, ano)

  # Evolucao do %
  df_acum = pd.DataFrame().reindex_like(df)
  df_acum["Nome"] = df_acum["Nome"].astype(str)
  for k, v in df.iterrows():
    tot = 0
    for c in df:
      if c != "Nome" and c != "Lvl":
        tot = tot + v[c]
        df_acum.at[k, c] = tot
      else:
        df_acum.at[k, "Nome"] = v["Nome"]
        df_acum.at[k, "Lvl"] = v["Lvl"]
  for k, v in df_acum.iterrows():
    if v["Nome"][:2] == "De":
      pass
    else:
      df_acum = df_acum.drop(k)
  df_acum = df_acum.drop("ToSort", axis=1)
  df_acum = df_acum.drop(df.columns[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]],
                         axis=1)

  for k, v in df_acum.iterrows():
    df_acum.at[k, "Nome"] = v["Nome"].replace("Despesas -> ", "")
  evol_lbs = []
  evol_pct_l3 = {}
  evol_pct_l2 = {}

  evol_lbs = []
  for c in df_acum:
    if c != "Nome" and c != "Lvl":
      evol_lbs.append(c)
  for k, v in df_acum.iterrows():
    for c in df_acum:
      if c != "Nome" and c != "Lvl":
        if v["Lvl"] == 3:
          if v["Nome"] not in evol_pct_l3:
            evol_pct_l3[v["Nome"]] = []
          evol_pct_l3[v["Nome"]].append(df_acum.at[k, c] /
                                        df_acum.query("Lvl == 2")[c].sum())
        elif v["Lvl"] == 2:
          if v["Nome"] not in evol_pct_l2:
            evol_pct_l2[v["Nome"]] = []
          evol_pct_l2[v["Nome"]].append(df_acum.at[k, c] /
                                        df_acum.query("Lvl == 1")[c].sum())
  df_acum = df_acum.drop("Lvl", axis=1)

  evol_pct = [evol_lbs, evol_pct_l2, evol_pct_l3]

  df = df.reindex(df.index.values.tolist() + [4000])
  df = df.fillna(0)
  df.at[4000, "Nome"] = "Sem Classificacao"
  df.at[4000, "ToSort"] = 2.1
  df.at[4000, "Lvl"] = 1

  r = sqlQuery(
    "SELECT cast(strftime('%Y', datahora) as integer) as Ano, cast(strftime('%m', datahora) as integer) as Mes, sum(t1.valor) as Valor FROM Despesas t1 where t1.datahora <= date('{}') and t1.id_conta = 0 GROUP BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer) ORDER BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer)"
    .format(udate.strftime('%Y-%m-%d')))
  for l in r:
    df.at[4000, "{:02}/{}".format(l["Mes"], int(l["Ano"]) - 2000)] = l["Valor"]
  df = df.reindex(df.index.values.tolist() + [3000])
  df = df.fillna(0)
  df.at[3000, "Nome"] = "TOTAL Ex Inv"
  df.at[3000, "ToSort"] = 3

  df = df.reindex(df.index.values.tolist() + [3001])
  df = df.fillna(0)
  df.at[3001, "Nome"] = "TOTAL"
  df.at[3001, "ToSort"] = 5

  df = df.reindex(df.index.values.tolist() + [3010])
  df = df.fillna(0)
  df.at[3010, "Nome"] = "TOTAL LIMPO"
  df.at[3010, "ToSort"] = 7
  df.at[3010, "Lvl"] = 2

  df = df.reindex(df.index.values.tolist() + [3011])
  df = df.fillna(0)
  df.at[3011, "Nome"] = "&nbsp;&nbsp;&nbsp;&nbsp;1. (+) Salario Fixo"
  df.at[3011, "ToSort"] = 6
  df.at[3011, "Lvl"] = 3

  df = df.reindex(df.index.values.tolist() + [3012])
  df = df.fillna(0)
  df.at[3012, "Nome"] = "&nbsp;&nbsp;&nbsp;&nbsp;2. (+) Filhos Educacao"
  df.at[3012, "ToSort"] = 6
  df.at[3012, "Lvl"] = 3

  df = df.reindex(df.index.values.tolist() + [3013])
  df = df.fillna(0)
  df.at[3013, "Nome"] = "&nbsp;&nbsp;&nbsp;&nbsp;3. (+) Ferias"
  df.at[3013, "ToSort"] = 6
  df.at[3013, "Lvl"] = 3

  df = df.reindex(df.index.values.tolist() + [3014])
  df = df.fillna(0)
  df.at[3014, "Nome"] = "&nbsp;&nbsp;&nbsp;&nbsp;4. (-) Total Despesas"
  df.at[3014, "ToSort"] = 6
  df.at[3014, "Lvl"] = 3

  df = df.reindex(df.index.values.tolist() + [3020])
  df = df.fillna(0)
  df.at[3020, "Nome"] = "TOTAL SUJO"
  df.at[3020, "ToSort"] = 9
  df.at[3020, "Lvl"] = 2

  df = df.reindex(df.index.values.tolist() + [3021])
  df = df.fillna(0)
  df.at[3021, "Nome"] = "&nbsp;&nbsp;&nbsp;&nbsp;1. (+) Total Receitas"
  df.at[3021, "ToSort"] = 8
  df.at[3021, "Lvl"] = 3

  df = df.reindex(df.index.values.tolist() + [3022])
  df = df.fillna(0)
  df.at[3022, "Nome"] = "&nbsp;&nbsp;&nbsp;&nbsp;2. (-) Bonus"
  df.at[3022, "ToSort"] = 8
  df.at[3022, "Lvl"] = 3

  df = df.reindex(df.index.values.tolist() + [3023])
  df = df.fillna(0)
  df.at[3023, "Nome"] = "&nbsp;&nbsp;&nbsp;&nbsp;3. (-) Total Despesas"
  df.at[3023, "ToSort"] = 8
  df.at[3023, "Lvl"] = 3

  id_fixo = df.index[df["Nome"] == "Receitas -> Salario -> Fixo"].tolist()[0]
  id_fixo_d = df.index[df["Nome"] ==
                       "Receitas -> Salario -> Fixo Deduções"].tolist()[0]
  id_ferias = df.index[df["Nome"] == "Despesas -> Lazer -> Ferias"].tolist()[0]
  id_educacao = df.index[df["Nome"] ==
                         "Despesas -> Filhos -> Educacao"].tolist()[0]
  # id_aquisicoes = df.index[df['Nome'] == 'Despesas -> Aquisicao'].tolist()[0]
  # id_manutencao = df.index[df['Nome'] == 'Despesas -> Manutencao'].tolist()[0]

  id_receitas = df.index[df["Nome"] == "Receitas"].tolist()[0]
  id_bonus = df.index[df["Nome"] ==
                      "Receitas -> Salario -> Variavel"].tolist()[0]

  for c in df:
    if c != "Nome" and c != "Lvl" and c != "ToSort":
      df.at[3000, c] = df.at[2000, c] + df.at[2001, c] + df.at[4000, c]
      df.at[3001, c] = (df.at[2000, c] + df.at[2001, c] + df.at[2002, c] +
                        df.at[4000, c])

      df.at[3011, c] = df.at[id_fixo, c] + df.at[id_fixo_d, c]
      df.at[3012, c] = -df.at[id_educacao, c]
      df.at[3013, c] = -df.at[id_ferias, c]
      df.at[3014, c] = df.at[2001, c] + df.at[4000, c]

      df.at[3010, c] = (df.at[3011, c] + df.at[3012, c] + df.at[3013, c] +
                        df.at[3014, c])

      df.at[3021, c] = df.at[id_receitas, c]
      df.at[3022, c] = -df.at[id_bonus, c]
      df.at[3023, c] = df.at[3014, c]
      df.at[3020, c] = df.at[3021, c] + df.at[3022, c] + df.at[3023, c]

  df = df.sort_values(["ToSort", "Nome"])
  df = df.drop("ToSort", axis=1)
  lvl = df.pop("Lvl")
  df.insert(0, "Lvl", lvl)

  res = {}
  res["header"] = []
  res["lvl"] = []
  res["contas"] = []
  res["nome"] = []
  res["tb"] = []
  res["tot"] = []
  res["tot12"] = []
  res["avg"] = []
  res["avg12"] = []
  res["mes"] = []
  res["ano"] = []
  res["davg"] = []
  res["p"] = []
  res["p12"] = []

  res["header"].append("Nome")
  i = 0
  for c in df:
    if c != "Lvl" and c != "Nome":
      if (len(df.columns) - i - 2) <= 12:
        res["header"].append(c)
        if c.count("/") > 0:
          atmp = c.split("/")
          res["ano"].append("{:.0f}".format(int(atmp[1]) + 2000))
          res["mes"].append("{:.0f}".format(int(atmp[0])))
      i = i + 1
  tot_rec = 0
  tot_des = 0
  tot_rec12 = 0
  tot_des12 = 0
  for k, v in df.iterrows():
    l = []
    lv = []
    i = 0
    tot = 0
    for c in df:
      if c == "Nome":
        res["nome"].append("{}{}".format(
          "&nbsp;&nbsp;&nbsp;" * str(df.at[k, c]).count("->"),
          str(df.at[k, c]),
        ))
        if str(df.at[k, c]) in contas:
          res["contas"].append(contas[str(df.at[k, c])])
        else:
          res["contas"].append(0)
      elif c == "Lvl":
        res["lvl"].append("{:.0f}".format(int(df.at[k, c])))
      else:
        tot = tot + df.at[k, c]
        if (len(df.columns) - i - 2) <= 12:
          l.append("{:0,.0f}".format(float(df.at[k, c])))
        lv.append(float(df.at[k, c]))
        i = i + 1
    res["tb"].append(l)

    res["tot"].append("{:0,.0f}".format(tot))

    if res["nome"][-1] == "Receitas":
      tot_rec = tot
      tot_rec12 = sum(lv[-12:])
    elif res["nome"][-1] == "Despesas":
      tot_des = tot
      tot_des12 = sum(lv[-12:])
    avg = tot / i
    res["avg"].append("{:0,.0f}".format(avg))

    avg12 = sum(lv[-12:]) / len(lv[-12:])
    res["avg12"].append("{:0,.0f}".format(avg12))

    tot12 = sum(lv[-12:])
    res["tot12"].append("{:0,.0f}".format(tot12))

    if lv[-1] > avg12:
      res["tb"][-1][
        -1] = '<span style="color: green;">' + res["tb"][-1][-1] + "</span>"
    elif lv[-1] < avg12:
      res["tb"][-1][
        -1] = '<span style="color: red;">' + res["tb"][-1][-1] + "</span>"

    res["davg"].append("{:0,.0f}".format(avg12 - avg))

    if v["Nome"][:3] == "Rec":
      res["p"].append("{:0,.0f}".format(100 * tot / tot_rec))
      res["p12"].append("{:0,.0f}".format(100 * tot12 / tot_rec12))
    elif v["Nome"][:3] == "Des":
      res["p"].append("{:0,.0f}".format(100 * tot / tot_des))
      res["p12"].append("{:0,.0f}".format(100 * tot12 / tot_des12))
  pie = {}
  pie_r = {}

  pie12 = {}
  pie12_r = {}

  tt = 0
  tt12 = 0
  graphs = []
  for k, v in df.iterrows():
    g = {}
    x = []
    y = []
    tot = []
    avg = []
    avg12 = []
    gper = []

    i = 1
    t = 0
    t12 = 0
    if v["Lvl"] <= 2:
      g["nome"] = v["Nome"]
      for c in df:
        if c not in ["Nome", "Lvl"]:
          x.append(c)
          y.append(v[c])

          t = t + v[c]
          tot.append(t)

          avg.append(t / i)

          avg12.append(sum(y[-12:]) / len(y[-12:]))

          i = i + 1
      g["x"] = x
      g["y"] = y
      g["tot"] = tot
      g["avg"] = avg
      g["avg12"] = avg12
      g["gper"] = gper
      graphs.append(g)
    else:
      j = 0
      for c in df:
        if c not in ["Nome", "Lvl"]:
          t = t + v[c]
          if (len(df.columns) - j) <= 12:
            t12 = t12 + v[c]
        j = j + 1
      if v["Nome"].split(" -> ")[0] == "Despesas":
        pie[v["Nome"].replace("Despesas -> ", "")] = -t
        pie12[v["Nome"].replace("Despesas -> ", "")] = -t12
        tt = tt - t
        tt12 = tt12 - t12
  # PIE
  pie = sorted(pie.items(), key=lambda kv: kv[1], reverse=True)
  for l in pie:
    pie_r[l[0]] = round((l[1] / tt) * 100, 1)
  # PIE 12M
  pie12 = sorted(pie12.items(), key=lambda kv: kv[1], reverse=True)
  for l in pie12:
    pie12_r[l[0]] = round((l[1] / tt12) * 100, 1)
  # Crescimento das despesas
  for k, v in df.iterrows():
    if v["Nome"].split(" -> ")[0] == "Despesas":
      i = 0
      y = []
      for c in df:
        if c not in ["Nome", "Lvl"] and v["Lvl"] == 2:
          y.append(v[c])
          vh = sum(y)
          v1a = vh - sum(y[-12:])
          if i >= 48:
            if v1a != 0:
              g = math.log(vh / v1a)
            else:
              g = 0
            # print("{} {} {}".format(v["Nome"], c, g))
          i = i + 1
  #Grafico de Savings
  id_salario = df.index[df["Nome"] == "Receitas -> Salario"].tolist()[0]
  id_receitas = df.index[df["Nome"] == "Receitas"].tolist()[0]
  id_despesas = df.index[df["Nome"] == "Despesas"].tolist()[0]
  recs = []
  desps = []
  savings = []
  savings_tot = []
  savlbs = []
  for c in df:
    if c != "Lvl" and c != "Nome":
      recs.append(df.at[id_salario, c])
      desps.append(-(df.at[id_despesas, c] +
                     (df.at[id_receitas, c] - df.at[id_salario, c])))
      savings.append(1 - sum(desps[-12:]) / sum(recs[-12:]))
      savings_tot.append(1 - sum(desps) / sum(recs))
      savlbs.append(c)
  k = 12 * 4
  savs = [savlbs[k:], savings[k:], savings_tot[k:]]

  # Return
  return res, contas, graphs, evol_pct, pie_r, pie12_r, savs


def geraRelatorioCrescimento(conta, mes, ano):
  contas = getContas()
  df = geraTabela(contas, False, mes, ano)
  df_infl = geraTabela(contas, True, mes, ano)

  id_conta = df.index[df["Nome"] == conta].tolist()[0]
  id_parent = df.index[df["Nome"] == conta.split(" -> ")[0]].tolist()[0]

  for r in ['Lvl', 'ToSort']:
    df = df.drop(r, axis=1)

  res = {}
  res['labels'] = []
  res['valores'] = []
  res['valores_avg'] = []
  res['valores_acum'] = []
  res['valores_12m'] = []
  res['valores_avg12'] = []
  res['valores_infl'] = []
  res['valores_infl_avg12'] = []
  res['parent'] = []
  res['participacao'] = []

  anos = {}
  anosi = {}

  for c in df:
    if c not in ["Nome"]:
      res['labels'].append(c)
      res['valores'].append(df.at[id_conta, c])
      res['valores_acum'].append(sum(res['valores']))
      res['valores_avg'].append(sum(res['valores']) / len(res['valores']))
      res['valores_avg12'].append(
        sum(res['valores'][-12:]) / len(res['valores'][-12:]))
      res['valores_12m'].append(sum(res['valores'][-12:]))

      res['valores_infl'].append(df_infl.at[id_conta, c])
      res['valores_infl_avg12'].append(
        sum(res['valores_infl'][-12:]) / len(res['valores_infl'][-12:]))

      res['parent'].append(df.at[id_parent, c])
      res['participacao'].append(100 * sum(res['valores']) /
                                 sum(res['parent']))

      a = str(int(c.split("/")[1]) + 2000)
      if a not in anos:
        anos[a] = df.at[id_conta, c]
        anosi[a] = df_infl.at[id_conta, c]
      else:
        anos[a] = anos[a] + df.at[id_conta, c]
        anosi[a] = anosi[a] + df_infl.at[id_conta, c]

  return res, df['Nome'].tolist(), [list(anos.keys()), anos, anosi]


def getDuplicates():

  # Considerando a data
  rs = sqlQuery(
    "SELECT t1.datahora, t1.texto, t1.valor, count(*) FROM Despesas t1 WHERE texto like '% CCA %' GROUP BY t1.datahora, t1.texto, t1.valor HAVING count(*) > 1 ORDER BY Count(*) DESC"
  )
  tb_dt = []
  for r in rs:
    l = sqlQuery(
      "SELECT * FROM Despesas t1 WHERE t1.datahora = date('{}') and t1.texto = '{}' and t1.valor = {}"
      .format(r['datahora'], r['texto'], r['valor']))
    ls = []
    for rr in l:
      ls.append([rr['id'], rr['datahora'], rr['texto'], rr['valor']])
    tb_dt.append(ls)

  # Desconsiderando a data
  rs = sqlQuery(
    "SELECT t1.texto, t1.valor, count(*) FROM Despesas t1 WHERE texto NOT like '% CCA %' and texto NOT like '(TRANSFER) %' GROUP BY t1.texto, t1.valor HAVING count(*) > 1 ORDER BY Count(*) DESC"
  )
  tb_sdt = []
  for r in rs:
    l = sqlQuery(
      "SELECT * FROM Despesas t1 WHERE t1.texto = '{}' and t1.valor = {}".
      format(r['texto'], r['valor']))
    ls = []
    for rr in l:
      ls.append([rr['id'], rr['datahora'], rr['texto'], rr['valor']])
    tb_sdt.append(ls)

  return tb_dt, tb_sdt
