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

@app.route('/cmsevents/')
@app.route('/cmsevents/<page>')
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

@app.route('/editevent/<cid>')
def editEvent(cid):
    dbm = Database()

    event = Event()
    event.getEvent(dbm, cid, 1)

    return render_template('editEvent.html', event = event)

@app.route('/saveevent/', methods = ['POST', 'GET'])
def saveEvent():
    if request.method == 'POST':
      result = request.form

      #print("### Name: %s | Date: %s | Format: %s | Players: %s" % (result['eventName'], result['eventDate'], result['format'], result['numPlayers']))

      deckNames = result.getlist('deckName')
      deckPilot = result.getlist('deckPilot')
      finish = result.getlist('finish')
      ark = result.getlist('archetype')
      for i in range(len(deckNames)):
          pass
          #print("### Name: %s | Pilot: %s | Finish: %s | Archetype: %s" % (deckNames[i], deckPilot[i], finish[i], ark[i]))


      return cmsEvents()