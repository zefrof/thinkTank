import time, json, requests, pymysql, string, random
from classes.card import Card, Face

class Deck:

	def __init__(self):
		self.pilot = ""
		self.finish = ""
		self.cards = []
		self.sideboard = []
		self.archetype = ""
		self.subArk = ""

		self.cid = 0
		self.price = 0
		self.ord = 0 #display order
		self.mainboardCount = 0
		self.sideboardCount = 0

	def commitDeck(self, dbm, eventId, new = 1):
		with dbm.con:
			if new == 1:
				dbm.cur.execute("INSERT INTO decks (pilot, finish, `order`) VALUES (%s, %s, %s)", (self.pilot, self.finish, self.ord))
				deckId = dbm.cur.lastrowid

				self.deckToEvent(dbm, deckId, eventId)

				for card in self.cards:
					card.cardToDeck(dbm, deckId)
			elif new == 0:
				dbm.cur.execute("UPDATE decks SET pilot = %s, finish = %s WHERE id = %s", (self.pilot, self.finish, self.cid))
				
				self.deckToEvent(dbm, self.cid, eventId)
				if self.archetype != "0":
					self.commitArchetype(dbm)
				if self.subArk != "0":
					self.insertSubArkToDeck(dbm)

				dbm.cur.execute("DELETE FROM cardToDeck WHERE deckId = %s", (self.cid, ))
				for card in self.cards:
					card.cardToDeck(dbm, self.cid)

	def deckToEvent(self, dbm, deckId, eventId):
		with dbm.con:
			dbm.cur.execute("INSERT INTO deckToEvent (deckId, eventId) VALUES (%s, %s)", (deckId, eventId))

	def commitArchetype(self, dbm):
		with dbm.con:
			dbm.cur.execute("DELETE FROM archetypeToDeck WHERE deckId = %s", (self.cid, ))

			#self.archetype is set to the ID in saveEvent (app.py), so fetching the ID from the name isn't necessary
			dbm.cur.execute("INSERT INTO archetypeToDeck (archetypeId, deckId) VALUES (%s, %s)", (self.archetype, self.cid))

	def insertSubArkToDeck(self, dbm):
		with dbm.con:
			dbm.cur.execute("DELETE FROM subArchetypeToDeck WHERE deckId = %s", (self.cid, ))
			dbm.cur.execute("INSERT INTO subArchetypeToDeck (subArchetypeId, deckId) VALUES (%s, %s)", (self.subArk, self.cid))

	def getDeck(self, dbm, cid):
		with dbm.con:
			dbm.cur.execute("SELECT d.id, d.pilot, d.finish, sa.name AS subArkName FROM decks d LEFT JOIN subArchetypeToDeck sad ON sad.deckId = d.id LEFT JOIN subArchetypes sa ON sa.id = sad.subArchetypeId WHERE d.id = %s", (cid, ))
			fetch = dbm.cur.fetchone()
			
			self.cid = cid
			self.pilot = fetch[1]
			self.finish = fetch[2]
			self.subArk = fetch[3]

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
				try:
					card.imageUrl = c[4]
					#showImage in app.js has issues with quotes
					card.altText = c[5].replace("'", "&apos;")
				except:
					pass
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

				dbm.cur.execute("SELECT p.price, p.foilPrice FROM magic.prices p JOIN cardToPrice ctp ON ctp.priceId = p.id WHERE ctp.cardId = %s ORDER BY p.`timestamp` DESC", (card.scryfallId, ))
				price = dbm.cur.fetchone()

				card.curPrice = price[0]
				card.curFoilPrice = price[1]
				self.price = self.price + card.curPrice

				typ = card.typeLine.split('—')[0]
				typ = typ.split()[-1].strip()
				print(typ)

				if sideboard == 2:
					commander.append(card)
				elif sideboard == 3:
					companion.append(card)
				elif card.sideboard == 1:
					sideboard.append(card)
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
				
			if len(commander) > 0:
				card = Card()
				card.name = "Commander"
				card.copies = 0
				self.cards.append(card)
				self.cards.extend(commander)
			if len(creature) > 0:
				card = Card()
				card.name = "Creatures"
				card.copies = 0
				self.cards.append(card)
				self.cards.extend(creature)
			if len(instant) > 0:
				card = Card()
				card.name = "Instants"
				card.copies = 0
				self.cards.append(card)
				self.cards.extend(instant)
			if len(sorcery):
				card = Card()
				card.name = "Sorceries"
				card.copies = 0
				self.cards.append(card)
				self.cards.extend(sorcery)
			if len(enchant):
				card = Card()
				card.name = "Enchantments"
				card.copies = 0
				self.cards.append(card)
				self.cards.extend(enchant)
			if len(artifact):
				card = Card()
				card.name = "Artifacts"
				card.copies = 0
				self.cards.append(card)
				self.cards.extend(artifact)
			if len(walker):
				card = Card()
				card.name = "Planeswalkers"
				card.copies = 0
				self.cards.append(card)
				self.cards.extend(walker)
			if len(land):
				card = Card()
				card.name = "Lands"
				card.copies = 0
				self.cards.append(card)
				self.cards.extend(land)
			if len(companion):
				card = Card()
				card.name = "Companion"
				card.copies = 0
				self.cards.append(card)
				self.cards.extend(companion)
			if len(sideboard):
				card = Card()
				card.name = "Sideboard"
				card.copies = 0
				self.cards.append(card)
				self.cards.extend(sideboard)

	def toString(self):
		s = '{"pilot":"%s", "finish":"%s", "archetype":"%s"}' % (self.pilot, self.finish, self.archetype)

		for card in self.cards:
			s += card.toString()

		return s