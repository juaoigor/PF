import logging
import math
import numpy as np
import pandas as pd

import string

from database import sqlQuery
from datetime import datetime


def despProcessarTexto(s):
    r = []
    i = 1
    for l in s.split("$"):
        a = l.split("#")
        if len(a) == 3:
            r.append({"Data": a[0], "Texto": a[1], "Valor": a[2], "ID": i})
            i = i + 1
    return r


def str2date(s, fmt):
    return datetime.strptime(s, fmt)


def date2str(d, fmt):
    return d.strftime(fmt)


def transfTexto(texto):
    texto = texto.lower().translate(str.maketrans("", "", string.punctuation))
    # texto = "".join([i for i in texto if not i.isdigit()])
    return texto


def MontaTabelaResumo(mes, ano):
    # mes = 8
    # ano = 2022
    from database import sqlQuery

    contas = sqlQuery("SELECT * from Contas")
    cts = {}
    for r in contas:
        cts[r["id"]] = r["Conta"]
    cts[0] = "SemClass"
    cts[9999] = "Ignorar"

    import pickle

    with open("count_vect.pickle", "rb") as handle:
        count_vect = pickle.load(handle)
    with open("tf_transformer.pickle", "rb") as handle:
        tf_transformer = pickle.load(handle)
    with open("calibrated_svc.pickle", "rb") as handle:
        calibrated_svc = pickle.load(handle)
    with open("labels.pickle", "rb") as handle:
        labels = pickle.load(handle)
    r = sqlQuery(
        "SELECT t1.id, t1.datahora, t1.texto, t1.id_conta, t1.valor FROM Despesas t1 where cast(strftime('%Y', t1.datahora) as integer) = {} and cast(strftime('%m', t1.datahora) as integer) = {} order by t1.datahora, t1.texto"
        .format(ano, mes))
    t = 0
    i = 0
    for l in r:
        t = t + l["valor"]
        r[i]["conta"] = cts[l["id_conta"]]
        r[i]["total"] = "{:0,.2f}".format(t)
        r[i]["valor"] = "{:0,.2f}".format(l["valor"])

        to_predict = [transfTexto(l["texto"])]
        p_count = count_vect.transform(to_predict)
        p_tfidf = tf_transformer.transform(p_count)
        pbt = pd.DataFrame(calibrated_svc.predict_proba(p_tfidf) * 100,
                           columns=labels.classes_)
        high_prob = pbt.idxmax(axis=1)[0]
        if high_prob == cts[l["id_conta"]]:
            r[i]["high_prob"] = "ok"
        else:
            if l["texto"][-7:] == "EDITADO":
                r[i]["high_prob"] = "ok"
            else:
                r[i]["high_prob"] = high_prob
        i = i + 1
    res = {}
    res["detalhe"] = r

    return res


def getProbLabel(nid):
    import string
    from database import sqlQuery

    texto = sqlQuery(
        "SELECT texto from Despesas WHERE id = {} order by id".format(
            nid))[0]["texto"]
    to_predict = [transfTexto(texto)]

    import pickle

    with open("count_vect.pickle", "rb") as handle:
        count_vect = pickle.load(handle)
    with open("tf_transformer.pickle", "rb") as handle:
        tf_transformer = pickle.load(handle)
    with open("calibrated_svc.pickle", "rb") as handle:
        calibrated_svc = pickle.load(handle)
    with open("labels.pickle", "rb") as handle:
        labels = pickle.load(handle)
    p_count = count_vect.transform(to_predict)
    p_tfidf = tf_transformer.transform(p_count)

    import pandas as pd

    pbt = pd.DataFrame(calibrated_svc.predict_proba(p_tfidf) * 100,
                       columns=labels.classes_)

    res = []
    for c in pbt:
        res.append({
            "Conta": c,
            "Prob": pbt[c][0],
            "Probs": "{:0,.2f}".format(pbt[c][0])
        })
    return sorted(res, key=lambda d: d["Prob"], reverse=True)


def getProbLabelBulk():
    from database import sqlQuery

    tb = sqlQuery("SELECT id, texto, valor from Despesas WHERE id_conta = 0")
    i = 0
    to_predict = []
    for r in tb:
        t = transfTexto(tb[i]["texto"])
        to_predict.append(t)

        i = i + 1
    contas = sqlQuery("SELECT * from Contas")
    cts = {}
    for r in contas:
        cts[r["Conta"]] = str(r["id"])
    import pickle

    with open("count_vect.pickle", "rb") as handle:
        count_vect = pickle.load(handle)
    with open("tf_transformer.pickle", "rb") as handle:
        tf_transformer = pickle.load(handle)
    with open("calibrated_svc.pickle", "rb") as handle:
        calibrated_svc = pickle.load(handle)
    with open("labels.pickle", "rb") as handle:
        labels = pickle.load(handle)
    p_count = count_vect.transform(to_predict)
    p_tfidf = tf_transformer.transform(p_count)

    import pandas as pd

    pbt = pd.DataFrame(calibrated_svc.predict_proba(p_tfidf) * 100,
                       columns=labels.classes_)

    topprob = pd.DataFrame()

    topprob["Max1"] = pbt.idxmax(axis=1)
    for i, r in pbt.iterrows():
        topprob.at[i, "ID"] = str(tb[i]["id"])
        topprob.at[i, "Texto"] = tb[i]["texto"]
        topprob.at[i, "Valor"] = "{:0,.2f}".format(tb[i]["valor"])
        topprob.at[i, "MaxVal1"] = round(pbt.at[i, topprob.at[i, "Max1"]], 2)
        topprob.at[i, "IDMax1"] = cts[topprob.at[i, "Max1"]]
        pbt.at[i, topprob.at[i, "Max1"]] = 0
    topprob["Max2"] = pbt.idxmax(axis=1)
    for i, r in pbt.iterrows():
        topprob.at[i, "MaxVal2"] = round(pbt.at[i, topprob.at[i, "Max2"]], 2)
        topprob.at[i, "IDMax2"] = cts[topprob.at[i, "Max2"]]
        pbt.at[i, topprob.at[i, "Max2"]] = 0
    topprob["Max3"] = pbt.idxmax(axis=1)
    for i, r in pbt.iterrows():
        topprob.at[i, "MaxVal3"] = round(pbt.at[i, topprob.at[i, "Max3"]], 2)
        topprob.at[i, "IDMax3"] = cts[topprob.at[i, "Max3"]]
        pbt.at[i, topprob.at[i, "Max3"]] = 0
    topprob = topprob.sort_values("MaxVal1", ascending=False)
    return topprob


def getProbLabelBulkCat():
    import string
    from database import sqlQuery

    tb = sqlQuery("SELECT id, texto, valor from Despesas WHERE id_conta = 0")
    i = 0
    to_predict = []
    for r in tb:
        t = transfTexto(tb[i]["texto"])
        to_predict.append(t)

        i = i + 1
    contas = sqlQuery("SELECT * from Contas")
    cts = {}
    for r in contas:
        cts[r["Conta"]] = str(r["id"])
    import pickle

    with open("count_vect.pickle", "rb") as handle:
        count_vect = pickle.load(handle)
    with open("tf_transformer.pickle", "rb") as handle:
        tf_transformer = pickle.load(handle)
    with open("calibrated_svc.pickle", "rb") as handle:
        calibrated_svc = pickle.load(handle)
    with open("labels.pickle", "rb") as handle:
        labels = pickle.load(handle)
    p_count = count_vect.transform(to_predict)
    p_tfidf = tf_transformer.transform(p_count)

    import pandas as pd

    pbt = pd.DataFrame(calibrated_svc.predict_proba(p_tfidf) * 100,
                       columns=labels.classes_)

    topprob = pd.DataFrame()

    topprob["Max1"] = pbt.idxmax(axis=1)
    for i, r in pbt.iterrows():
        topprob.at[i, "ID"] = str(tb[i]["id"])
        topprob.at[i, "Texto"] = tb[i]["texto"]
        topprob.at[i, "Valor"] = "{:0,.2f}".format(tb[i]["valor"])
        topprob.at[i, "MaxVal1"] = round(pbt.at[i, topprob.at[i, "Max1"]], 2)
        topprob.at[i, "IDMax1"] = cts[topprob.at[i, "Max1"]]
        pbt.at[i, topprob.at[i, "Max1"]] = 0
    res = {}
    topprob = topprob.sort_values("MaxVal1", ascending=False)
    for i, r in topprob.iterrows():
        if r["Max1"] not in res:
            res[r["Max1"]] = pd.DataFrame(data=None, columns=topprob.columns)
        k = len(res[r["Max1"]])
        res[r["Max1"]].loc[k] = r
    return res


def LabelTrain():
    from database import sqlQuery

    r = sqlQuery(
        "SELECT t1.datahora, t1.texto, t1.valor, t2.conta, t2.id as id_conta FROM Despesas t1, Contas t2 where t1.id_conta = t2.id"
    )
    i = 0
    for l in r:
        r[i]["texto"] = transfTexto(l["texto"])

        i = i + 1
    import pandas as pd

    df = pd.DataFrame.from_dict(r)

    labels = df["Conta"]
    text = df["texto"]

    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.feature_extraction.text import TfidfTransformer
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder

    X_train, X_test, y_train, y_test = train_test_split(text,
                                                        labels,
                                                        random_state=0,
                                                        test_size=0.01)
    count_vect = CountVectorizer()
    X_train_counts = count_vect.fit_transform(X_train)
    tf_transformer = TfidfTransformer().fit(X_train_counts)
    X_train_transformed = tf_transformer.transform(X_train_counts)

    X_test_counts = count_vect.transform(X_test)
    X_test_transformed = tf_transformer.transform(X_test_counts)

    labels = LabelEncoder()
    y_train_labels_fut = labels.fit(y_train)
    y_train_labels_trf = labels.transform(y_train)

    from sklearn.svm import LinearSVC
    from sklearn.calibration import CalibratedClassifierCV

    linear_svc = LinearSVC()
    clf = linear_svc.fit(X_train_transformed, y_train_labels_trf)

    calibrated_svc = CalibratedClassifierCV(base_estimator=linear_svc,
                                            cv="prefit")
    calibrated_svc.fit(X_train_transformed, y_train_labels_trf)
    predicted = calibrated_svc.predict(X_test_transformed)

    import pickle

    with open("count_vect.pickle", "wb") as handle:
        pickle.dump(count_vect, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open("tf_transformer.pickle", "wb") as handle:
        pickle.dump(tf_transformer, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open("calibrated_svc.pickle", "wb") as handle:
        pickle.dump(calibrated_svc, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open("labels.pickle", "wb") as handle:
        pickle.dump(labels, handle, protocol=pickle.HIGHEST_PROTOCOL)


def is_number_tryexcept(s):
    """ Returns True is string is a number. """
    try:
        float(s)
        return True
    except ValueError:
        return False


def geraRelatorioInvest():
    r = sqlQuery(
        "SELECT cast(strftime('%Y', datahora) as integer) as Ano, cast(strftime('%m', datahora) as integer) as Mes, t2.id as conta, t2.Conta as NomeConta, sum(t1.valor) as Valor FROM Despesas t1, Contas t2 where t2.Inv = 1 AND t1.id_conta = t2.id and t2.saldo = 0 GROUP BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id, t2.conta ORDER BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id"
    )

    df = pd.DataFrame()

    for l in r:
        df.at[int(l["conta"]), "Nome"] = l["NomeConta"]
        df.at[int(l["conta"]),
              "{:02}/{}".format(l["Mes"],
                                int(l["Ano"]) - 2000)] = l["Valor"]
    r = sqlQuery(
        "SELECT cast(strftime('%Y', datahora) as integer) as Ano, cast(strftime('%m', datahora) as integer) as Mes, t2.id as conta, t2.Conta as NomeConta, sum(t1.valor) as Valor FROM Saldos t1, Contas t2 where t2.Inv = 1 AND t1.id_conta = t2.id and t2.saldo = 1 GROUP BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id, t2.conta ORDER BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id"
    )

    for l in r:
        df.at[int(l["conta"]), "Nome"] = l["NomeConta"]
        df.at[int(l["conta"]),
              "{:02}/{}".format(l["Mes"],
                                int(l["Ano"]) - 2000)] = l["Valor"]
    df = df.sort_values("Nome")
    df = df.fillna(0)

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

    res["header"].append("Nome")

    tot_carteira = 0
    tot_invest = 0
    tot_bens = 0
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
        elif v["Nome"].split(" -> ")[0] == "Carteira":
            res["p"].append("{:.0f}%".format(tot / (tot_carteira - tot_bens) *
                                             100))
        elif v["Nome"].split(" -> ")[0] == "Investimentos":
            res["p"].append("")
        else:
            res["p"].append("")
    # Renda Fixa
    df = df.drop("Lvl", axis=1)
    rf = {}
    rf["header"] = res["header"]
    rf["lvl"] = []
    rf["nome"] = []
    rf["tb"] = []
    rf["tot"] = []
    rf["avg"] = []
    rf["tot12"] = []
    rf["avg12"] = []
    rf["mes"] = []
    rf["ano"] = []

    df = df.reindex(df.index.values.tolist() + [4000])
    df = df.fillna(0)
    df.at[4000, "Nome"] = "TOTAL RF"

    acct_list = [
        "Carteira -> Renda Fixa", "Investimentos -> Caixa -> Renda Fixa"
    ]
    for acct in acct_list:
        acct_id = df.index[df["Nome"] == acct].tolist()[0]
        for c in df:
            if c != "Nome":
                df.at[4000, c] = df.at[4000, c] + df.at[acct_id, c]
    acct_list = [
        "Carteira -> Renda Fixa",
        "Investimentos -> Caixa -> Renda Fixa",
        "TOTAL RF",
    ]
    for acct in acct_list:
        acct_id = df.index[df["Nome"] == acct].tolist()[0]
        l = []
        i = -1
        tot = 0
        tot12 = 0
        for c in df:
            if c == "Nome":
                rf["nome"].append(df.at[acct_id,
                                        c].replace("Investimentos -> ", ""))
                if df.at[acct_id, c] == "TOTAL RF":
                    rf["lvl"].append(2)
                else:
                    rf["lvl"].append(3)
            elif c != "Lvl":
                tot = tot + df.at[acct_id, c]
                if (len(df.columns) - i - 2) <= 12:
                    tot12 = tot12 + df.at[acct_id, c]
                    l.append("{:0,.0f}".format(df.at[acct_id, c]))
                i = i + 1
        rf["tb"].append(l)
        rf["avg"].append("{:0,.0f}".format(tot / (i + 1)))
        rf["avg12"].append("{:0,.0f}".format(tot12 / 12))
        rf["tot"].append("{:0,.0f}".format(tot))
        rf["tot12"].append("{:0,.0f}".format(tot12))
    # Renda Variavel
    rv = {}
    rv["header"] = res["header"]
    rv["lvl"] = []
    rv["nome"] = []
    rv["tb"] = []
    rv["tot"] = []
    rv["avg"] = []
    rv["tot12"] = []
    rv["avg12"] = []
    rv["mes"] = []
    rv["ano"] = []

    df = df.reindex(df.index.values.tolist() + [4001])
    df = df.fillna(0)
    df.at[4001, "Nome"] = "TOTAL RV"

    acct_list = [
        "Carteira -> Renda Variavel",
        "Investimentos -> Caixa -> Renda Variavel",
    ]
    for acct in acct_list:
        acct_id = df.index[df["Nome"] == acct].tolist()[0]
        for c in df:
            if c != "Nome":
                df.at[4001, c] = df.at[4001, c] + df.at[acct_id, c]
    acct_list = [
        "Carteira -> Renda Variavel",
        "Investimentos -> Caixa -> Renda Variavel",
        "TOTAL RV",
    ]
    for acct in acct_list:
        acct_id = df.index[df["Nome"] == acct].tolist()[0]
        l = []
        i = -1
        tot = 0
        tot12 = 0
        for c in df:
            if c == "Nome":
                rv["nome"].append(df.at[acct_id,
                                        c].replace("Investimentos -> ", ""))
                if df.at[acct_id, c] == "TOTAL RV":
                    rv["lvl"].append(2)
                else:
                    rv["lvl"].append(3)
            elif c != "Lvl":
                tot = tot + df.at[acct_id, c]
                if (len(df.columns) - i - 2) <= 12:
                    tot12 = tot12 + df.at[acct_id, c]
                    l.append("{:0,.0f}".format(df.at[acct_id, c]))
                i = i + 1
        rv["tb"].append(l)
        rv["avg"].append("{:0,.0f}".format(tot / (i + 1)))
        rv["avg12"].append("{:0,.0f}".format(tot12 / 12))
        rv["tot"].append("{:0,.0f}".format(tot))
        rv["tot12"].append("{:0,.0f}".format(tot12))
    # Previdencia
    prev = {}
    prev["header"] = res["header"]
    prev["lvl"] = []
    prev["nome"] = []
    prev["tb"] = []
    prev["tot"] = []
    prev["avg"] = []
    prev["tot12"] = []
    prev["avg12"] = []
    prev["mes"] = []
    prev["ano"] = []

    df = df.reindex(df.index.values.tolist() + [4002])
    df = df.fillna(0)
    df.at[4002, "Nome"] = "TOTAL Prev"

    acct_list = [
        "Carteira -> Previdencia",
        "Investimentos -> Caixa -> Previdencia",
    ]
    for acct in acct_list:
        acct_id = df.index[df["Nome"] == acct].tolist()[0]
        for c in df:
            if c != "Nome":
                df.at[4002, c] = df.at[4002, c] + df.at[acct_id, c]
    acct_list = [
        "Carteira -> Previdencia",
        "Investimentos -> Caixa -> Previdencia",
        "TOTAL Prev",
    ]
    for acct in acct_list:
        acct_id = df.index[df["Nome"] == acct].tolist()[0]
        l = []
        i = -1
        tot = 0
        tot12 = 0
        for c in df:
            if c == "Nome":
                prev["nome"].append(df.at[acct_id,
                                          c].replace("Investimentos -> ", ""))
                if df.at[acct_id, c] == "TOTAL Prev":
                    prev["lvl"].append(2)
                else:
                    prev["lvl"].append(3)
            elif c != "Lvl":
                tot = tot + df.at[acct_id, c]
                if (len(df.columns) - i - 2) <= 12:
                    tot12 = tot12 + df.at[acct_id, c]
                    l.append("{:0,.0f}".format(df.at[acct_id, c]))
                i = i + 1
        prev["tb"].append(l)
        prev["avg"].append("{:0,.0f}".format(tot / (i + 1)))
        prev["avg12"].append("{:0,.0f}".format(tot12 / 12))
        prev["tot"].append("{:0,.0f}".format(tot))
        prev["tot12"].append("{:0,.0f}".format(tot12))
    # dolaridencia
    dolar = {}
    dolar["header"] = res["header"]
    dolar["lvl"] = []
    dolar["nome"] = []
    dolar["tb"] = []
    dolar["tot"] = []
    dolar["avg"] = []
    dolar["tot12"] = []
    dolar["avg12"] = []
    dolar["mes"] = []
    dolar["ano"] = []

    df = df.reindex(df.index.values.tolist() + [4003])
    df = df.fillna(0)
    df.at[4003, "Nome"] = "TOTAL Dolar"

    acct_list = [
        "Carteira -> Dolar",
        "Investimentos -> Caixa -> Dolar",
    ]
    for acct in acct_list:
        acct_id = df.index[df["Nome"] == acct].tolist()[0]
        for c in df:
            if c != "Nome":
                df.at[4003, c] = df.at[4003, c] + df.at[acct_id, c]
    acct_list = [
        "Carteira -> Dolar",
        "Investimentos -> Caixa -> Dolar",
        "TOTAL Dolar",
    ]
    for acct in acct_list:
        acct_id = df.index[df["Nome"] == acct].tolist()[0]
        l = []
        i = -1
        tot = 0
        tot12 = 0
        for c in df:
            if c == "Nome":
                dolar["nome"].append(df.at[acct_id,
                                           c].replace("Investimentos -> ", ""))
                if df.at[acct_id, c] == "TOTAL Dolar":
                    dolar["lvl"].append(2)
                else:
                    dolar["lvl"].append(3)
            elif c != "Lvl":
                tot = tot + df.at[acct_id, c]
                if (len(df.columns) - i - 2) <= 12:
                    tot12 = tot12 + df.at[acct_id, c]
                    l.append("{:0,.0f}".format(df.at[acct_id, c]))
                i = i + 1
        dolar["tb"].append(l)
        dolar["avg"].append("{:0,.0f}".format(tot / (i + 1)))
        dolar["avg12"].append("{:0,.0f}".format(tot12 / 12))
        dolar["tot"].append("{:0,.0f}".format(tot))
        dolar["tot12"].append("{:0,.0f}".format(tot12))
    return res, rf, rv, prev, dolar


def geraRelatorio():
    r = sqlQuery("SELECT * from Contas")
    contas = {}
    for l in r:
        contas[l["Conta"]] = str(l["id"])
    r = sqlQuery(
        "SELECT cast(strftime('%Y', datahora) as integer) as Ano, cast(strftime('%m', datahora) as integer) as Mes, t2.id as conta, t2.Conta as NomeConta, sum(t1.valor) as Valor FROM Despesas t1, Contas t2 where t1.id_conta = t2.id and t2.saldo = 0 GROUP BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id, t2.conta ORDER BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id"
    )

    df = pd.DataFrame()

    for l in r:
        df.at[int(l["conta"]), "Nome"] = l["NomeConta"]
        df.at[int(l["conta"]),
              "{:02}/{}".format(l["Mes"],
                                int(l["Ano"]) - 2000)] = l["Valor"]
    df = df.sort_values("Nome")
    df = df.fillna(0)

    # Distribui as contas passadas
    acct_zero = "Despesas -> Zero -> Zero"
    acct_dist = [
        "Despesas -> Compras -> Casa",
        "Despesas -> Filhos -> Presentes",
        "Despesas -> Lazer -> Ferias",
        "Despesas -> Lazer -> Mensal",
        "Despesas -> Living -> Mercado",
        "Despesas -> Living -> Alimentacao",
        "Despesas -> Compras -> Pessoais",
        "Despesas -> Saude -> Mensal",
        "Despesas -> Living -> Transporte",
    ]

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
                df.at[acct_id,
                      c] = df.at[acct_id, c] + df.at[acct_zero_id, c] * (
                          acct_dist_tot[a] / s)
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
                    evol_pct_l3[v["Nome"]].append(
                        df_acum.at[k, c] / df_acum.query("Lvl == 2")[c].sum())
                elif v["Lvl"] == 2:
                    if v["Nome"] not in evol_pct_l2:
                        evol_pct_l2[v["Nome"]] = []
                    evol_pct_l2[v["Nome"]].append(
                        df_acum.at[k, c] / df_acum.query("Lvl == 1")[c].sum())
    df_acum = df_acum.drop("Lvl", axis=1)

    evol_pct = [evol_lbs, evol_pct_l2, evol_pct_l3]

    df = df.reindex(df.index.values.tolist() + [4000])
    df = df.fillna(0)
    df.at[4000, "Nome"] = "Sem Classificacao"
    df.at[4000, "ToSort"] = 2.1
    df.at[4000, "Lvl"] = 1

    r = sqlQuery(
        "SELECT cast(strftime('%Y', datahora) as integer) as Ano, cast(strftime('%m', datahora) as integer) as Mes, sum(t1.valor) as Valor FROM Despesas t1 where t1.id_conta = 0 GROUP BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer) ORDER BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer)"
    )
    for l in r:
        df.at[4000, "{:02}/{}".format(l["Mes"],
                                      int(l["Ano"]) - 2000)] = l["Valor"]
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

    id_fixo = df.index[df["Nome"] == "Receitas -> Salario -> Fixo"].tolist()[0]
    id_ferias = df.index[df["Nome"] ==
                         "Despesas -> Lazer -> Ferias"].tolist()[0]
    id_educacao = df.index[df["Nome"] ==
                           "Despesas -> Filhos -> Educacao"].tolist()[0]
    # id_aquisicoes = df.index[df['Nome'] == 'Despesas -> Aquisicao'].tolist()[0]
    # id_manutencao = df.index[df['Nome'] == 'Despesas -> Manutencao'].tolist()[0]

    for c in df:
        if c != "Nome" and c != "Lvl" and c != "ToSort":
            df.at[3000, c] = df.at[2000, c] + df.at[2001, c] + df.at[4000, c]
            df.at[3001, c] = (df.at[2000, c] + df.at[2001, c] +
                              df.at[2002, c] + df.at[4000, c])

            df.at[3011, c] = df.at[id_fixo, c]
            df.at[3012, c] = -df.at[id_educacao, c]
            df.at[3013, c] = -df.at[id_ferias, c]
            df.at[3014, c] = df.at[2001, c] + df.at[4000, c]

            df.at[3010, c] = (df.at[3011, c] + df.at[3012, c] +
                              df.at[3013, c] + df.at[3014, c])
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
            res["tb"][-1][-1] = ('<span style="color: green;">' +
                                 res["tb"][-1][-1] + "</span>")
        elif lv[-1] < avg12:
            res["tb"][-1][-1] = ('<span style="color: red;">' +
                                 res["tb"][-1][-1] + "</span>")
        if avg12 > avg:
            res["avg12"][-1] = ('<span style="color: green;">' +
                                res["avg12"][-1] + "</span>")
        elif avg12 < avg:
            res["avg12"][-1] = ('<span style="color: red;">' +
                                res["avg12"][-1] + "</span>")
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
    # Return
    return res, contas, graphs, evol_pct, pie_r, pie12_r
