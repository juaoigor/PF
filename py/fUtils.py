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
        "SELECT t1.datahora, t1.texto, t1.valor, t2.conta FROM Despesas t1, Contas t2 where t1.id_conta = t2.id and cast(strftime('%Y', t1.datahora) as integer) = {} and cast(strftime('%m', t1.datahora) as integer) = {} order by t1.datahora, t2.conta"
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

    tb = sqlQuery("SELECT id, texto from Despesas WHERE id_conta = 0")
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

    return topprob


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
