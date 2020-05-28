import time, json, requests, pymysql, string, random
from classes.card import Card, Face

class Deck:

	def __init__(self):
		self.name = ""
		self.pilot = ""
		self.finish = 0
		self.cards = []
		self.sideboard = []
		self.archetype = ""

		self.cid = 0

	def commitDeck(self, dbm, eventId, new = 1):
		with dbm.con:
			if new == 1:
				dbm.cur.execute("INSERT INTO decks (name, pilot, finish) VALUES (%s, %s, %s)", (self.name, self.pilot, self.finish))
				deckId = dbm.cur.lastrowid

				self.deckToEvent(dbm, deckId, eventId)
				self.commitArchetype(dbm, deckId)

				for card in self.cards:
					card.cardToDeck(dbm, deckId)
			elif new == 0:
				dbm.cur.execute("UPDATE decks SET name = %s, pilot = %s, finish = %s WHERE id = %s", (self.name, self.pilot, self.finish, self.cid))

				self.deckToEvent(dbm, self.cid, eventId)
				self.commitArchetype(dbm, self.cid, 0)

				dbm.cur.execute("DELETE FROM cardToDeck WHERE deckId = %s", (self.cid, ))
				for card in self.cards:
					card.cardToDeck(dbm, self.cid)

	def deckToEvent(self, dbm, deckId, eventId):
		with dbm.con:
			dbm.cur.execute("INSERT INTO deckToEvent (deckId, eventId) VALUES (%s, %s)", (deckId, eventId))

	def commitArchetype(self, dbm, deckId, new = 1):
		with dbm.con:
			if new == 1:
				dbm.cur.execute("SELECT id FROM archetypes WHERE name = %s", (self.archetype, ))

				if dbm.cur.rowcount == 0:
					dbm.cur.execute("INSERT INTO archetypes (name, active) VALUES (%s, %s)", (self.archetype, 1))
					dbm.cur.execute("SELECT id FROM archetypes WHERE name = %s", (self.archetype, ))

				tmp = dbm.cur.fetchone()
				arkId = tmp[0]

				dbm.cur.execute("INSERT INTO archetypeToDeck (archetypeId, deckId) VALUES (%s, %s)", (arkId, deckId))
			elif new == 0:
				dbm.cur.execute("DELETE FROM archetypeToDeck WHERE deckId = %s", (deckId, ))

				#self.archetype is set to the ID in saveEvent (app.py), so fetching the ID from the name isn't necessary
				dbm.cur.execute("INSERT INTO archetypeToDeck (archetypeId, deckId) VALUES (%s, %s)", (self.archetype, deckId))

	def getDeck(self, dbm, cid):
		with dbm.con:
			dbm.cur.execute("SELECT d.id, d.name, d.pilot, d.finish, a.name AS arkName FROM decks d JOIN archetypeToDeck ad ON ad.deckId = d.id JOIN archetypes a ON a.id = ad.archetypeId WHERE d.id = %s", (cid, ))
			fetch = dbm.cur.fetchone()

			self.cid = cid
			self.name = fetch[1]
			self.pilot = fetch[2]
			self.finish = fetch[3]
			self.archetype = fetch[4]

			dbm.cur.execute("SELECT c.id, c.name, c.typeLine, c.manaCost, m.mediaUrl, m.altText, cd.copies, cd.sideboard FROM cards c LEFT JOIN mediaToCard mc ON mc.cardId = c.id LEFT JOIN media m ON m.id = mc.mediaId JOIN cardToDeck cd ON cd.cardId = c.id WHERE cd.deckId = %s", (cid, ))
			fetch = dbm.cur.fetchall()

			creature = []
			instant = []
			sorcery = []
			enchant = []
			artifact = []
			land = []
			walker = []
			commander = []
			companion = []
			sideboard = []

			for c in fetch:
				card = Card()
				card.scryfallId = c[0]
				card.name = c[1]
				card.typeLine = c[2]
				card.manaCost = c[3]
				card.imageUrl = c[4]
				card.altText = c[5]
				card.copies = int(c[6])
				card.sideboard = int(c[7])
				
				dbm.cur.execute("SELECT cf.name, m.mediaUrl, m.altText FROM cardFace cf JOIN cardFaceToCard cfc ON cfc.cardFaceId = cf.id JOIN cards c ON c.id = cfc.cardId JOIN cardFaceToMedia cfm ON cfm.cardFaceId = cf.id JOIN media m ON m.id = cfm.mediaId WHERE c.id = %s ", (card.scryfallId, ))
				fetch2 = dbm.cur.fetchall()

				for f in fetch2:
					face = Face()
					face.name = f[0]
					face.imageUrl = f[1]
					face.altText = f[2]
					card.faces.append(face)

				typ = card.typeLine.split('—')[0]
				typ = typ.split()[-1].strip()
				print(typ)

				if sideboard == 2:
					commander.append(card)
				elif sideboard == 3:
					companion.append(card)
				elif typ == "Creature":
					creature.append(card)
				elif typ == "Instant":
					instant.append(card)
				elif typ == "Sorcery":
					sorcery.append(card)
				elif typ == "Enchantment":
					enchant.append(card)
				elif typ == "Artifact":
					artifact.append(card)
				elif typ == "Planeswalker":
					walker.append(card)
				elif typ == "Land":
					land.append(card)
				elif card.sideboard == 1:
					sideboard.append(card)
				
			self.cards.extend(commander)
			self.cards.extend(creature)
			self.cards.extend(instant)
			self.cards.extend(sorcery)
			self.cards.extend(enchant)
			self.cards.extend(artifact)
			self.cards.extend(walker)
			self.cards.extend(land)
			self.cards.extend(companion)
			self.cards.extend(sideboard)

	def toString(self):
		s = '{"name":"%s", "pilot":"%s", "finish":"%s", "archetype":"%s"}' % (self.name, self.pilot, self.finish, self.archetype)

		for card in self.cards:
			s += card.toString()

		return s