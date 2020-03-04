from flask import Flask
from flask import render_template
from classes import Database, Content, Event, Deck, Card
app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello World!'

@app.route('/deck/')
@app.route('/deck/<cid>')
def deck(cid = 0):

    dbm = Database()
    deck = Deck()
    deck.getDeck(dbm, cid)

    cont = Content()
    decks = cont.fetchDecksInEvent(dbm, cid)

    return render_template('deck.html', deck = deck, decks = decks)

@app.route('/event/')
@app.route('/event/<cid>')
def event(cid = None):
    return render_template('event.html', id = id)