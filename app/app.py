from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello World!'

@app.route('/deck/')
@app.route('/deck/<id>')
def deck(id = None):
    return render_template('deck.html', id = id)

@app.route('/event/')
@app.route('/event/<id>')
def deck(id = None):
    return render_template('event.html', id = id)