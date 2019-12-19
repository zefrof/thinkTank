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

@app.route('/cms/')
def cmsHome():
    return render_template('cmsIndex.html')

@app.route('/cmsEvents/')
def cmsEvents():
    return render_template('cmsEvents.html')

@app.route('/editEvent/')
def editEvent():
    return render_template('editEvent.html')