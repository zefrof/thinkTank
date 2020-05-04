from flask import Flask, render_template, request, session, flash, redirect, url_for
from classes.general import Database, Content, User
from classes.event import Event
from classes.deck import Deck
from classes.card import Card
app = Flask(__name__)
app.secret_key = b"\xf0/\xa1\xdb'\xfe!\xf68#\xb1\x19\x18\x01\xfb\x0f"

#FRONT END
@app.route('/')
@app.route('/<int:page>')
def home(fid = 0, page = 0):
	dbm = Database()
	cont = Content()

	events = cont.fetchRecentEvents(dbm, fid, page)
	
	half = len(events) // 2
	e1 = events[:half]
	e2 = events[half:]

	return render_template('index.html', e1 = e1, e2 = e2, page = page, fid = fid)

@app.route('/event/<int:fid>')
@app.route('/event/<int:fid>/<int:page>')
def event(fid = 0, page = 0):
	dbm = Database()
	cont = Content()

	events = cont.fetchRecentEvents(dbm, fid, page)

	return render_template('event.html', events = events, page = page, fid = fid)

@app.route('/deck/')
@app.route('/deck/<cid>')
def deck(cid = 0):

	dbm = Database()
	deck = Deck()
	deck.getDeck(dbm, cid)

	cont = Content()
	decks = cont.fetchDecksInEvent(dbm, cid)

	print(decks)

	return render_template('deck.html', deck = deck, decks = decks)

#CMS
@app.route('/cms/')
def cmsHome():
	user = User()
	try:
		check = user.verifyUser(session['id'])
		if check == True:
			return redirect(url_for('cmsEvents'))
	except:
		pass

	return render_template('cms/cmsIndex.html')

@app.route('/login/', methods = ['POST', 'GET'])
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

#@app.route('/cmsevents/')
#@app.route('/cmsevents/<page>')
#def cmsEvents(page = 1):
	#page = int(page)
	#user = User()

	#try:
	#	check = user.verifyUser(session['id'])
	#except:
	#	print("no sess")
	#	return redirect(url_for('cmsHome'))

	#if check == False:
	#	return redirect(url_for('cmsHome'))

	#dbm = Database()
	#cont = Content()

	#if page <= 0:
	#	page = 1
	#events = cont.fetchEvents(dbm, page)

	#for event in events:
	#    print(event.name)

	#return render_template('cms/cmsEvents.html', events = events, page = page)

@app.route('/editevent/<cid>')
def editEvent(cid):
	dbm = Database()
	user = User()
	cont = Content()

	try:
		check = user.verifyUser(session['id'])
	except:
		return redirect(url_for('cmsHome'))

	formats = cont.getFormats(dbm, 1)
	ark = cont.getArk(dbm, 1)

	event = Event()
	event.cid = cid
	event.getEvent(dbm, cid, 1)

	return render_template('cms/editEvent.html', event = event, formats = formats, ark = ark)

@app.route('/saveevent/', methods = ['POST', 'GET'])
def saveEvent():
	if request.method == 'POST':
		result = request.form
		dbm = Database()

		#print(result.getlist('pid'))

		event = Event()
		event.cid = result['cid']
		event.name = result['eventName']
		event.date = result['eventDate']
		event.format = result['format']
		event.numPlayers = int(result['numPlayers'])
		#print("### Name: %s | Date: %s | Format: %s | Players: %s" % (result['eventName'], result['eventDate'], result['format'], result['numPlayers']))

		deckIds = result.getlist('did')
		deckNames = result.getlist('deckName')
		deckPilot = result.getlist('deckPilot')
		finish = result.getlist('finish')
		ark = result.getlist('archetype')
		mainboard = result.getlist('mainboard')
		sideboard = result.getlist('sideboard')
		for i in range(len(deckNames)):
			deck = Deck()
			deck.cid = deckIds[i]
			deck.name = deckNames[i]
			deck.pilot = deckPilot[i]
			deck.finish = finish[i]
			deck.archetype = ark[i]

			main = mainboard[i].splitlines()
			side = sideboard[i].splitlines()

			for c in main:
				spl = c.split(' | ')
				card = Card()
				card.copies = spl[0]
				card.scryfallId = spl[2]
				deck.cards.append(card)

			for c in side:
				spl = c.split(' | ')
				card = Card()
				card.copies = spl[0]
				card.scryfallId = spl[2]
				card.sideboard = 1
				deck.cards.append(card)

			event.decks.append(deck)
			#print("### Name: %s | Pilot: %s | Finish: %s | Archetype: %s" % (deckNames[i], deckPilot[i], finish[i], ark[i]))
		event.updateEvent(dbm)

	return redirect(url_for('cmsEvents'))

@app.route('/searchevent/', methods = ['POST', 'GET'])
def searchEvent():
	dbm = Database()
	result = request.form

	cont = Content()
	events = cont.searchEventNames(dbm, result['name'])

	return render_template('cms/cmsEvents.html', events = events, page = 1)
