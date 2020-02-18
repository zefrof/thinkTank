from flask import Flask, render_template, request, session, flash, redirect, url_for
from classes import Database, User, Content, Event, Deck, Card
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

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

@app.route('/login', methods = ['POST', 'GET'])
def cmsLogin():
    result = request.form

    user = User()
    sessionId = user.loginUser(result['username'], result['password'])

    if sessionId != False:
        session['id'] = sessionId
        return redirect(url_for('cmsEvents'))
    else:
        return redirect(url_for('cmsHome'))

@app.route('/createUser/', methods = ['POST', 'GET'])
def createUser():
    result = request.form

    user = User()
    check = user.createUser(result['username'], result['email'], result['password'], result['vPass'])

    if check == True:
        flash('Account created')
    elif check == False:
        flash("Your username/password is too short (3/8) or passwords don't match")

    return redirect(url_for('cmsHome'))

@app.route('/cmsevents/')
@app.route('/cmsevents/<page>')
def cmsEvents(page = 1):
    page = int(page)

    user = User()

    try:
        check = user.verifyUser(session['id'])
    except:
        return redirect(url_for('cmsHome'))

    if check == False:
        return redirect(url_for('cmsHome'))

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

      print(result)

      event = Event()
      event.name = result['eventName']
      event.date = result['eventDate']
      event.format = result['format']
      event.numPlayers = int(result['numPlayers'])
      #print("### Name: %s | Date: %s | Format: %s | Players: %s" % (result['eventName'], result['eventDate'], result['format'], result['numPlayers']))

      deckNames = result.getlist('deckName')
      deckPilot = result.getlist('deckPilot')
      finish = result.getlist('finish')
      ark = result.getlist('archetype')
      mainboard = result.getlist('mainboard')
      sideboard = result.getlist('sideboard')
      for i in range(len(deckNames)):
          deck = Deck()
          deck.name = deckNames[i]
          deck.pilot = deckPilot[i]
          deck.finish = finish[i]
          deck.archetype = ark[i]

          event.decks.append(deck)
          #print("### Name: %s | Pilot: %s | Finish: %s | Archetype: %s" % (deckNames[i], deckPilot[i], finish[i], ark[i]))


      return redirect(url_for('cmsEvents'))