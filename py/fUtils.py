import logging
import math
import numpy as np
import pandas as pd

import string

from database import sqlQuery
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

def despProcessarTexto(s):
  r = []
  i = 1
  for l in s.split("$"):
    a = l.split("#")
    if len(a) == 3:
      sql = "SELECT COUNT(*) as N FROM Despesas WHERE Datahora = '{}' AND (texto = '{}' OR texto = '{}') and valor = {}".format(date2str(str2date(a[0].replace('\r', '').replace('\n', ''), "%d/%m/%Y"),"%Y-%m-%d",), a[1], "{} EDITADO".format(a[1]), a[2])
      n = sqlQuery(sql)
      r.append({"Data": a[0], "Texto": a[1], "Valor": a[2], "ID": i, "N": n[0]['N']})
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


def isfloat(str):
    try:
        float(str)
    except ValueError:
        return False
    return True


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
    r = sqlQuery("SELECT t1.id, t1.datahora, t1.texto, t1.id_conta, t1.id_transfer, t1.valor FROM Despesas t1 where cast(strftime('%Y', t1.datahora) as integer) = {} and cast(strftime('%m', t1.datahora) as integer) = {} order by t1.datahora, t1.texto".format(ano, mes))

    t = 0
    i = 0
    for l in r:
        if isfloat(l["valor"]):
            t = t + l["valor"]
        r[i]["conta"] = cts[l["id_conta"]]
        r[i]["total"] = "{:0,.2f}".format(t)
        if isfloat(l["valor"]):
            r[i]["valor"] = "{:0,.2f}".format(l["valor"])
        else:
            r[i]["valor"] = -9999
        to_predict = [transfTexto(l["texto"])]
        p_count = count_vect.transform(to_predict)
        p_tfidf = tf_transformer.transform(p_count)
        pbt = pd.DataFrame(calibrated_svc.predict_proba(p_tfidf) * 100, columns=labels.classes_)
        high_prob = pbt.idxmax(axis=1)[0]
        if high_prob == cts[l["id_conta"]]:
            r[i]["high_prob"] = "ok"
        else:
            if l["texto"][-7:] == "EDITADO":
                r[i]["high_prob"] = "ok"
            elif l["texto"][:10] == "(TRANSFER)":
                r[i]["high_prob"] = "ok"
            elif l["texto"].count("(TRANSF: ") >0:
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
        "SELECT texto from Despesas WHERE id = {} order by id".format(nid)
    )[0]["texto"]
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

    pbt = pd.DataFrame(
        calibrated_svc.predict_proba(p_tfidf) * 100, columns=labels.classes_
    )

    res = []
    for c in pbt:
        res.append(
            {"Conta": c, "Prob": pbt[c][0], "Probs": "{:0,.2f}".format(pbt[c][0])}
        )
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

    pbt = pd.DataFrame(
        calibrated_svc.predict_proba(p_tfidf) * 100, columns=labels.classes_
    )

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

    pbt = pd.DataFrame(
        calibrated_svc.predict_proba(p_tfidf) * 100, columns=labels.classes_
    )

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

    X_train, X_test, y_train, y_test = train_test_split(
        text, labels, random_state=0, test_size=0.01
    )
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

    calibrated_svc = CalibratedClassifierCV(base_estimator=linear_svc, cv="prefit")
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

def cpiFactors():
  fact = {}
  rs = sqlQuery("SELECT * from Taxas WHERE indice = 'IPCA' ORDER BY datahora DESC")
  data_ultima = date(int(rs[0]['datahora'][0:4]), int(rs[0]['datahora'][5:7]), 15)  + relativedelta(months=0)
  # rs.insert(0, {'id': 0, 'datahora': data_ultima.strftime('%Y-%m-%d'), 'indice': 'IPCA', 'valor': rs[0]['valor'] * (rs[0]['valor']/rs[1]['valor'])})

  for i in range(0,len(rs) - 2):
    dt1 = datetime.strptime(rs[i]['datahora'], '%Y-%m-%d')
    dt2 = datetime.strptime(rs[i + 1]['datahora'], '%Y-%m-%d')
    nd = (dt1-dt2).days
    for j in range(0, nd):
      ipca = rs[i]['valor'] + j * (rs[i+1]['valor'] - rs[i]['valor'])/nd
      dt = dt1 - relativedelta(days=j)
      fact[dt.strftime('%Y-%m-%d')] = {'IPCA': ipca}

  for i in range(1, 100):
    dt = data_ultima + relativedelta(days=i)
    dt2 = dt - relativedelta(days=1)

    if dt2.month == 2 and dt2.day >= 29:
      dt1 = date(dt2.year - 1, dt2.month, 28)
    else:
      dt1 = date(dt2.year - 1, dt2.month, dt2.day)

    dt0 = dt1 + relativedelta(days=1)
    f = fact[dt2.strftime('%Y-%m-%d')]['IPCA']/fact[dt1.strftime('%Y-%m-%d')]['IPCA']
    ipca = fact[dt0.strftime('%Y-%m-%d')]['IPCA'] * f
    fact[dt.strftime('%Y-%m-%d')] = {'IPCA': ipca}

  i = 0
  fk = ""
  for k in sorted(fact):
    if i == 0:
      fk = k
      fact[k]['fator'] = 1
    else:
      fact[k]['fator'] = fact[k]['IPCA']/fact[fk]['IPCA']
    i = i + 1

  i = 0
  fk = ""
  for k in sorted(fact, reverse=True):
    if i == 0:
      fk = k
      fact[k]['fator_inv'] = 1
    else:
      fact[k]['fator_inv'] = fact[fk]['IPCA']/fact[k]['IPCA']
    i = i + 1

  return fact
