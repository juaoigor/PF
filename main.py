import sys

sys.path.insert(0, '/home/juaoigor/pf')
sys.path.insert(0, '/home/juaoigor/pf/py')
sys.path.insert(0, '/home/runner/PF')
sys.path.insert(0, '/home/runner/PF/py')
sys.path.insert(0, r'C:\dev\Projects\Python\Pessoal\py')

from flask import Flask
from flask import render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'financas'
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/')
@app.route('/index.html')
def index():
    if 'loggedin' in session:
        return render_template('index.html')
    return redirect(url_for('login'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'juaoigor' and request.form[
                'password'] == 'site':
            session['loggedin'] = True
            return render_template('index.html')
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/config/contas', methods=['GET', 'POST'])
def configContas():
    if request.method == 'POST' and 'Criar' in request.form:
        if request.form['Criar'] == 'Criar':
            from database import InsertValues
            InsertValues("Contas", ['conta', 'recdes', 'fixvar', 'inv'], [
                request.form['conta'], request.form['RecDes'],
                request.form['FixVar'], request.form['Invest']
            ])

    from database import sqlQuery
    tb = sqlQuery("SELECT * FROM Contas ORDER BY Inv, RecDes, conta")
    return render_template('config.contas.html', tb=tb)


@app.route('/config/debug', methods=['GET', 'POST'])
def configDebug():
    info = {}

    import os
    info['FOLDER'] = os.getcwd()
    return render_template('config.debug.html', info=info)


@app.route('/config/setup', methods=['GET', 'POST'])
def configSetup():
    if request.method == 'POST':
        if request.form['Setup'] == 'Setup':
            from database import DataBaseReset
            DataBaseReset()

    if request.method == 'GET':
        if request.args.get('train') != None:
            if request.args.get('train') == "1":
                from fUtils import LabelTrain
                LabelTrain()

    return render_template('config.setup.html')


@app.route('/despesas/classificar', methods=['GET', 'POST'])
def despesasClassificar():
    if request.method == 'POST' and 'Salvar' in request.form:
        if request.form['Salvar'] == 'Salvar':
            from database import sqlExec
            for i in range(0, 999):
                if '{}_ID'.format(i) in request.form:
                    if int(request.form['{}_Conta'.format(i)]) > 0:
                        sql = "UPDATE Despesas SET id_conta = {} WHERE id = {}".format(
                            request.form['{}_Conta'.format(i)],
                            request.form['{}_ID'.format(i)])
                        sqlExec(sql)
            return redirect(url_for('despesasResumo'))

    from database import sqlQuery
    tb = sqlQuery("SELECT * FROM Despesas WHERE id_conta = 0 ORDER BY id desc")
    labels = sqlQuery(
        "SELECT id, conta from Contas ORDER BY Inv, RecDes, conta")
    return render_template('despesas.classificar.html', tb=tb, labels=labels)


@app.route('/despesas/classnlp', methods=['GET', 'POST'])
def despesasClassNLP():
    if request.method == 'POST':
        if request.form['Update'] == 'Update':
            for i in range(0, 999):
                if 'c_{}'.format(i) in request.form:
                    if int(request.form['c_{}'.format(i)]) != 0:
                        sql = "UPDATE Despesas set id_conta = {} WHERE id = {}".format(
                            request.form['c_{}'.format(i)],
                            request.form['id_{}'.format(i)])
                        from database import sqlExec
                        sqlExec(sql)

    from fUtils import getProbLabelBulk
    tb = getProbLabelBulk()

    return render_template('despesas.classnlp.html', tb=tb)


@app.route('/despesas/importar', methods=['GET', 'POST'])
def despesasImportar():
    if request.method == 'POST' and 'Processar' in request.form:
        if request.form['Processar'] == 'Processar':
            from fUtils import despProcessarTexto
            r = despProcessarTexto(request.form['texto'])
            return render_template('despesas.importar.html', tb=r)
    if request.method == 'POST' and 'Inserir' in request.form:
        if request.form['Inserir'] == 'Inserir':
            from database import InsertValues
            from fUtils import str2date, date2str
            for i in range(0, 999):
                if '{}_Data'.format(i) in request.form:
                    InsertValues("Despesas", [
                        "id_conta", "id_cartao", "id_bem", "id_pessoa",
                        "datahora", "texto", "valor"
                    ], [
                        0, 1, 1, 1,
                        date2str(
                            str2date(request.form['{}_Data'.format(i)],
                                     "%d/%m/%Y"),
                            "%Y-%m-%d"), request.form['{}_Texto'.format(i)],
                        request.form['{}_Valor'.format(i)]
                    ])
            return redirect(url_for('despesasResumo'))
    else:
        return render_template('despesas.importar.html')


@app.route('/despesas/nlp', methods=['GET', 'POST'])
def despesasNLP():
    from database import sqlQuery

    nid = 0
    if request.method == 'GET':
        if request.args.get('id') != None:
            nid = int(request.args.get('id'))
    if nid == 0:
        nid = sqlQuery(
            "SELECT id from Despesas WHERE id_conta = 0 order by id")[0]['id']

    print(nid)
    linfo = sqlQuery("SELECT * from Despesas WHERE id = {}".format(nid))[0]
    lprox = sqlQuery(
        "SELECT id from Despesas WHERE id_conta = 0 and id > {} order by id".
        format(nid))[0]
    from fUtils import getProbLabel
    tb = getProbLabel(nid)

    return render_template('despesas.nlp.html',
                           tb=tb,
                           linfo=linfo,
                           lprox=lprox)


@app.route('/despesas/resumo', methods=['GET', 'POST'])
def despesasResumo():
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    mes = datetime.now().month
    ano = datetime.now().year

    if request.method == 'GET':
        if request.args.get('mes') != None:
            mes = int(request.args.get('mes'))
        if request.args.get('ano') != None:
            ano = int(request.args.get('ano'))

    from database import sqlQuery
    labels = sqlQuery("SELECT id, conta from Contas ORDER BY RecDes, conta")
    pessoas = sqlQuery("SELECT id, nome from Pessoas ORDER BY Nome")
    bens = sqlQuery("SELECT id, nome from Bens ORDER BY Nome")

    ant = (datetime(int(ano), int(mes), 1) + relativedelta(months=-1))
    pos = (datetime(int(ano), int(mes), 1) + relativedelta(months=1))
    links = {
        "ant": r"/despesas/resumo?mes={}&ano={}".format(ant.month, ant.year),
        "pos": r"/despesas/resumo?mes={}&ano={}".format(pos.month, pos.year)
    }

    from fUtils import MontaTabelaResumo

    return render_template('despesas.resumo.html',
                           labels=labels,
                           pessoas=pessoas,
                           bens=bens,
                           links=links,
                           tb=MontaTabelaResumo(mes, ano))


#app.run(host='0.0.0.0', port=81)
