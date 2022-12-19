import logging
import math
import numpy as np
import pandas as pd

import string

from database import sqlQuery
from datetime import date
from datetime import datetime
from datetime import timedelta


def geraRelatorio():
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
    res["p"] = []
    res["pg"] = []

    res["header"].append("Nome")

    tot_carteira = 0
    tot_invest = 0
    tot_bens = 0
    tot_outros = 0
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

        if v["Nome"] == "Carteira":
            tot_carteira = tot
            res["p"].append("")
        elif v["Nome"] == "Investimentos":
            tot_invest = tot
            res["p"].append("")
        elif v["Nome"] == "Carteira -> Bens":
            tot_bens = tot
            res["p"].append("")
        elif v["Nome"][:19] == "Carteira -> Bens ->":
            res["p"].append("")
        elif v["Nome"] == "Carteira -> Outros":
            tot_outros = tot
            res["p"].append("")
        elif v["Nome"][:21] == "Carteira -> Outros ->":
            res["p"].append("")
        elif v["Nome"].split(" -> ")[0] == "Carteira":
            res["p"].append("{:.0f}%".format(
                tot / (tot_carteira - tot_bens - tot_outros) * 100))
        elif v["Nome"].split(" -> ")[0] == "Investimentos":
            res["p"].append("")
        else:
            res["p"].append("")
        if v["Nome"].split(" -> ")[0] == "Carteira":
            res["pg"].append("{:0,.0f}%".format((tot / tot_carteira) * 100))
        elif v["Nome"].split(" -> ")[0] == "Investimentos":
            res["pg"].append("{:0,.0f}%".format((tot / tot_invest) * 100))
    ##########
    # Blocos
    ##########
    df = df.drop("Lvl", axis=1)
    blocos = []
    for b in [
        ["Renda Fixa", 4000],
        ["Renda Variavel", 4001],
        ["Previdencia", 4002],
        ["Dolar", 4003],
    ]:

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

        acct_list = [
            "Carteira -> {}".format(b[0]),
            "Investimentos -> Caixa -> {}".format(b[0])
        ]
        for acct in acct_list:
            x = df.index[df["Nome"] == acct].tolist()
            if len(x) > 0:
                acct_id = x[0]
                for c in df:
                    if c != "Nome":
                        df.at[b[1], c] = df.at[b[1], c] + df.at[acct_id, c]
            acct_list = [
                "Carteira -> {}".format(b[0]),
                "Investimentos -> Caixa -> {}".format(b[0]),
                "TOTAL {}".format(b[0])
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
                    else:
                        bloco["lvl"].append(3)
                elif c != "Lvl":
                    tot = tot + df.at[acct_id, c]
                    if (len(df.columns) - i - 2) <= 12:
                        tot12 = tot12 + df.at[acct_id, c]
                        l.append("{:0,.0f}".format(df.at[acct_id, c]))
                    i = i + 1
            bloco["tb"].append(l)
            bloco["avg"].append("{:0,.0f}".format(tot / (i + 1)))
            bloco["avg12"].append("{:0,.0f}".format(tot12 / 12))
            bloco["tot"].append("{:0,.0f}".format(tot))
            bloco["tot12"].append("{:0,.0f}".format(tot12))
        # Rentabilidade
        bloco["nome"].append("Rentabilidade a.a.%")
        bloco["lvl"].append(1)
        l = []
        cx = []
        mtm = []
        mtm_acum = []
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
                pnl12 = sum(cx[-12:]) + sum(mtm[-12:])
                saldo_avg = sum(mtm_acum[-12:]) / len(mtm_acum[-12:])
                if (len(df.columns) - i - 2) <= 12:
                    if saldo_avg == 0:
                        l.append("{:0,.2f}%".format(0))
                    else:
                        l.append("{:0,.2f}%".format(100 * pnl12 / saldo_avg))
                i = i + 1
        bloco["tb"].append(l)
        if sum(cx) == 0:
            bloco["tot"].append("{:0,.2f}%".format(0))
        else:
            bloco["tot"].append("{:0,.2f}%".format(100 * (sum(cx) + sum(mtm)) /
                                                   -sum(cx)))
        blocos.append(bloco)
    ##########
    ##########
    ##########
    return res, blocos
