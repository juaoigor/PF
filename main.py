from flask import Flask
from flask import render_template, request, url_for, flash, redirect, jsonify

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


#app.run(host='0.0.0.0', port=81)

#Database host address:juaoigor.mysql.pythonanywhere-services.com
#Username:juaoigor password database
#database Start a console on:juaoigor$pf