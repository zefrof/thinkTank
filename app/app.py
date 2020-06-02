from flask import Flask, render_template, request, session, flash, redirect, url_for
from classes.general import Database, Content, User
from classes.event import Event
from classes.deck import Deck
from classes.card import Card
from eventFetchv2 import urlFilter
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

@app.route('/deck/<cid>')
def deck(cid = 0):

	dbm = Database()
	deck = Deck()
	deck.getDeck(dbm, cid)

	cont = Content()
	decks = cont.fetchDecksInEvent(dbm, cid)

	print(decks)

	return render_template('deck.html', deck = deck, decks = decks)

@app.route('/submit')
@app.route('/submit/')
def submit():
	return render_template('submit.html')


@app.route('/edit/', methods = ['POST', 'GET'])
def edit():
	#https://magic.wizards.com/en/articles/archive/mtgo-standings/legacy-super-qualifier-2020-05-15#decklists
	#https://magic.wizards.com/en/articles/archive/mtgo-standings/standard-league-2020-05-14
	cont = Content()
	dbm = Database()
	result = request.form

	event = Event()
	event.cid = urlFilter(result['link'])
	
	if event.cid == 0:
		return render_template('/eventExists.html')

	event.getEvent(dbm)

	formats = cont.getFormats(dbm, 1)
	ark = cont.getArk(dbm, 1)

	return render_template('edit.html', event = event, formats = formats, ark = ark)


#CMS
@app.route('/cms')
@app.route('/cms/')
def cmsIndex():
	user = User()
	try:
		check = user.verifyUser(session['id'])
		if check == True:
			return redirect(url_for('cmsHome'))
	except:
		pass

	return render_template('cms/index.html')

@app.route('/login/', methods = ['POST', 'GET'])
def cmsLogin():
	result = request.form

	user = User()
	sessionId = user.loginUser(result['email'], result['password'])

	if sessionId != False:
		session['id'] = sessionId
		return redirect(url_for('cmsHome'))
	else:
		return redirect(url_for('cmsIndex'))

@app.route('/createUser/', methods = ['POST', 'GET'])
def createUser():
	result = request.form

	user = User()
	check = user.createUser(result['username'], result['email'], result['password'], result['vPass'])

	if check == True:
		flash('Account created')
	elif check == False:
		flash("Your username/password is too short (3/8) or passwords don't match")

	return redirect(url_for('cmsIndex'))

@app.route('/cmshome')
@app.route('/cmshome/')
def cmsHome():
	user = User()
	try:
		check = user.verifyUser(session['id'])
		if check == True:
			return render_template('cms/home.html')
	except:
		pass

	return redirect(url_for('cmsIndex'))

@app.route('/editevent')
@app.route('/editevent/')
@app.route('/editevent/<cid>')
def editEvent(cid = 0):
	user = User()
	try:
		check = user.verifyUser(session['id'])
		if check == True:
			cont = Content()
			dbm = Database()

			formats = cont.getFormats(dbm, 1)
			ark = cont.getArk(dbm, 1)

			event = Event()
			if cid != 0:
				event.cid = cid
			else:
				event.cid = cont.eventQueue(dbm)

			event.getEvent(dbm)

			return render_template('cms/editEvent.html', event = event, formats = formats, ark = ark)
	except:
		pass

	return redirect(url_for('cmsIndex'))

@app.route('/saveevent/', methods = ['POST', 'GET'])
@app.route('/saveevent/<int:active>', methods = ['POST', 'GET'])
def saveEvent(active = 0):
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

			if deck.pilot == '':
				deck.pilot = 'Unknown'

			main = mainboard[i].splitlines()
			side = sideboard[i].splitlines()

			for c in main:
				spl = c.split(' | ')
				card = Card()
				card.copies = spl[0]
				
				try:
					card.scryfallId = spl[2]
				except:
					card.scryfallId = card.getCardId(spl[1], dbm)

				deck.cards.append(card)

			for c in side:
				spl = c.split(' | ')
				card = Card()
				card.copies = spl[0]

				try:
					card.scryfallId = spl[2]
				except:
					card.scryfallId = card.getCardId(spl[1], dbm)

				card.sideboard = 1
				deck.cards.append(card)

			event.decks.append(deck)
			#print("### Name: %s | Pilot: %s | Finish: %s | Archetype: %s" % (deckNames[i], deckPilot[i], finish[i], ark[i]))
		
		if active != 1:
			active = 0
		
		event.updateEvent(dbm, active)

	if active == 1:
		return redirect(url_for('editEvent'))
	else:
		return redirect(url_for('submit'))

@app.route('/delevent/<int:eid>')
def delEvent(eid = 0):
	user = User()
	try:
		check = user.verifyUser(session['id'])
		if check == True:
			dbm = Database()

			event = Event()
			event.cid = eid
			event.deleteEvent(dbm)

			return redirect(url_for('editEvent'))
		else:
			return redirect(url_for('home'))
	except:
		return redirect(url_for('home'))