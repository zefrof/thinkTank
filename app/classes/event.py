import time, json, requests, pymysql, string, random
from classes.deck import Deck
from classes.card import Card, Face

class Event:

	def __init__(self):
		self.name = ""
		self.date = ""
		self.format = ""
		self.numPlayers = 0
		self.source = ""
		self.decks = []

		self.cid = 0
		self.firstPlaceDeckId = 0

	def commitEvent(self, dbm):
		with dbm.con:

			dbm.cur.execute("INSERT INTO events (name, date, numPlayers, source) VALUES (%s, %s, %s, %s)", (self.name, self.date, self.numPlayers, self.source))
			self.cid = dbm.cur.lastrowid

			self.eventToFormat(dbm, self.cid)

			for deck in self.decks:
				deck.commitDeck(dbm, self.cid)

			print("### Inserted %s on %s in format %s" % (self.name, self.date, self.format))

	def updateEvent(self, dbm, active = 0):
		with dbm.con:
			dbm.cur.execute("UPDATE events SET name = %s, date = %s, numPlayers = %s, active = %s WHERE id = %s", (self.name, self.date, self.numPlayers, active, self.cid))

			self.eventToFormat(dbm, self.cid, 0)

			dbm.cur.execute("DELETE FROM deckToEvent WHERE eventId = %s", (self.cid, ))
			for deck in self.decks:
				deck.commitDeck(dbm, self.cid, 0)

	def eventToFormat(self, dbm, eventId, new = 1):
		with dbm.con:
			if new == 1:
				try:
					dbm.cur.execute("SELECT id FROM formats WHERE name = %s", (self.format, ))
					tmp = dbm.cur.fetchone()
					formatId = tmp[0]

					dbm.cur.execute("INSERT INTO eventToFormat (eventId, formatId) VALUES (%s, %s)", (eventId, formatId))
				except:
					print("!!! The %s format didn't exist for event %s on %s" % (self.format, self.name, self.date))

					dbm.cur.execute("INSERT INTO formats (name, active) VALUES (%s, 0)", (self.format, ))
					formatId = dbm.cur.lastrowid

					dbm.cur.execute("INSERT INTO eventToFormat (eventId, formatId) VALUES (%s, %s)", (eventId, formatId))
			elif new == 0:
				dbm.cur.execute("DELETE FROM eventToFormat WHERE eventId = %s", (eventId, ))

				#self.format is set to the ID in saveEvent (app.py), so fetching the ID from the name isn't necessary
				dbm.cur.execute("INSERT INTO eventToFormat (eventId, formatId) VALUES (%s, %s)", (eventId, self.format))

	def eventExists(self, dbm):
		with dbm.con:

			dbm.cur.execute("SELECT e.id FROM events e JOIN eventToFormat etf ON etf.eventId = e.id JOIN formats f ON f.id = etf.formatId WHERE e.name = %s AND e.date = %s AND f.name = %s ", (self.name, self.date, self.format))

			if dbm.cur.rowcount == 1:
				print("!!! %s on %s in format %s already exists" % (self.name, self.date, self.format))
				return True
			elif dbm.cur.rowcount > 1:
				print("&&& %s on %s in format %s has duplicates" % (self.name, self.date, self.format))
				return True
			else:
				return False

	def getEvent(self, dbm):
		with dbm.con:
			dbm.cur.execute("SELECT e.name, e.date, e.numPlayers, e.source, f.name as formatName FROM `events` e JOIN eventToFormat ef ON ef.eventId = e.id JOIN formats f ON f.id = ef.formatId WHERE e.id = %s", (self.cid, ))
			fetch = dbm.cur.fetchone()

			self.name = fetch[0]
			self.date = fetch[1]
			self.numPlayers = fetch[2]
			self.source = fetch[3]
			self.format = fetch[4]

			dbm.cur.execute("SELECT d.id, d.pilot, d.finish, a.id AS arkId, sa.name as subArkName FROM decks d LEFT JOIN archetypeToDeck ad ON ad.deckId = d.id LEFT JOIN archetypes a ON a.id = ad.archetypeId LEFT JOIN subArchetypeToDeck sad ON sad.deckId = d.id LEFT JOIN subArchetypes sa ON sa.id = sad.subArchetypeId JOIN deckToEvent de ON de.deckId = d.id WHERE de.eventId = %s ORDER BY `order`", (self.cid, ))
			fetch = dbm.cur.fetchall()

			for d in fetch:
				deck = Deck()
				deck.cid = d[0]
				deck.pilot = d[1]
				deck.finish = d[2]
				deck.archetype = d[3]
				deck.subArk = d[4]

				dbm.cur.execute("SELECT c.id, c.name, cd.copies, cd.sideboard FROM cards c JOIN cardToDeck cd ON cd.cardId = c.id WHERE cd.deckId = %s", (deck.cid, ))
				fetch2 = dbm.cur.fetchall()

				for c in fetch2:
					card = Card()
					card.scryfallId = c[0]
					card.name = c[1]
					card.copies = int(c[2])
					card.sideboard = int(c[3])
					if card.sideboard == 0:
						deck.cards.append(card)
						deck.mainboardCount += card.copies
					elif card.sideboard == 1:
						deck.sideboard.append(card)
						deck.sideboardCount += card.copies

				self.decks.append(deck)

	def deleteEvent(self, dbm):
		with dbm.con:
			dbm.cur.execute("SELECT d.id FROM magic.decks d JOIN magic.deckToEvent dte ON dte.deckId = d.id WHERE dte.eventId = %s", (self.cid, ))
			fetch = dbm.cur.fetchall()

			for d in fetch:
				dbm.cur.execute("DELETE FROM magic.decks WHERE id = %s", (d[0], ))

			dbm.cur.execute("DELETE FROM magic.events WHERE id = %s", (self.cid, ))

	def skipEvent(self, dbm):
		with dbm.con:
			dbm.cur.execute("UPDATE events SET active = 2 WHERE id = %s", (self.cid, ))
			