import time, json, requests, pymysql, string, random
from passlib.hash import bcrypt
from datetime import datetime, timedelta
from collections import defaultdict
from classes.event import Event
from classes.deck import Deck
from classes.card import Card, Face

class Content:
	
	def __init__(self):
		pass

	def fetchRecentEvents(self, dbm, day, fid = 0):
		events = []
		with dbm.con:
			while(1):
				if fid == 0:
					dbm.cur.execute("SELECT e.id, e.name, e.date, e.numPlayers FROM `events` e WHERE e.active = 1 AND e.`date` = %s ORDER BY e.date", (day.strftime('%Y-%m-%d'), ))
					fetch = dbm.cur.fetchall()
				else:
					dbm.cur.execute("SELECT e.id, e.name, e.date, e.numPlayers FROM `events` e JOIN eventToFormat ef ON ef.eventId = e.id WHERE e.active = 1 AND e.`date` = %s AND ef.formatId = %s ORDER BY e.date DESC", (day, fid))
					fetch = dbm.cur.fetchall()
				if len(fetch) == 0:
					day = day - timedelta(days = 1)
				else:
					break

			#if len(fetch) == 0:
			#	self.fetchRecentEvents(dbm, day - timedelta(days = 1), fid)

			for x in fetch:
				event = Event()
				event.cid = x[0]
				event.name = x[1]
				event.date = x[2]
				event.numPlayers = x[3]

				dbm.cur.execute("SELECT d.id FROM decks d JOIN deckToEvent de ON de.deckId = d.id WHERE de.eventId = %s AND d.`order` = 0 ORDER BY d.`order`", (event.cid, ))
				f = dbm.cur.fetchone()
				event.firstPlaceDeckId = f[0]

				events.append(event)

			return events, day

	def fetchDecksInEvent(self, dbm, deckId):
		decks = {}
		with dbm.con:
			dbm.cur.execute("SELECT e.id FROM events e JOIN deckToEvent de ON de.eventId = e.id WHERE de.deckId = %s", (deckId, ))
			if dbm.cur.rowcount == 1:
				eid = dbm.cur.fetchone()

				dbm.cur.execute("SELECT d.id, d.pilot, sa.name AS subArkName FROM decks d JOIN deckToEvent de ON de.deckId = d.id JOIN subArchetypeToDeck sad ON sad.deckId = d.id JOIN subArchetypes sa ON sa.id = sad.subArchetypeId WHERE de.eventId = %s ORDER BY `order`", (eid[0], ))
				fetch = dbm.cur.fetchall()

				for f in fetch:
					#TODO
					decks[f[0]] = f[2] + " - " + f[1]
					
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
			dbm.cur.execute("SELECT d.id, a.name, e.`date` FROM magic.decks d JOIN magic.archetypeToDeck atd ON atd.deckId = d.id JOIN magic.archetypes a ON a.id = atd.archetypeId JOIN magic.deckToEvent dte ON dte.deckId  = d.id JOIN magic.eventToFormat etf ON etf.eventId = dte.eventId JOIN magic.events e ON e.id = dte.eventId WHERE etf.formatId = %s AND e.`date` BETWEEN %s AND %s", (fid, startDate, endDate))

	def search(self, dbm, searchTearm):
		events = []
		with dbm.con:
			eventSearch = "%" + searchTearm + "%"
			dbm.cur.execute("SELECT e.id, e.name, e.date, e.numPlayers FROM `events` e WHERE e.active = 1 AND e.name LIKE %s ORDER BY e.date DESC", (eventSearch, ))
			fetch = dbm.cur.fetchall()

			dbm.cur.execute("SELECT e.id, e.name, e.date, e.numPlayers FROM archetypes a JOIN archetypeToDeck atd ON atd.archetypeId = a.id JOIN deckToEvent dte ON atd.deckId = dte.deckId JOIN events e ON e.id = dte.eventId WHERE a.name LIKE %s", (eventSearch, ))
			fetch = fetch + dbm.cur.fetchall()

			for x in fetch:
				event = Event()
				event.cid = x[0]
				event.name = x[1]
				event.date = x[2]
				event.numPlayers = x[3]

				dbm.cur.execute("SELECT d.id FROM decks d JOIN deckToEvent de ON de.deckId = d.id WHERE de.eventId = %s ORDER BY d.`order` LIMIT 1 ", (event.cid, ))
				f = dbm.cur.fetchone()
				event.firstPlaceDeckId = f[0]

				events.append(event)

			return events

	def suggester(self, dbm, cards_input, mtg_format, ignore_list):
		percent = 0.005
		
		card_query = 'SELECT c.id FROM cards c WHERE ( '
		for c in cards_input:
			card_query += 'c.name LIKE %s OR '

		card_query = card_query[:-3]
		card_query += ') AND c.uniqueCard = 1;'

		filtr_str = ""
		for ig in ignore_list:
			#https://stackoverflow.com/questions/8775460/mysql-python-like-wildcard
			filtr_str = filtr_str + 'AND u.typeLine NOT LIKE {0} '.format('"%%' + ig + '%%"')

		sugg_str = 'SELECT u.card1_id, u.card2_id, u.percent FROM (SELECT ctc.*, c.typeLine FROM cardToCard ctc LEFT JOIN cards c ON c.id = ctc.card2_id WHERE ctc.card1_id = %s UNION SELECT ctc.*, c.typeLine FROM cardToCard ctc LEFT JOIN cards c ON c.id = ctc.card1_id WHERE ctc.card2_id = %s) AS u WHERE u.percent > %s AND u.`format` = %s ' + filtr_str + 'LIMIT 15 '

		print(sugg_str)

		with dbm.con:
			dbm.cur.execute(card_query, tuple(cards_input))
			card_ids = dbm.cur.fetchall()
			card_ids = [x for x, in card_ids]
			
			results = []
			for cId in card_ids:
				#TODO if no results are found with .005% try lower %
				dbm.cur.execute(sugg_str, (cId, cId, percent, mtg_format))
				results.append(dbm.cur.fetchall())

			card_dict = defaultdict(set)
			for x in results:
				for item in x:
					#print(item[0] + "   " + item[1])
					if item[0] == card_ids[0]:
						#print("match 1")
						card_dict[item[1]].add(item[2])
					else:
						#print("match 2")
						card_dict[item[0]].add(item[2])
			#print(card_dict)

			#print(max_card(card_dict))

			if len(card_dict) == 0:
				return "[]"
			
			# Exclude Basic lands
			# Should probably do thise somewhere else for speed purposes
			dbm.cur.execute("SELECT c.id FROM cards c WHERE (c.name = 'Plains' OR c.name = 'Island' OR c.name = 'Swamp' OR c.name = 'Mountain' OR c.name = 'Forest') AND c.uniqueCard = 1;")
			blacklist = dbm.cur.fetchall()
			blacklist = [x for x, in blacklist]
			#Not sure if this or adding "AND ctc.card1_id <> '' to search query would be better"
			blacklist.extend(card_ids)
			
			results = []
			offset = 0
			while len(results) < 11:
				results.extend(self.max_card(card_dict, offset))
				results = [i for i in results if i not in blacklist]
				offset += 1

			return results
	
	# A support function for suggester()
	def max_card(self, db, offset = 0):
		maxcount = max(len(v) for v in db.values())
		return [k for k, v in db.items() if len(v) == maxcount - offset]

class Database:
	def __init__(self):

		self.con = pymysql.connect(host='HOST', user='USER', password='PASS', database='DB')
		self.cur = self.con.cursor()

		#Get auth token from TCGPlayer
		#bearer = requests.post("https://api.tcgplayer.com/token",
		#	data = {
		#		"grant_type": "client_credentials",
		#		"client_id": "A7A184B3-923E-49EC-900F-204016D37EE2",
		#		"client_secret": "646E7BEC-556B-45EF-8746-3ADCF32FAB49",
		#	})
		#self.token = bearer.json()

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