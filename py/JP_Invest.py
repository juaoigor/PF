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


def geraRelatorio(il):
    # il = False
    if il:
        dd = datetime.now() + relativedelta(months=1)
        udate = date(dd.year, dd.month, 1) - timedelta(days=1)
    else:
        udate = date(datetime.now().year,
                     datetime.now().month, 1) - timedelta(days=1)

    r = sqlQuery(
        "SELECT cast(strftime('%Y', datahora) as integer) as Ano, cast(strftime('%m', datahora) as integer) as Mes, t2.id as conta, t2.Conta as NomeConta, sum(t1.valor) as Valor FROM Despesas t1, Contas t2 where t1.datahora <= date('{}') and t2.Inv = 1 AND t1.id_conta = t2.id and t2.saldo = 0 GROUP BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id, t2.conta ORDER BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id"
        .format(udate.strftime('%Y-%m-%d')))

    df = pd.DataFrame()

    for l in r:
        df.at[int(l["conta"]), "Nome"] = l["NomeConta"]
        df.at[int(l["conta"]),
              "{:02}/{}".format(l["Mes"],
                                int(l["Ano"]) - 2000)] = l["Valor"]
    r = sqlQuery(
        "SELECT cast(strftime('%Y', datahora) as integer) as Ano, cast(strftime('%m', datahora) as integer) as Mes, t2.id as conta, t2.Conta as NomeConta, sum(t1.valor) as Valor FROM Saldos t1, Contas t2 where t1.datahora <= date('{}') and t2.Inv = 1 AND t1.id_conta = t2.id and t2.saldo = 1 GROUP BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id, t2.conta ORDER BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id"
        .format(udate.strftime('%Y-%m-%d')))

    for l in r:
        df.at[int(l["conta"]), "Nome"] = l["NomeConta"]
        df.at[int(l["conta"]),
              "{:02}/{}".format(l["Mes"],
                                int(l["Ano"]) - 2000)] = l["Valor"]
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
    l = df.index[df["Nome"] ==
                 "Investimentos -> Caixa -> Previdencia"].tolist()[0]
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
    l = df.index[df["Nome"] ==
                 "Investimentos -> Caixa -> Renda Fixa"].tolist()[0]
    for c in df:
        if c != "Nome" and c != "Lvl":
            df.at[i, c] = (df.at[k, c] + df.at[l, c])

    i = 3005
    df = df.reindex(df.index.values.tolist() + [i])
    df = df.fillna(0)
    df.at[i, "Nome"] = "&nbsp;&nbsp;&nbsp;&nbsp;Renda Variavel"
    df.at[i, "Lvl"] = 3
    k = df.index[df["Nome"] == "Carteira -> Renda Variavel"].tolist()[0]
    l = df.index[df["Nome"] ==
                 "Investimentos -> Caixa -> Renda Variavel"].tolist()[0]
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
    df.at[i, "Nome"] = "&nbsp;Total Ex Bens/Outros"
    df.at[i, "Lvl"] = 2
    for c in df:
        if c != "Nome" and c != "Lvl":
            df.at[i, c] = df.at[3000, c] - df.at[3001, c] - df.at[3006, c]

    i = 3008
    df = df.reindex(df.index.values.tolist() + [i])
    df = df.fillna(0)
    df.at[i, "Nome"] = "&nbsp;Total Ex Bens/Outros/Previdencia"
    df.at[i, "Lvl"] = 1
    for c in df:
        if c != "Nome" and c != "Lvl":
            df.at[i, c] = df.at[3000, c] - df.at[3001,
                                                 c] - df.at[3006,
                                                            c] - df.at[3002, c]

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
                res["nome"].append("{}{}".format(
                    "&nbsp;&nbsp;&nbsp;" * str(df.at[k, c]).count("->"),
                    str(df.at[k, c]),
                ))
            elif c == "Lvl":
                res["lvl"].append("{:.0f}".format(int(df.at[k, c])))
            else:
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
    for b in [["Renda Fixa", 4000], ["Renda Variavel", 4001],
              ["Previdencia", 4002], ["Dolar", 4003]]:

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

        df = df.reindex(df.index.values.tolist() + [b[1] + 100])
        df = df.fillna(0)
        df.at[b[1] + 100, "Nome"] = "RESULTADO {}".format(b[0])

        acct_list = [
            "Carteira -> {}".format(b[0]),
            "Investimentos -> Caixa -> {}".format(b[0])
        ]
        c_ant = 0
        for acct in acct_list:
            x = df.index[df["Nome"] == acct].tolist()
            if len(x) > 0:
                acct_id = x[0]
                for c in df:
                    if c != "Nome":
                        df.at[b[1], c] = df.at[b[1], c] + df.at[acct_id, c]
                        if c_ant != 0 and c_ant != 'Nome':
                            df.at[b[1] + 100,
                                  c] = df.at[b[1], c] - df.at[b[1], c_ant]
                    c_ant = c
            acct_list = [
                "Carteira -> {}".format(b[0]),
                "Investimentos -> Caixa -> {}".format(b[0]),
                "TOTAL {}".format(b[0]), "RESULTADO {}".format(b[0])
            ]

        for acct in acct_list:
            acct_id = df.index[df["Nome"] == acct].tolist()[0]
            l = []
            i = -1
            tot = 0
            tot12 = 0
            for c in df:
                if c == "Nome":
                    bloco["nome"].append(df.at[acct_id, c].replace(
                        "Investimentos -> ", ""))
                    if df.at[acct_id, c] == "TOTAL {}".format(b[0]):
                        bloco["lvl"].append(2)
                    elif df.at[acct_id, c] == "RESULTADO {}".format(b[0]):
                        bloco["lvl"].append(1)
                    else:
                        bloco["lvl"].append(3)
                elif c != "Lvl":
                    tot = tot + df.at[acct_id, c]
                    if (len(df.columns) - i - 2) <= 12:
                        tot12 = tot12 + df.at[acct_id, c]
                        l.append("{:0,.0f}".format(tot))
                    i = i + 1
            bloco["tb"].append(l)

            # RESULTADO 12M
        bloco["nome"].append("RESULTADO 12M")
        bloco["lvl"].append(2)
        bloco["nome"].append("RESULTADO 12M % (P&L/Sld Avg)")
        bloco["lvl"].append(2)
        cx = []
        mtm = []
        mtm_acum = []
        l1 = []
        l2 = []
        id_cx = df.index[df["Nome"] == "Investimentos -> Caixa -> {}".format(
            b[0])].tolist()[0]
        id_mtm = df.index[df["Nome"] == "Carteira -> {}".format(
            b[0])].tolist()[0]
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
                    else:
                        l2.append("{:0,.2f}%".format(100 * pnl12 / saldo_avg))
                i = i + 1
        bloco["tb"].append(l1)
        bloco["tb"].append(l2)

        blocos.append(bloco)
    ##########
    ##########
    ##########

    ##########
    # Participacao Invest
    ##########
    df = df.drop(df.columns[[
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
        21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,
        39, 40, 41, 42, 43, 44, 45, 46, 47, 48
    ]],
                 axis=1)
    cts = []
    for l in ['Dolar', 'Previdencia', 'Renda Fixa', 'Renda Variavel']:
        cts.append([
            l, df.index[df["Nome"] == "Carteira -> {}".format(l)].tolist()[0]
        ])

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
                part_invest_acum[b[0]] = part_invest_acum[b[0]] + df.at[b[1],
                                                                        c]
                part_invest_acum['TOTAL'] = part_invest_acum['TOTAL'] + df.at[
                    b[1], c]

            for b in cts:
                if part_invest_acum['TOTAL'] == 0:
                    part_invest[b[0]].append("{:0,.2f}".format(0))
                else:
                    part_invest[b[0]].append(
                        "{:0,.2f}".format(100 * part_invest_acum[b[0]] /
                                          part_invest_acum['TOTAL']))

    ##########
    # Participacao Bens
    ##########
    cts = []
    for l in [
            'Dolar', 'Previdencia', 'Renda Fixa', 'Renda Variavel', 'Bens',
            'Outros'
    ]:
        cts.append([
            l, df.index[df["Nome"] == "Carteira -> {}".format(l)].tolist()[0]
        ])

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
                part_invest_acum[b[0]] = part_invest_acum[b[0]] + df.at[b[1],
                                                                        c]
                part_invest_acum['TOTAL'] = part_invest_acum['TOTAL'] + df.at[
                    b[1], c]

            for b in cts:
                if part_invest_acum['TOTAL'] == 0:
                    part_invest_bens[b[0]].append("{:0,.2f}".format(0))
                else:
                    part_invest_bens[b[0]].append(
                        "{:0,.2f}".format(100 * part_invest_acum[b[0]] /
                                          part_invest_acum['TOTAL']))

    #
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

    mintokeep = 100000
    mensal = "{:0,.2f}".format((sidx - mintokeep) / ms)

    return res, blocos, [lbs, part_invest], [lbs, part_invest_bens], mensal
