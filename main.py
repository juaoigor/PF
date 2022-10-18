import sys

sys.path.insert(0, '/home/juaoigor/pf')
sys.path.insert(0, '/home/juaoigor/pf/py')
sys.path.insert(0, '/home/runner/PF')
sys.path.insert(0, '/home/runner/PF/py')

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
    if request.form['username'] == 'juaoigor' and request.form['password'] == 'site':
      session['loggedin'] = True
      return render_template('index.html')
    else:
      return render_template('login.html')
  else:
    return render_template('login.html')

@app.route('/config/contas', methods=['GET', 'POST'])
def configContas():
  from database import sqlQuery
  tb = sqlQuery("SELECT * FROM Contas")
  return render_template('config.contas.html', tb=tb)

@app.route('/config/debug', methods=['GET', 'POST'])
def configDebug():
  info = {}
  
  import os
  info['FOLDER'] =  os.getcwd()
  return render_template('config.debug.html', info=info)

@app.route('/config/setup', methods=['GET', 'POST'])
def configSetup():
  if request.method == 'POST':
    if request.form['Setup'] == 'Setup':
      from database import DataBaseReset
      DataBaseReset()
  return render_template('config.setup.html')

@app.route('/despesas/resumo', methods=['GET', 'POST'])
def despesasResumo():
  from database import sqlQuery
  
  labels = sqlQuery("SELECT id, conta from Contas ORDER BY RecDes, conta")
  return render_template('despesas.resumo.html',
                        labels=labels)

  
#app.run(host='0.0.0.0', port=81)

#Database host address:juaoigor.mysql.pythonanywhere-services.com
#Username:juaoigor password database
#database Start a console on:juaoigor$pf