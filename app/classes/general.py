import time, json, requests, pymysql, string, random
from passlib.hash import bcrypt
from classes.event import Event
from classes.deck import Deck
from classes.card import Card, Face

class Content:
	
	def __init__(self):
		pass

	def fetchRecentEvents(self, dbm, fid, page):
		events = []
		if page < 0:
			page = 0

		offset = page * 10
		with dbm.con:
			if fid == 0:
				#Doing stupid pagination for now
				dbm.cur.execute("SELECT e.id, e.name, e.date, e.numPlayers FROM `events` e WHERE e.active = 1 ORDER BY e.date DESC LIMIT %s, 10 ", (offset, ))
				fetch = dbm.cur.fetchall()
			else:
				dbm.cur.execute("SELECT e.id, e.name, e.date, e.numPlayers FROM `events` e JOIN eventToFormat ef ON ef.eventId = e.id WHERE e.active = 1 AND ef.formatId = %s ORDER BY e.date DESC LIMIT %s, 10 ", (fid, offset))
				fetch = dbm.cur.fetchall()

			for x in fetch:
				event = Event()
				event.cid = x[0]
				event.name = x[1]
				event.date = x[2]
				event.numPlayers = x[3]

				dbm.cur.execute("SELECT d.id FROM decks d JOIN deckToEvent de ON de.deckId = d.id WHERE de.eventId = %s ORDER BY d.finish LIMIT 1 ", (event.cid, ))
				f = dbm.cur.fetchone()
				event.firstPlaceDeckId = f[0]

				events.append(event)

			return events

	def fetchDecksInEvent(self, dbm, deckId):
		decks = {}
		with dbm.con:
			dbm.cur.execute("SELECT e.id FROM events e JOIN deckToEvent de ON de.eventId = e.id WHERE de.deckId = %s", (deckId, ))
			if dbm.cur.rowcount == 1:
				eid = dbm.cur.fetchone()

				dbm.cur.execute("SELECT d.id, d.name, d.pilot FROM decks d JOIN deckToEvent de ON de.deckId = d.id WHERE de.eventId = %s", (eid[0], ))
				fetch = dbm.cur.fetchall()

				for f in fetch:
					decks[f[0]] = f[1] + " - " + f[2]
					
					#tDict = {'id' : f[0], 'name' : f[1]}
					#decks.append(tDict)
			else:
				print("!!! We have a deck (id: %s) not connected to an event" % (deckId))

		
		print(decks)
		return decks

	def getFormats(self, dbm, full = 0):
		formats = {}
		with dbm.con:
			if full == 0:
				pass
			elif full == 1:
				dbm.cur.execute("SELECT id, name FROM formats")
				fetch = dbm.cur.fetchall()

				for f in fetch:
					formats[f[0]] = f[1]
			return formats

	def getArk(self, dbm, full = 0):
		ark = {}
		with dbm.con:
			if full == 0:
				pass
			elif full == 1:
				dbm.cur.execute("SELECT id, name FROM archetypes ORDER BY name")
				fetch = dbm.cur.fetchall()

				for f in fetch:
					ark[f[0]] = f[1]
			return ark

	def eventQueue(self, dbm):
		with dbm.con:
			dbm.cur.execute("SELECT e.id FROM magic.events e WHERE active = 0 ORDER BY e.date DESC LIMIT 1")
			fetch = dbm.cur.fetchone()
			return fetch[0]

	def getMetagame(self, dbm, fid, startDate, endDate):
		with dbm.con:
			dbm.cur.execute("SELECT d.id, d.name, a.name, e.`date` FROM magic.decks d JOIN magic.archetypeToDeck atd ON atd.deckId = d.id JOIN magic.archetypes a ON a.id = atd.archetypeId JOIN magic.deckToEvent dte ON dte.deckId  = d.id JOIN magic.eventToFormat etf ON etf.eventId = dte.eventId JOIN magic.events e ON e.id = dte.eventId WHERE etf.formatId = %s AND e.`date` BETWEEN %s AND %s", (fid, startDate, endDate))

class Database:
	def __init__(self):

		self.con = pymysql.connect('database-1.cdoltwpzgxgp.us-east-2.rds.amazonaws.com', 'urza', 'hYbGFkPCgw@a', 'magic')
		self.cur = self.con.cursor()

		#Get auth token from TCGPlayer
		bearer = requests.post("https://api.tcgplayer.com/token",
			data = {
				"grant_type": "client_credentials",
				"client_id": "A7A184B3-923E-49EC-900F-204016D37EE2",
				"client_secret": "646E7BEC-556B-45EF-8746-3ADCF32FAB49",
			})
		self.token = bearer.json()

	def __del__(self):
		self.con.close()

class User:
	def __init__(self):
		self.username = ""

	def createUser(self, username, email, password, vPass):
		dbm = Database()

		if len(username) < 3:
			return False

		if len(password) < 8:
			return False

		if password != vPass:
			return False

		if len(email) <= 0:
			return False

		password = bcrypt.hash(password)

		with dbm.con:
			dbm.cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))

		return True

	def loginUser(self, email, password):
		dbm = Database()

		with dbm.con:
			dbm.cur.execute("SELECT id FROM users WHERE email = %s", (email, ))

			if dbm.cur.rowcount == 1:
				dbm.cur.execute("SELECT password FROM users WHERE email = %s", (email, ))
				fetch = dbm.cur.fetchone()
				check = bcrypt.verify(password, fetch[0])

				if check == True:
					sessionId = bcrypt.hash(email + ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(40)))
					dbm.cur.execute("UPDATE users SET session = %s WHERE email = %s", (sessionId, email))
					return sessionId
				else:
					return False
			else:
				return False

	def verifyUser(self, sessionId):
		dbm = Database()

		with dbm.con:
			dbm.cur.execute("SELECT UNIX_TIMESTAMP(lastLogin), id FROM users WHERE session = %s", (sessionId, ))
			fetch = dbm.cur.fetchone()
			if dbm.cur.rowcount == 1:
				if fetch[0] < (int(time.time()) - 1800):
					return False
				else:
					#Updates the timestamp
					dbm.cur.execute("UPDATE users SET lastLogin = CURRENT_TIMESTAMP WHERE id =  %s", (fetch[1], ))
					return True
			else:
				return False