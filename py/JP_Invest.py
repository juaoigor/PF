import logging
import math
import numpy as np
import pandas as pd

import string

from database import sqlQuery
from database import getParam
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

def geraRelatorio(mes, ano):
  # mes = 4
  # ano = 2024

  udate = date(ano , mes, 1) + relativedelta(months=0) - timedelta(days=1)

  r = sqlQuery("SELECT cast(strftime('%Y', datahora) as integer) as Ano, cast(strftime('%m', datahora) as integer) as Mes, t2.id as conta, t2.Conta as NomeConta, sum(t1.valor) as Valor FROM Despesas t1, Contas t2 where t1.datahora <= date('{}') and t2.Inv = 1 AND t1.id_conta = t2.id and t2.saldo = 0 GROUP BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id, t2.conta ORDER BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id".format(udate.strftime('%Y-%m-%d')))

  df = pd.DataFrame()

  for l in r:
    df.at[int(l["conta"]), "Nome"] = l["NomeConta"]
    df.at[int(l["conta"]), "{:02}/{}".format(l["Mes"], int(l["Ano"]) - 2000)] = l["Valor"]
  r = sqlQuery("SELECT cast(strftime('%Y', datahora) as integer) as Ano, cast(strftime('%m', datahora) as integer) as Mes, t2.id as conta, t2.Conta as NomeConta, sum(t1.valor) as Valor FROM Saldos t1, Contas t2 where t1.datahora <= date('{}') and t2.Inv = 1 AND t1.id_conta = t2.id and t2.saldo = 1 GROUP BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id, t2.conta ORDER BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id".format(udate.strftime('%Y-%m-%d')))

  for l in r:
    df.at[int(l["conta"]), "Nome"] = l["NomeConta"]
    df.at[int(l["conta"]), "{:02}/{}".format(l["Mes"], int(l["Ano"]) - 2000)] = l["Valor"]
  df = df.sort_values("Nome")
  df = df.fillna(0)

  toDel = []
  for c in df:
    if df[c].sum() == 0:
      toDel.append(c)

  for td in toDel:
    df = df.drop(td, axis=1)

  # Faz a Diff dos Saldos
  cols = df.columns.tolist()
  for k, v in df.iterrows():
    if v["Nome"].split(" -> ")[0] == "Carteira":
      l = v.copy()
      i = 0
      for s in l:
        if i > 1:
          df.at[k, cols[i]] = l.iloc[i] - l.iloc[i - 1]
        i = i + 1
  # Adiciona os Totais
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
  for i in ["Carteira", "Investimentos"]:
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
  for k, v in df.iterrows():
    df.at[k, "Lvl"] = int("{}".format(v["Nome"].count("->") + 1))
  df = df.reindex(df.index.values.tolist() + [3000])
  df = df.fillna(0)
  df.at[3000, "Nome"] = "TOTAL"




  for c in df:
    if c != "Nome" and c != "Lvl":
      df.at[3000, c] = df.at[2000, c] + df.at[2001, c]


  i = 3001
  df = df.reindex(df.index.values.tolist() + [i])
  df = df.fillna(0)
  df.at[i, "Nome"] = "&nbsp;&nbsp;&nbsp;&nbsp;Bens"
  df.at[i, "Lvl"] = 3
  k = df.index[df["Nome"] == "Carteira -> Bens"].tolist()[0]
  l = df.index[df["Nome"] == "Investimentos -> Bens"].tolist()[0]
  for c in df:
    if c != "Nome" and c != "Lvl":
      df.at[i, c] = (df.at[k, c] + df.at[l, c])

  i = 3002
  df = df.reindex(df.index.values.tolist() + [i])
  df = df.fillna(0)
  df.at[i, "Nome"] = "&nbsp;&nbsp;&nbsp;&nbsp;Previdencia"
  df.at[i, "Lvl"] = 3
  k = df.index[df["Nome"] == "Carteira -> Previdencia"].tolist()[0]
  l = df.index[df["Nome"] == "Investimentos -> Caixa -> Previdencia"].tolist()[0]
  for c in df:
    if c != "Nome" and c != "Lvl":
      df.at[i, c] = (df.at[k, c] + df.at[l, c])

  i = 3003
  df = df.reindex(df.index.values.tolist() + [i])
  df = df.fillna(0)
  df.at[i, "Nome"] = "&nbsp;&nbsp;&nbsp;&nbsp;Dolar"
  df.at[i, "Lvl"] = 3
  k = df.index[df["Nome"] == "Carteira -> Dolar"].tolist()[0]
  l = df.index[df["Nome"] == "Investimentos -> Caixa -> Dolar"].tolist()[0]
  for c in df:
    if c != "Nome" and c != "Lvl":
      df.at[i, c] = (df.at[k, c] + df.at[l, c])

  i = 3004
  df = df.reindex(df.index.values.tolist() + [i])
  df = df.fillna(0)
  df.at[i, "Nome"] = "&nbsp;&nbsp;&nbsp;&nbsp;Renda Fixa"
  df.at[i, "Lvl"] = 3
  k = df.index[df["Nome"] == "Carteira -> Renda Fixa"].tolist()[0]
  l = df.index[df["Nome"] == "Investimentos -> Caixa -> Renda Fixa"].tolist()[0]
  for c in df:
    if c != "Nome" and c != "Lvl":
      df.at[i, c] = (df.at[k, c] + df.at[l, c])

  i = 3005
  df = df.reindex(df.index.values.tolist() + [i])
  df = df.fillna(0)
  df.at[i, "Nome"] = "&nbsp;&nbsp;&nbsp;&nbsp;Renda Variavel"
  df.at[i, "Lvl"] = 3
  k = df.index[df["Nome"] == "Carteira -> Renda Variavel"].tolist()[0]
  l = df.index[df["Nome"] == "Investimentos -> Caixa -> Renda Variavel"].tolist()[0]
  for c in df:
    if c != "Nome" and c != "Lvl":
      df.at[i, c] = (df.at[k, c] + df.at[l, c])

  i = 3006
  df = df.reindex(df.index.values.tolist() + [i])
  df = df.fillna(0)
  df.at[i, "Nome"] = "&nbsp;&nbsp;&nbsp;&nbsp;Outros"
  df.at[i, "Lvl"] = 3
  k = df.index[df["Nome"] == "Carteira -> Outros"].tolist()[0]
  l = df.index[df["Nome"] == "Investimentos -> Caixa -> Outros"].tolist()[0]
  for c in df:
    if c != "Nome" and c != "Lvl":
      df.at[i, c] = (df.at[k, c] + df.at[l, c])

  i = 3007
  df = df.reindex(df.index.values.tolist() + [i])
  df = df.fillna(0)
  df.at[i, "Nome"] = "&nbsp;&nbsp;&nbsp;&nbsp;Retido"
  df.at[i, "Lvl"] = 3
  k = df.index[df["Nome"] == "Carteira -> Retido"].tolist()[0]
  l = df.index[df["Nome"] == "Investimentos -> Caixa -> Retido"].tolist()[0]
  for c in df:
    if c != "Nome" and c != "Lvl":
      df.at[i, c] = (df.at[k, c] + df.at[l, c])

  i = 3020
  df = df.reindex(df.index.values.tolist() + [i])
  df = df.fillna(0)
  df.at[i, "Nome"] = "&nbsp;Total Ex Retido"
  df.at[i, "Lvl"] = 2
  for c in df:
    if c != "Nome" and c != "Lvl":
      df.at[i, c] = df.at[3000, c] - df.at[3007, c]

  i = 3021
  df = df.reindex(df.index.values.tolist() + [i])
  df = df.fillna(0)
  df.at[i, "Nome"] = "&nbsp;Total Ex Retido/Bens/Outros"
  df.at[i, "Lvl"] = 2
  for c in df:
    if c != "Nome" and c != "Lvl":
      df.at[i, c] = df.at[3000, c] - df.at[3007, c] - df.at[3001, c] - df.at[3006, c]

  i = 3022
  df = df.reindex(df.index.values.tolist() + [i])
  df = df.fillna(0)
  df.at[i, "Nome"] = "&nbsp;Total Ex Retido/Bens/Outros/Previdencia"
  df.at[i, "Lvl"] = 1
  for c in df:
    if c != "Nome" and c != "Lvl":
      df.at[i, c] = df.at[3000, c] - df.at[3001, c] - df.at[3006, c] - df.at[3002, c] - df.at[3007, c]


  res = {}
  res["header"] = []
  res["lvl"] = []
  res["nome"] = []
  res["tb"] = []
  res["tot"] = []
  res["avg"] = []
  res["tot12"] = []
  res["avg12"] = []
  res["mes"] = []
  res["ano"] = []

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
  for k, v in df.iterrows():
    l = []
    lv = []
    i = 0
    tot = 0
    for c in df:
      if c == "Nome":
        res["nome"].append("{}{}".format("&nbsp;&nbsp;&nbsp;" * str(df.at[k, c]).count("->"),str(df.at[k, c]),))
      elif c == "Lvl":
        res["lvl"].append("{:.0f}".format(int(df.at[k, c])))
      else:
        # print("{} {}".format(k,c))
        tot = tot + float(df.at[k, c])
        if (len(df.columns) - i - 2) <= 12:
          l.append("{:0,.0f}".format(float(df.at[k, c])))
        lv.append(float(df.at[k, c]))
        i = i + 1
    res["tb"].append(l)
    res["tot"].append("{:0,.0f}".format(tot))

    avg = tot / i
    res["avg"].append("{:0,.0f}".format(avg))

    avg12 = sum(lv[-12:]) / len(lv[-12:])
    res["avg12"].append("{:0,.0f}".format(avg12))

    tot12 = sum(lv[-12:])
    res["tot12"].append("{:0,.0f}".format(tot12))


  ##########
  # Blocos
  ##########
  df = df.drop("Lvl", axis=1)
  blocos = []
  for b in [["Renda Fixa", 4000], ["Renda Variavel", 4001], ["Previdencia", 4002], ["Dolar", 4003]]:

    bloco = {}
    bloco["header"] = res["header"]
    bloco["lvl"] = []
    bloco["nome"] = []
    bloco["tb"] = []
    bloco["tot"] = []
    bloco["avg"] = []
    bloco["tot12"] = []
    bloco["avg12"] = []
    bloco["mes"] = []
    bloco["ano"] = []
    bloco["titulo"] = b[0]

    df = df.reindex(df.index.values.tolist() + [b[1]])
    df = df.fillna(0)
    df.at[b[1], "Nome"] = "TOTAL {}".format(b[0])

    df = df.reindex(df.index.values.tolist() + [b[1]+100])
    df = df.fillna(0)
    df.at[b[1]+100, "Nome"] = "RESULTADO {}".format(b[0])

    c_ant = 0
    for c in df:
      if c != "Nome":
        id_mtm = df.index[df["Nome"] == "Carteira -> {}".format(b[0])].tolist()[0]
        id_cx = df.index[df["Nome"] == "Investimentos -> Caixa -> {}".format(b[0])].tolist()[0]
        df.at[b[1], c] = (df.at[id_mtm, c] + df.at[id_cx, c])
        df.at[b[1] + 100, c] = df.at[id_mtm, c] + df.at[id_cx, c]

    acct_list = ["Carteira -> {}".format(b[0]), "Investimentos -> Caixa -> {}".format(b[0]), "TOTAL {}".format(b[0]), "RESULTADO {}".format(b[0])]
    for acct in acct_list:
      acct_id = df.index[df["Nome"] == acct].tolist()[0]
      l = []
      i = -1
      tot = 0
      tot12 = 0
      for c in df:
        if c == "Nome":
          bloco["nome"].append(df.at[acct_id, c].replace("Investimentos -> ", ""))
          if df.at[acct_id, c] == "TOTAL {}".format(b[0]):
            bloco["lvl"].append(2)
          elif df.at[acct_id, c] == "RESULTADO {}".format(b[0]):
            bloco["lvl"].append(1)
          else:
            bloco["lvl"].append(3)
        elif c != "Lvl":
          if df.at[acct_id, 'Nome'] == "RESULTADO {}".format(b[0]):
            tot = df.at[acct_id, c]
          else:
            tot = tot + df.at[acct_id, c]
          if (len(df.columns) - i - 2) <= 12:
            tot12 = tot12 + df.at[acct_id, c]
            l.append("{:0,.0f}".format(tot))
          i = i + 1
      bloco["tb"].append(l)

      # RESULTADO 12M
    bloco["nome"].append("RESULTADO 12M")
    bloco["lvl"].append(2)
    bloco["nome"].append("Sld Avg")
    bloco["lvl"].append(3)
    bloco["nome"].append("RESULTADO 12M % (P&L/Sld Avg)")
    bloco["lvl"].append(2)
    cx = []
    mtm = []
    mtm_acum = []
    l1 = []
    l2 = []
    l3 = []
    id_cx = df.index[df["Nome"] == "Investimentos -> Caixa -> {}".format(b[0])].tolist()[0]
    id_mtm = df.index[df["Nome"] == "Carteira -> {}".format(b[0])].tolist()[0]
    i = -1
    for c in df:
      if c != "Lvl" and c != "Nome":
        cx.append(df.at[id_cx, c])
        mtm.append(df.at[id_mtm, c])
        mtm_acum.append(sum(mtm))
        if (len(df.columns) - i - 2) <= 12:
          pnl12 = sum(cx[-12:]) + sum(mtm[-12:])
          l1.append("{:0,.0f}".format(pnl12))

          saldo_avg = sum(mtm_acum[-12:]) / len(mtm_acum[-12:])
          if saldo_avg == 0:
            l2.append("{:0,.2f}%".format(0))
            l3.append("{:0,.2f}%".format(0))
          else:
            l2.append("{:0,.2f}%".format(100 * pnl12 / saldo_avg))
            l3.append("{:0,.0f}".format(saldo_avg))
        i = i + 1
    bloco["tb"].append(l1)
    bloco["tb"].append(l3)
    bloco["tb"].append(l2)

    blocos.append(bloco)
  ##########
  # Blocao
  ##########
  bloco = {}
  bloco["header"] = res["header"]
  bloco["lvl"] = []
  bloco["nome"] = []
  bloco["tb"] = []
  bloco["tot"] = []
  bloco["avg"] = []
  bloco["tot12"] = []
  bloco["avg12"] = []
  bloco["mes"] = []
  bloco["ano"] = []
  bloco["titulo"] = "Total"

  bloco["nome"].append("Caixa")
  bloco["lvl"].append(3)

  bloco["nome"].append("Mark To Market")
  bloco["lvl"].append(3)

  bloco["nome"].append("TOTAL")
  bloco["lvl"].append(2)

  bloco["nome"].append("RESULTADO")
  bloco["lvl"].append(1)

  bloco["nome"].append("RESULTADO 12M")
  bloco["lvl"].append(2)

  bloco["nome"].append("Sld Avg")
  bloco["lvl"].append(3)

  bloco["nome"].append("RESULTADO 12M % (P&L/Sld Avg)")
  bloco["lvl"].append(2)

  cxs = []
  mtms = []

  l1 = []
  l2 = []
  l3 = []
  l4 = []
  l5 = []
  l6 = []
  l7 = []
  restot = []
  i = -1
  cx = 0
  mtm = 0
  tot_ant = 0
  for c in df:
    if c != "Lvl" and c != "Nome":
      for b in [["Renda Fixa", 4000], ["Renda Variavel", 4001], ["Previdencia", 4002], ["Dolar", 4003]]:
        id_cx = df.index[df["Nome"] == "Investimentos -> Caixa -> {}".format(b[0])].tolist()[0]
        id_mtm = df.index[df["Nome"] == "Carteira -> {}".format(b[0])].tolist()[0]

        cx = cx + df.at[id_cx, c]
        mtm = mtm + df.at[id_mtm, c]

      cxs.append(cx)
      mtms.append(mtm)

      restot.append(cx + mtm - tot_ant)

      if (len(df.columns) - i - 2) <= 12:
        l1.append("{:0,.0f}".format(cx))
        l2.append("{:0,.0f}".format(mtm))
        l3.append("{:0,.0f}".format(cx + mtm))
        l4.append("{:0,.0f}".format(cx + mtm - tot_ant))
        l5.append("{:0,.0f}".format(sum(restot[-12:])))

        saldo_avg = sum(mtms[-12:]) / len(mtms[-12:])
        l6.append("{:0,.2f}%".format(100 * sum(restot[-12:]) / saldo_avg))
        l7.append("{:0,.0f}".format(saldo_avg))


      tot_ant = cx + mtm

      i = i + 1

  bloco["tb"].append(l1)
  bloco["tb"].append(l2)
  bloco["tb"].append(l3)
  bloco["tb"].append(l4)
  bloco["tb"].append(l5)
  bloco["tb"].append(l7)
  bloco["tb"].append(l6)

  blocos.append(bloco)
  ##########
  ##########
  ##########

  ##########
  # Participacao Invest
  ##########
  df = df.drop(df.columns[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48]], axis=1)
  cts = []
  for l in ['Dolar', 'Previdencia', 'Renda Fixa', 'Renda Variavel']:
    cts.append([l, df.index[df["Nome"] == "Carteira -> {}".format(l)].tolist()[0] ])

  lbs = []

  part_invest = {}
  part_invest_acum = {}
  for b in cts:
    part_invest[b[0]] = []
    part_invest_acum[b[0]] = 0

  part_invest_acum['TOTAL'] = 0

  for c in df:
    if c != 'Nome':
      lbs.append(c)

      for b in cts:
        part_invest_acum[b[0]] = part_invest_acum[b[0]] + df.at[b[1], c]
        part_invest_acum['TOTAL'] = part_invest_acum['TOTAL'] + df.at[b[1], c]

      for b in cts:
        if part_invest_acum['TOTAL'] == 0:
          part_invest[b[0]].append("{:0,.2f}".format(0))
        else:
          part_invest[b[0]].append("{:0,.2f}".format(100 *  part_invest_acum[b[0]]/part_invest_acum['TOTAL']))

  ##########
  # Participacao Bens
  ##########
  cts = []
  for l in ['Dolar', 'Previdencia', 'Renda Fixa', 'Renda Variavel', 'Bens', 'Outros']:
    cts.append([l, df.index[df["Nome"] == "Carteira -> {}".format(l)].tolist()[0] ])

  lbs = []

  part_invest_bens = {}
  part_invest_acum = {}
  for b in cts:
    part_invest_bens[b[0]] = []
    part_invest_acum[b[0]] = 0

  part_invest_acum['TOTAL'] = 0

  for c in df:
    if c != 'Nome':
      lbs.append(c)

      for b in cts:
        part_invest_acum[b[0]] = part_invest_acum[b[0]] + df.at[b[1], c]
        part_invest_acum['TOTAL'] = part_invest_acum['TOTAL'] + df.at[b[1], c]

      for b in cts:
        if part_invest_acum['TOTAL'] == 0:
          part_invest_bens[b[0]].append("{:0,.2f}".format(0))
        else:
          part_invest_bens[b[0]].append("{:0,.2f}".format(100 *  part_invest_acum[b[0]]/part_invest_acum['TOTAL']))

  ##########
  # Valor Mensal
  ##########
  dt = date(udate.year, 3, 1)
  if udate.month >= 3:
    dt = dt + relativedelta(years=1)
  r = relativedelta(dt, udate)
  ms = r.years * 12 + r.months

  idx = df.index[df["Nome"] == "Carteira -> Renda Fixa -> CDB"].tolist()[0]
  sidx = 0
  for c in df:
    if c != 'Nome':
      sidx = sidx + df.at[idx, c]

  mintokeep = float(getParam("MinReservaCDB", 200000))
  mensal = "{:0,.2f}".format((sidx - mintokeep) / ms)

  ##########
  # Valores em Tabela
  ##########

  #r = sqlQuery("SELECT datahora, cast(strftime('%Y', datahora) as integer) as Ano, cast(strftime('%m', datahora) as integer) as Mes, t2.id as conta, t2.Conta as NomeConta, sum(t1.valor) as Valor FROM Despesas t1, Contas t2 where t1.datahora <= date('{}') and t1.id_conta = t2.id and t2.saldo = 0 AND (t2.Conta LIKE 'D%' OR t2.Conta like 'R%') GROUP BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id, t2.conta ORDER BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id".format(udate.strftime('%Y-%m-%d')))
  r = sqlQuery("SELECT datahora, cast(strftime('%Y', datahora) as integer) as Ano, cast(strftime('%m', datahora) as integer) as Mes, t2.id as conta, t2.Conta as NomeConta, sum(t1.valor) as Valor FROM Despesas t1, Contas t2 where t1.datahora <= date('{}') and t1.id_conta = t2.id and t2.saldo = 0 AND (t2.Conta LIKE 'Investimentos -> Caixa%') GROUP BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id, t2.conta ORDER BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id".format(udate.strftime('%Y-%m-%d')))
  df_mes = pd.DataFrame()

  for l in r:
    df_mes.at[int(l["conta"]), "Nome"] = l["NomeConta"]
    df_mes.at[int(l["conta"]), "{:02}/{}".format(l["Mes"], int(l["Ano"]) - 2000)] = l["Valor"]

  df_mes = df_mes.sort_values("Nome")
  df_mes = df_mes.fillna(0)
  df_mes = df_mes.set_index('Nome')
  df_mes_acum = df_mes.cumsum(axis=1)

  mtm = []
  mtm_delta = []
  mtm_delta_val = []

  resmtm = []
  resmtm_val = []

  rf = 0
  rv = 0
  dol = 0
  prev = 0
  subtot1 = 0
  bens = 0
  outr = 0
  subtot2 = 0
  retido = 0
  tot = 0
  res_mes = 0
  res_mes_12 = 0
  i = 0
  for c in df:
    if c != 'Nome':
      rf_ant = rf
      rv_ant = rv
      dol_ant = dol
      prev_ant = prev
      subtot1_ant = subtot1
      bens_ant = bens
      outr_ant = outr
      subtot2_ant = subtot2
      retido_ant = retido
      tot_ant = tot

      res_mes_ant = res_mes
      res_mes_12_ant = res_mes_12

      rf = rf + df.at[1004, c]/1000000
      rv = rv + df.at[1005, c]/1000000
      dol = dol + df.at[1001, c]/1000000
      prev = prev + df.at[1003, c]/1000000
      subtot1 = rf + rv + dol + prev
      bens = bens + df.at[1000, c]/1000000
      outr = outr + df.at[1002, c]/1000000
      subtot2 = rf + rv + dol + prev + bens + outr
      retido = retido + df.at[1006, c]/1000000
      tot = rf + rv + dol + prev + bens + outr + retido

      c_rf = 'green' if rf >= rf_ant else 'red'
      c_rv = 'green' if rv >= rv_ant else 'red'
      c_dol = 'green' if dol >= dol_ant else 'red'
      c_prev = 'green' if prev >= prev_ant else 'red'
      c_subtot1 = 'green' if subtot1 >= subtot1_ant else 'red'
      c_bens = 'green' if bens >= bens_ant else 'red'
      c_outr = 'green' if outr >= outr_ant else 'red'
      c_subtot2 = 'green' if subtot2 >= subtot2_ant else 'red'
      c_retido = 'green' if retido >= retido_ant else 'red'
      c_tot = 'green' if tot >= tot_ant else 'red'

      mtm.append({'dt': c, 'rf': "{:0,.2f}".format(rf), 'rv': "{:0,.2f}".format(rv),
                  'dol': "{:0,.2f}".format(dol), 'prev': "{:0,.2f}".format(prev), 'subtot1': "{:0,.2f}".format(subtot1),
                  'bens': "{:0,.2f}".format(bens), 'outr': "{:0,.2f}".format(outr), 'subtot2': "{:0,.2f}".format(subtot2),
                  'retido': "{:0,.2f}".format(retido), 'total': "{:0,.2f}".format(tot),
                  'c_rf': c_rf, 'c_rv': c_rv, 'c_dol': c_dol, 'c_prev': c_prev, 'c_subtot1': c_subtot1,
                  'c_bens': c_bens, 'c_outr': c_outr, 'c_subtot2': c_subtot2, 'c_retido': c_retido, 'c_tot': c_tot,
                  })


      res_mes = subtot1 + df_mes_acum[c].sum()/1000000

      c_res_mes = 'green' if res_mes >= res_mes_ant else 'red'
      c_res_mes_12 = 'green' if res_mes_12 >= res_mes_12_ant else 'red'

      resmtm_val.append(res_mes - res_mes_ant)
      res_mes_12 = sum(resmtm_val[-12:])
      resmtm.append({'dt': c, 'tot': "{:0,.2f}".format(1000*res_mes),
                     'tot_delta': "{:0,.2f}".format(1000*(res_mes - res_mes_ant)),
                     'tot_delta_12m': "{:0,.2f}".format(1000*res_mes_12),
                     'tot_delta_12m_avg': "{:0,.2f}".format(1000*res_mes_12/12),
                     'c_res_mes': c_res_mes, 'c_res_mes_12': c_res_mes_12


                     })

      if i > 0:
        mtm_delta_val.append(tot - tot_ant)

        mtm_delta.append({'dt': c, 'rf': "{:0,.2f}".format(1000*(rf - rf_ant)), 'rv': "{:0,.2f}".format(1000*(rv - rv_ant)),
                    'dol': "{:0,.2f}".format(1000*(dol - dol_ant)), 'prev': "{:0,.2f}".format(1000*(prev - prev_ant)), 'subtot1': "{:0,.2f}".format(1000*(subtot1 - subtot1_ant)),
                    'bens': "{:0,.2f}".format(1000*(bens - bens_ant)), 'outr': "{:0,.2f}".format(1000*(outr - outr_ant)), 'subtot2': "{:0,.2f}".format(1000*(subtot2 - subtot2_ant)),
                    'retido': "{:0,.2f}".format(1000*(retido - retido_ant)), 'total': "{:0,.2f}".format(1000*(tot - tot_ant)),
                    'total_12': "{:0,.2f}".format(1000*sum(mtm_delta_val[-12:])),
                    'c_rf': c_rf, 'c_rv': c_rv, 'c_dol': c_dol, 'c_prev': c_prev, 'c_subtot1': c_subtot1,
                    'c_bens': c_bens, 'c_outr': c_outr, 'c_subtot2': c_subtot2, 'c_retido': c_retido, 'c_tot': c_tot,
                    })

      i = i + 1


  del mtm[:24]
  del resmtm[:24]
  del mtm_delta[:23]


  ### Grafico Categorias
  i = 1
  gcats = []
  categorias = sqlQuery("SELECT Categ from Riscos GROUP BY Categ ORDER BY Categ" )
  for categoria in categorias:
    cgat = {}
    cgat['nome'] = categoria['Categ']
    cgat['id'] = categoria['Categ'].replace(" ","")
    cgat['vals'] = {}
    cgat['per'] = {}
    tot = 0

    contas = sqlQuery("SELECT t3.Conta, t2.Risco FROM RiscosC t1, Riscos t2, Contas t3 where t1.idRisco = t2.id and t1.idConta = t3.id and t2.Categ  = '{}' and t2.Risco NOT IN ('Ignora')".format(categoria['Categ']))
    for conta in contas:
      idl = df.index[df["Nome"] == conta['Conta']].tolist()
      if len(idl) > 0:
        idx = idl[0]
        sidx = 0
        for c in df:
          if c != 'Nome':
            sidx = sidx + round(df.at[idx, c],0)

        tot = tot + sidx
        if conta['Risco'] in cgat['vals']:
          cgat['vals'][conta['Risco']] = cgat['vals'][conta['Risco']] + sidx
        else:
          cgat['vals'][conta['Risco']] = sidx

      for k,v in cgat['vals'].items():
          cgat['per'][k] = "{:0,.0f}%".format(100 * cgat['vals'][k]/tot)

    cgat['vals'] = {k: v for k, v in sorted(cgat['vals'].items(), key=lambda item: item[1], reverse=True)}

    if i % 2 == 0:
      cgat['pi'] = 1
    else:
      cgat['pi'] = 0

    i = i + 1

    gcats.append(cgat)


  return res, blocos, [lbs, part_invest], [lbs, part_invest_bens], mensal, [mtm, mtm_delta, resmtm], gcats


def GeraRelatorioFC(sid):
  df = pd.DataFrame()

  dt = datetime.now().date().strftime('%Y-%m-%d')
  ipca = sqlQuery("select * from taxas where indice = 'IPCA' and datahora <= '{}' ORDER BY datahora DESC LIMIT 1".format(dt))[0]['valor']
  if sid == 0:
    res = sqlQuery("SELECT t1.startindex, t2.data, t2.tipo, t2.yield, t2.yieldper, t2.amtz, sum(t3.qtde) AS qtde FROM Bonds t1, BondsFlows t2, BondsCarteira t3 WHERE t1.id = t2.idbond and t1.id = t3.idbond AND t2.data >= '{}' GROUP BY t1.startindex, t2.data, t2.tipo, t2.yield, t2.yieldper, t2.amtz HAVING SUM(t3.qtde) <> 0".format(dt))
  else:
    res = sqlQuery("SELECT t1.startindex, t2.data, t2.tipo, t2.yield, t2.yieldper, t2.amtz, sum(t3.qtde) as qtde FROM Bonds t1, BondsFlows t2, BondsCarteira t3 WHERE t1.id = t2.idbond and t1.id = t3.idbond AND t3.id = {} GROUP BY t1.startindex, t2.data, t2.tipo, t2.yield, t2.yieldper, t2.amtz  HAVING SUM(t3.qtde) <> 0".format(sid))

  for r in res:
    # r['data'] = datetime.strptime(r['data'], '%Y-%m-%d')
    if r['tipo'] == 'A':
      v = ipca / r['startindex'] * 1000 * r['amtz'] * r['qtde']
      if r['data'] in df.index:
        df.at[r['data'],'Cx'] = df.at[r['data'],'Cx'] + v
      else:
        df.at[r['data'],'Cx'] = v
    elif r['tipo'] == 'J':
      v = ipca / r['startindex'] * 1000 * (((1 + r['yield'])**r['yieldper'])-1)* (1-r['amtz']) * r['qtde']
      if r['data'] in df.index:
        df.at[r['data'],'Cx'] = df.at[r['data'],'Cx'] + v
      else:
        df.at[r['data'],'Cx'] = v

  df.index = pd.to_datetime(df.index)
  df_mes = df.groupby([(df.index.year), (df.index.month)]).sum()
  df_ano = df.groupby([(df.index.year)]).sum()

  anos = []
  valores = []
  valores12 = []
  valorest = []
  ys = 60
  t = 0
  for i in range(0, ys + 1):
    y = (datetime.now().date() + relativedelta(months=i * 12)).year
    anos.append(y)
    if y in df_ano.index:
      t = t + df_ano.at[y, 'Cx']
      valores.append("{:0,.2f}".format(df_ano.at[y, 'Cx']))
      valores12.append("{:0,.2f}".format(df_ano.at[y, 'Cx']/12))
      valorest.append("{:0,.2f}".format(t))
    else:
      valores.append("{:0,.2f}".format(0))
      valores12.append("{:0,.2f}".format(0))
      valorest.append("{:0,.2f}".format(0))

  tb1 = [anos, valores, valores12, valorest]

  return tb1


def GeraRelatorioFCAno(ano):
  # ano = '2024'
  df = pd.DataFrame()

  dt = datetime.now().date().strftime('%Y-%m-%d')
  ipca = sqlQuery("select * from taxas where indice = 'IPCA' and datahora <= '{}' ORDER BY datahora DESC LIMIT 1".format(dt))[0]['valor']
  res = sqlQuery("SELECT t1.bond, t1.startindex, t2.data, t2.tipo, t2.yield, t2.yieldper, t2.amtz, sum(t3.qtde) as qtde FROM Bonds t1, BondsFlows t2, BondsCarteira t3 WHERE t1.id = t2.idbond and t1.id = t3.idbond and strftime('%Y', t2.data) = '{}' GROUP BY t1.bond, t1.startindex, t2.data, t2.tipo, t2.yield, t2.yieldper, t2.amtz having sum(t3.qtde) <> 0 order by t2.data".format(ano))

  bonds = []
  datasdets = []
  valoresdets = []

  for r in res:
    # r['data'] = datetime.strptime(r['data'], '%Y-%m-%d')
    if r['tipo'] == 'A':
      v = ipca / r['startindex'] * 1000 * r['amtz'] * r['qtde']
      if r['data'] in df.index:
        df.at[r['data'],'Cx'] = df.at[r['data'],'Cx'] + v
      else:
        df.at[r['data'],'Cx'] = v
      bonds.append(r['bond'])
      datasdets.append(r['data'])
      valoresdets.append("{:0,.2f}".format(v))

    elif r['tipo'] == 'J':
      v = ipca / r['startindex'] * 1000 * (((1 + r['yield'])**r['yieldper'])-1)* (1-r['amtz']) * r['qtde']
      if r['data'] in df.index:
        df.at[r['data'],'Cx'] = df.at[r['data'],'Cx'] + v
      else:
        df.at[r['data'],'Cx'] = v
      bonds.append(r['bond'])
      datasdets.append(r['data'])
      valoresdets.append("{:0,.2f}".format(v))

  datas = []
  valores = []
  valorest = []
  t = 0
  for k, v in df.iterrows():
    datas.append(k)
    valores.append("{:0,.2f}".format(v['Cx']))
    t = t + v['Cx']
    valorest.append("{:0,.2f}".format(t))



  return [datas, valores, valorest], [bonds, datasdets, valoresdets]

def GeraSemCadastro():
  categorias = sqlQuery("SELECT id, Categ from Riscos ORDER BY Categ" )
  contas = sqlQuery("SELECT id, Conta from Contas WHERE Saldo = 1 ORDER BY Conta")
  riscos = sqlQuery("SELECT t3.Conta, t2.Categ FROM RiscosC t1, Riscos t2, Contas t3 where t1.idRisco = t2.id and t1.idConta = t3.id")

  def cadastrado(riscos, c, r):
    res = False
    for l in riscos:
      if l['Conta'] == c and l['Categ'] == r:
        res = True
        break
    return res

  lista = []
  for categoria in categorias:
    for conta in contas:
      if cadastrado(riscos, conta['Conta'], categoria['Categ']) == False:
        lista.append([conta['Conta'], categoria['Categ']])

  return lista
