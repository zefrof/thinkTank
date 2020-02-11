from flask import Flask, render_template, request
from classes import Database, Content, Event, Deck, Card
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
@app.route('/cmsEvents/<page>')
def cmsEvents(page = 1):
    page = int(page)

    dbm = Database()
    cont = Content()

    if page <= 0:
        page = 1
    events = cont.fetchEvents(dbm, page)

    #for event in events:
    #    print(event.name)

    return render_template('cmsEvents.html', events = events, page = page)

@app.route('/editEvent/<cid>')
def editEvent(cid):
    dbm = Database()

    event = Event()
    event.getEvent(dbm, cid, 1)

    return render_template('editEvent.html', event = event)

@app.route('/saveevent/', methods = ['POST', 'GET'])
def saveEvent():
    if request.method == 'POST':
      result = request.form
      #print(result['deckName[]'])
      print(result.getlist('deckName[]'))

      return cmsEvents()