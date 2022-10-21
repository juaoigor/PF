from datetime import datetime


def despProcessarTexto(s):
    r = []
    i = 1
    for l in s.split("$"):
        a = l.split("#")
        if len(a) == 3:
            r.append({'Data': a[0], 'Texto': a[1], 'Valor': a[2], 'ID': i})
            i = i + 1
    return r


def str2date(s, fmt):
    return datetime.strptime(s, fmt)


def date2str(d, fmt):
    return d.strftime(fmt)


def MontaTabelaResumo(mes, ano):
    from database import sqlQuery
    r = sqlQuery(
        "SELECT t1.datahora, t1.texto, t1.valor, t2.conta FROM Despesas t1, Contas t2 where t1.id_conta = t2.id and cast(strftime('%Y', t1.datahora) as integer) = {} and cast(strftime('%m', t1.datahora) as integer) = {} order by t1.datahora, t2.conta, t1.texto"
        .format(ano, mes))
    t = 0
    i = 0
    for l in r:
        t = t + l['valor']
        r[i]['total'] = "{:0,.2f}".format(t)
        r[i]['valor'] = "{:0,.2f}".format(l['valor'])
        i = i + 1
    res = {}
    res['detalhe'] = r

    r = sqlQuery(
        "SELECT t1.id, t1.datahora, t1.texto, t1.valor FROM Despesas t1 where t1.id_conta = 0 and cast(strftime('%Y', t1.datahora) as integer) = {} and cast(strftime('%m', t1.datahora) as integer) = {} order by t1.datahora, t1.texto"
        .format(ano, mes))
    t = 0
    i = 0
    for l in r:
        t = t + l['valor']
        r[i]['total'] = "{:0,.2f}".format(t)
        r[i]['valor'] = "{:0,.2f}".format(l['valor'])
        i = i + 1
    res['naoclass'] = r

    return res


def getProbLabel(nid):
    import string
    from database import sqlQuery
    texto = sqlQuery(
        "SELECT texto from Despesas WHERE id = {} order by id".format(
            nid))[0]['texto']
    texto = texto.lower().translate(str.maketrans('', '', string.punctuation))
    texto = ''.join([i for i in texto if not i.isdigit()])
    to_predict = [texto]

    import pickle

    with open('count_vect.pickle', 'rb') as handle:
        count_vect = pickle.load(handle)
    with open('tf_transformer.pickle', 'rb') as handle:
        tf_transformer = pickle.load(handle)
    with open('calibrated_svc.pickle', 'rb') as handle:
        calibrated_svc = pickle.load(handle)
    with open('labels.pickle', 'rb') as handle:
        labels = pickle.load(handle)

    p_count = count_vect.transform(to_predict)
    p_tfidf = tf_transformer.transform(p_count)

    import pandas as pd
    pbt = pd.DataFrame(calibrated_svc.predict_proba(p_tfidf) * 100,
                       columns=labels.classes_)

    res = []
    for c in pbt:
        res.append({
            'Conta': c,
            'Prob': pbt[c][0],
            'Probs': "{:0,.2f}".format(pbt[c][0])
        })

    return sorted(res, key=lambda d: d['Prob'], reverse=True)


def getProbLabelBulk():
    import string
    from database import sqlQuery

    tb = sqlQuery("SELECT id, texto, valor from Despesas WHERE id_conta = 0")
    i = 0
    to_predict = []
    for r in tb:
        t = tb[i]['texto']
        t = t.lower().translate(str.maketrans('', '', string.punctuation))
        t = ''.join([i for i in t if not i.isdigit()])
        to_predict.append(t)

        i = i + 1

    contas = sqlQuery("SELECT * from Contas")
    cts = {}
    for r in contas:
        cts[r['Conta']] = str(r['id'])

    import pickle

    with open('count_vect.pickle', 'rb') as handle:
        count_vect = pickle.load(handle)
    with open('tf_transformer.pickle', 'rb') as handle:
        tf_transformer = pickle.load(handle)
    with open('calibrated_svc.pickle', 'rb') as handle:
        calibrated_svc = pickle.load(handle)
    with open('labels.pickle', 'rb') as handle:
        labels = pickle.load(handle)

    p_count = count_vect.transform(to_predict)
    p_tfidf = tf_transformer.transform(p_count)

    import pandas as pd
    pbt = pd.DataFrame(calibrated_svc.predict_proba(p_tfidf) * 100,
                       columns=labels.classes_)

    topprob = pd.DataFrame()

    topprob['Max1'] = pbt.idxmax(axis=1)
    for i, r in pbt.iterrows():
        topprob.at[i, 'ID'] = str(tb[i]['id'])
        topprob.at[i, 'Texto'] = tb[i]['texto']
        topprob.at[i, 'Valor'] = "{:0,.2f}".format(tb[i]['valor'])
        topprob.at[i, 'MaxVal1'] = round(pbt.at[i, topprob.at[i, 'Max1']], 2)
        topprob.at[i, 'IDMax1'] = cts[topprob.at[i, 'Max1']]
        pbt.at[i, topprob.at[i, 'Max1']] = 0

    topprob['Max2'] = pbt.idxmax(axis=1)
    for i, r in pbt.iterrows():
        topprob.at[i, 'MaxVal2'] = round(pbt.at[i, topprob.at[i, 'Max2']], 2)
        topprob.at[i, 'IDMax2'] = cts[topprob.at[i, 'Max2']]
        pbt.at[i, topprob.at[i, 'Max2']] = 0

    topprob['Max3'] = pbt.idxmax(axis=1)
    for i, r in pbt.iterrows():
        topprob.at[i, 'MaxVal3'] = round(pbt.at[i, topprob.at[i, 'Max3']], 2)
        topprob.at[i, 'IDMax3'] = cts[topprob.at[i, 'Max3']]
        pbt.at[i, topprob.at[i, 'Max3']] = 0

    topprob = topprob.sort_values('MaxVal1', ascending=False)
    return topprob


def getProbLabelBulkCat():
    import string
    from database import sqlQuery

    tb = sqlQuery("SELECT id, texto, valor from Despesas WHERE id_conta = 0")
    i = 0
    to_predict = []
    for r in tb:
        t = tb[i]['texto']
        t = t.lower().translate(str.maketrans('', '', string.punctuation))
        t = ''.join([i for i in t if not i.isdigit()])
        to_predict.append(t)

        i = i + 1

    contas = sqlQuery("SELECT * from Contas")
    cts = {}
    for r in contas:
        cts[r['Conta']] = str(r['id'])

    import pickle

    with open('count_vect.pickle', 'rb') as handle:
        count_vect = pickle.load(handle)
    with open('tf_transformer.pickle', 'rb') as handle:
        tf_transformer = pickle.load(handle)
    with open('calibrated_svc.pickle', 'rb') as handle:
        calibrated_svc = pickle.load(handle)
    with open('labels.pickle', 'rb') as handle:
        labels = pickle.load(handle)

    p_count = count_vect.transform(to_predict)
    p_tfidf = tf_transformer.transform(p_count)

    import pandas as pd
    pbt = pd.DataFrame(calibrated_svc.predict_proba(p_tfidf) * 100,
                       columns=labels.classes_)

    topprob = pd.DataFrame()

    topprob['Max1'] = pbt.idxmax(axis=1)
    for i, r in pbt.iterrows():
        topprob.at[i, 'ID'] = str(tb[i]['id'])
        topprob.at[i, 'Texto'] = tb[i]['texto']
        topprob.at[i, 'Valor'] = "{:0,.2f}".format(tb[i]['valor'])
        topprob.at[i, 'MaxVal1'] = round(pbt.at[i, topprob.at[i, 'Max1']], 2)
        topprob.at[i, 'IDMax1'] = cts[topprob.at[i, 'Max1']]
        pbt.at[i, topprob.at[i, 'Max1']] = 0

    res = {}
    topprob = topprob.sort_values('MaxVal1', ascending=False)
    for i, r in topprob.iterrows():
        if r['Max1'] not in res:
            res[r['Max1']] = pd.DataFrame(data=None, columns=topprob.columns)
        k = len(res[r['Max1']])
        res[r['Max1']].loc[k] = r

    return res


def LabelTrain():
    # %reset -f
    import string
    from database import sqlQuery
    r = sqlQuery(
        "SELECT t1.datahora, t1.texto, t1.valor, t2.conta, t2.id as id_conta FROM Despesas t1, Contas t2 where t1.id_conta = t2.id"
    )
    i = 0
    for l in r:
        v = l['texto'].lower().translate(
            str.maketrans('', '', string.punctuation))
        r[i]['texto'] = ''.join([i for i in v if not i.isdigit()])

        i = i + 1

    import pandas as pd
    df = pd.DataFrame.from_dict(r)

    labels = df['Conta']
    text = df['texto']

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

    with open('count_vect.pickle', 'wb') as handle:
        pickle.dump(count_vect, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('tf_transformer.pickle', 'wb') as handle:
        pickle.dump(tf_transformer, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('calibrated_svc.pickle', 'wb') as handle:
        pickle.dump(calibrated_svc, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('labels.pickle', 'wb') as handle:
        pickle.dump(labels, handle, protocol=pickle.HIGHEST_PROTOCOL)


def geraRelatorio():
    from database import sqlQuery
    r = sqlQuery(
        "SELECT cast(strftime('%Y', datahora) as integer) as Ano, cast(strftime('%m', datahora) as integer) as Mes, t2.id as conta, t2.Conta as NomeConta, sum(t1.valor) as Valor FROM Despesas t1, Contas t2 where t1.id_conta = t2.id GROUP BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id, t2.conta ORDER BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer), t2.id"
    )

    import numpy as np
    import pandas as pd
    df = pd.DataFrame()

    for l in r:
        df.at[int(l['conta']), 'Nome'] = l['NomeConta']
        df.at[int(l['conta']), '{}/{}'.format(l['Mes'], l['Ano'])] = l['Valor']

    df = df.sort_values('Nome')

    z = 999
    for k, v in df.iterrows():
        nome = v['Nome']
        anome = nome.split(' -> ')
        incluir = "{} -> {}".format(anome[0], anome[1])
        if incluir not in df['Nome'].unique():
            z = z + 1
            df = df.reindex(df.index.values.tolist() + [z])
            df = df.fillna(0)
            df.at[z, 'Nome'] = incluir
            for c in df:
                if c != 'Nome':
                    for x, y in df.iterrows():
                        atmp = y['Nome'].split(' -> ')
                        tmp = "{} -> {}".format(atmp[0], atmp[1])
                        if tmp == incluir:
                            df.at[z, c] = df.at[z, c] + y[c]

    z = 1999
    for i in ['Receitas', 'Despesas', 'Investimentos']:
        z = z + 1
        df = df.reindex(df.index.values.tolist() + [z])
        df = df.fillna(0)
        df.at[z, 'Nome'] = i
        for c in df:
            if c != 'Nome':
                for x, y in df.iterrows():
                    atmp = y['Nome'].split(' -> ')
                    if len(atmp) == 2:
                        if atmp[0] == i:
                            df.at[z, c] = df.at[z, c] + y[c]

    df = df.sort_values('Nome')
    df['Lvl'] = 0
    df['ToSort'] = 0

    for k, v in df.iterrows():
        df.at[k, 'Lvl'] = '{}'.format(v['Nome'].count('->') + 1)
        if v['Nome'][:2] == 'De':
            df.at[k, 'ToSort'] = 2
        elif v['Nome'][:2] == 'Re':
            df.at[k, 'ToSort'] = 1
        elif v['Nome'][:2] == 'In':
            df.at[k, 'ToSort'] = 4

    df = df.reindex(df.index.values.tolist() + [4000])
    df = df.fillna(0)
    df.at[4000, 'Nome'] = 'Sem Classificacao'
    df.at[4000, 'ToSort'] = 2.1
    df.at[4000, 'Lvl'] = "1"

    r = sqlQuery(
        "SELECT cast(strftime('%Y', datahora) as integer) as Ano, cast(strftime('%m', datahora) as integer) as Mes, sum(t1.valor) as Valor FROM Despesas t1 where t1.id_conta = 0 GROUP BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer) ORDER BY cast(strftime('%Y', datahora) as integer), cast(strftime('%m', datahora) as integer)"
    )
    for l in r:
        df.at[4000, '{}/{}'.format(l['Mes'], l['Ano'])] = l['Valor']

    df = df.reindex(df.index.values.tolist() + [3000])
    df = df.fillna(0)
    df.at[3000, 'Nome'] = 'TOTAL'
    df.at[3000, 'ToSort'] = 3

    df = df.reindex(df.index.values.tolist() + [3001])
    df = df.fillna(0)
    df.at[3001, 'Nome'] = 'TOTAL'
    df.at[3001, 'ToSort'] = 5

    for c in df:
        if c != 'Nome' and c != 'Lvl' and c != 'ToSort':
            df.at[3000, c] = df.at[2000, c] + df.at[2001, c] + df.at[4000, c]
            df.at[3001,
                  c] = df.at[2000, c] + df.at[2001, c] + df.at[2002,
                                                               c] + df.at[4000,
                                                                          c]

    df = df.sort_values(['ToSort', 'Nome'])
    df = df.drop('ToSort', axis=1)
    lvl = df.pop('Lvl')
    df.insert(0, 'Lvl', lvl)

    df['TOT_12M'] = 0
    df['P_12M'] = ""
    df['TOT'] = 0
    df['P'] = ""
    df['M_12M'] = 0
    df['M'] = 0
    df['G'] = 0

    colexc = ['Nome', 'Lvl', 'TOT_12M', 'M_12M', 'TOT', 'M', 'P', 'P_12M', 'G']
    j = len(df.columns)
    for k, v in df.iterrows():
        tot = 0
        tot12m = 0
        i = 0
        for c in df:
            if c not in colexc:
                # print("{} {} {}".format(c, j-i-4, 2))
                if (j - i - len(colexc)) <= 12:
                    tot12m = tot12m + v[c]
                tot = tot + v[c]
                i = i + 1
        df.at[k, 'TOT'] = tot
        df.at[k, 'M'] = tot / (j - len(colexc))
        df.at[k, 'TOT_12M'] = tot12m
        df.at[k, 'M_12M'] = tot12m / 12

    for k, v in df.iterrows():
        df.at[k, 'G'] = df.at[k, 'M_12M'] - df.at[k, 'M']
        if v['Nome'].count('->') > 0:
            atmp = v['Nome'].split(' -> ')
            if atmp[0] == 'Receitas':
                df.at[k, 'P'] = (v['TOT'] / df.at[2000, 'TOT']) * 100
                df.at[k,
                      'P_12M'] = (v['TOT_12M'] / df.at[2000, 'TOT_12M']) * 100
            elif atmp[0] == 'Despesas':
                df.at[k, 'P'] = (v['TOT'] / df.at[2001, 'TOT']) * 100
                df.at[k,
                      'P_12M'] = (v['TOT_12M'] / df.at[2001, 'TOT_12M']) * 100

    for k, v in df.iterrows():
        for c in df:
            if df.at[k, c] != "":
                if (c == 'P' or c == 'P_12M'):
                    df.at[k, c] = "{:0,.0f}".format(df.at[k, c]) + "%"
                elif c != 'Nome' and c != 'Lvl':
                    df.at[k, c] = "{:0,.0f}".format(df.at[k, c])

    return df
