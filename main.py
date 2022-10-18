from flask import Flask
from flask import render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL 


app = Flask(__name__)
app.secret_key = 'financas'
app.config['TEMPLATES_AUTO_RELOAD'] = True

app.config['MYSQL_HOST'] = 'juaoigor.mysql.pythonanywhere-services.com'
app.config['MYSQL_USER'] = 'juaoigor'
app.config['MYSQL_PASSWORD'] = 'database'
app.config['MYSQL_DB'] = 'juaoigor$pf'
mysql = MySQL(app)

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

@app.route('/config/setup', methods=['GET', 'POST'])
def configSetup():
  if request.method == 'POST':
    if request.form['Setup'] == 'Setup':
      from py.database import execScript
      execScript(mysql, 'sql/setup.sql')
      
  return render_template('config.setup.html')

  
app.run(host='0.0.0.0', port=81)

#Database host address:juaoigor.mysql.pythonanywhere-services.com
#Username:juaoigor password database
#database Start a console on:juaoigor$pf