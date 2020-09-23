from flask import Flask, render_template, request, session, flash, redirect, url_for, json
from datetime import date, datetime, timedelta
from classes.general import Database, Content, User
from classes.event import Event
from classes.deck import Deck
from classes.card import Card
from eventFetch import urlFilter
app = Flask(__name__)
app.secret_key = b"\xf0/\xa1\xdb'\xfe!\xf68#\xb1\x19\x18\x01\xfb\x0f"

#FRONT END
@app.route('/')
def home():
	dbm = Database()
	cont = Content()

	events = cont.fetchRecentEvents(dbm, date.today())

	#raise ValueError('debug', e1)
	
	half = -(-len(events[0]) // 2) #https://stackoverflow.com/a/17511341
	e1 = events[0][:half]
	e2 = events[0][half:]

	return render_template('index.html', e1 = e1, e2 = e2, day = events[1])

@app.route('/event/<int:fid>')
def event(fid = 0):
	dbm = Database()
	cont = Content()

	events = cont.fetchRecentEvents(dbm, date.today(), fid)

	return render_template('event.html', events = events, fid = fid)

@app.route('/loadmore/', methods = ['POST'])
def loadMore():
	if request.method == 'POST':
		result = request.form
		d = datetime.strptime(result['day'], '%Y-%m-%d')
		d = d - timedelta(days = 1)

		dbm = Database()
		cont = Content()

		events = cont.fetchRecentEvents(dbm, d)

		jason = '{"events": ['
		for e in events[0]:
			jason = jason + '{{"eid":"{0}", "name":"{1}", "date":"{2}", "numPlayers":"{3}", "firstPlaceDeckId":"{4}"}},'.format(e.cid, e.name, e.date, e.numPlayers, e.firstPlaceDeckId)
		jason = jason[:-1]
		jason = jason + ']}'

		return jason
	else:
		return "She broke"

@app.route('/deck/<cid>')
def deck(cid = 0):

	dbm = Database()
	deck = Deck()
	deck.getDeck(dbm, cid)

	cont = Content()
	decks = cont.fetchDecksInEvent(dbm, cid)

	print(decks)

	return render_template('deck.html', deck = deck, decks = decks)

@app.route('/submit/')
def submit():
	return render_template('submit.html')


@app.route('/edit/', methods = ['POST', 'GET'])
def edit():
	cont = Content()
	dbm = Database()
	result = request.form

	event = Event()
	event.cid = urlFilter(result['link'])
	
	if event.cid == 0:
		flash("Event already exists! If you belive this to be an error, contact us in the footer.")
		return redirect(url_for('submit'))
	elif event.cid == -2:
		flash("Event submitted for manuel entry!")
		return redirect(url_for('submit'))
	elif event.cid == -1:
		flash("Not a valid URL")
		return redirect(url_for('submit'))
	
	event.getEvent(dbm)

	formats = cont.getFormats(dbm, 1)
	ark = cont.getArk(dbm, 1)

	return render_template('edit.html', event = event, formats = formats, ark = ark)

@app.route('/search/', methods = ['POST', 'GET'])
def search(fid = 0):
	if request.method == 'POST':
		result = request.form
		#print(result['searchSmall'])
		
		dbm = Database()
		cont = Content()
		events = cont.search(dbm, result['searchSmall'])

		if len(events) == 0:
			#TODO show user something legit here
			return "No Results Found"
		else:
			return render_template('event.html', events = events, fid = fid)

#CMS
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
			dbm = Database()
			cont = Content()
			ark = cont.getArk(dbm, 1)

			return render_template('cms/home.html', ark = ark)
	except:
		pass

	return redirect(url_for('cmsIndex'))

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
		deckPilot = result.getlist('deckPilot')
		finish = result.getlist('finish')
		ark = result.getlist('archetype')
		subArk = result.getlist('subArchetype')
		mainboard = result.getlist('mainboard')
		sideboard = result.getlist('sideboard')

		#print(len(deckPilot))
		#print(ark)
		#print(subArk)
		for i in range(len(deckPilot)):
			deck = Deck()
			deck.cid = deckIds[i]
			deck.pilot = deckPilot[i]
			deck.finish = finish[i]
			deck.archetype = ark[i]
			deck.subArk = subArk[i]

			if deck.pilot == '':
				deck.pilot = 'Unknown'

			main = mainboard[i].splitlines()
			side = sideboard[i].splitlines()

			for c in main:
				try:
					qty = c.strip().split(" ", 1)
					name = qty[1].split("*")

					card = Card()
					card.copies = qty[0].strip()
					card.name = name[0].strip()

					if len(name) == 2:
						card.scryfallId = name[1]
					else:
						card.scryfallId = card.getCardId(card.name, dbm)

					deck.cards.append(card)
				except Exception as e:
					print("save exception")
					print(e)
					flash("Formatting error!")
					return redirect(url_for('submit'))

			for c in side:
				try:
					qty = c.strip().split(" ", 1)
					name = qty[1].split("*")

					card = Card()
					card.copies = qty[0].strip()
					card.name = name[0].strip()

					if len(name) == 2:
						card.scryfallId = name[1]
					else:
						card.scryfallId = card.getCardId(card.name, dbm)

					card.sideboard = 1
					deck.cards.append(card)
				except Exception as e:
					print("save exception")
					print(e)
					flash("Formatting error!")
					return redirect(url_for('submit'))

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

@app.route('/skip/<int:eid>')
def skip(eid = 0):
	user = User()
	try:
		check = user.verifyUser(session['id'])
		if check == True:
			dbm = Database()

			event = Event()
			event.cid = eid
			event.skipEvent(dbm)

			return redirect(url_for('editEvent'))
		else:
			return redirect(url_for('home'))
	except:
		return redirect(url_for('home'))

@app.route('/archetype/', methods = ['POST', 'GET'])
def archetype():
	user = User()
	try:
		check = user.verifyUser(session['id'])
		if check == True:
			if request.method == 'POST':
				result = request.form
				dbm = Database()
				with dbm.con:
					dbm.cur.execute("SELECT id FROM archetypes WHERE name LIKE %s", (result['ark'], ))

					if dbm.cur.rowcount >= 1:
						flash("Archetype already exists.")
					else:
						dbm.cur.execute("INSERT INTO archetypes (name) VALUES (%s)", (result['ark'], ))
						flash("Archetype added.")

			return redirect(url_for('cmsIndex'))
		else:
			return redirect(url_for('home'))
	except:
		return redirect(url_for('home'))

@app.route('/subarchetype/', methods = ['POST', 'GET'])
def subArchetype():
	user = User()
	try:
		check = user.verifyUser(session['id'])
		if check == True:
			if request.method == 'POST':
				result = request.form
				dbm = Database()
				with dbm.con:
					dbm.cur.execute("SELECT id FROM subArchetypes WHERE name LIKE %s", (result['subArk'], ))

					if dbm.cur.rowcount >= 1:
						fetch = dbm.cur.fetchone()
						dbm.cur.execute("INSERT INTO subArchetypeToArchetype (subArchetypeId, archetypeId) VALUES (%s, %s)", (fetch[0], result['ark']))
					else:
						dbm.cur.execute("INSERT INTO subArchetypes (name) VALUES (%s)", (result['subArk'], ))
						arkId = dbm.cur.lastrowid
						dbm.cur.execute("INSERT INTO subArchetypeToArchetype (subArchetypeId, archetypeId) VALUES (%s, %s)", (arkId, result['ark']))

			return redirect(url_for('cmsIndex'))
		else:
			return redirect(url_for('home'))
	except Exception as e:
		print(e)
		return redirect(url_for('home'))

@app.route('/getsubark/', methods = ['POST', 'GET'])
def getSubArk():
	if request.method == 'POST':
		result = request.form
		dbm = Database()
	
		with dbm.con:
			dbm.cur.execute("SELECT id, name FROM subArchetypes s JOIN subArchetypeToArchetype saa ON saa.subArchetypeId = s.id WHERE saa.archetypeId = %s", (result['arkId']))
			fetch = dbm.cur.fetchall()

			return json.dumps(fetch)