import time, json, requests, pymysql, string, random

class Card:

	def __init__(self):
		#Gathered from Scyrfall
		self.scryfallId = ""
		self.tcgplayerId = 0
		self.name = ""
		self.releaseDate = ""
		self.layout = ""
		self.manaCost = ""
		self.cmc = 0.0
		self.typeLine = ""
		self.oracleText = ""
		self.flavorText = ""
		self.power = ""
		self.toughness = ""
		self.loyalty = ""
		self.colors = []
		self.colorIden = []
		self.legalities = {
			"standard" : "",
			"future" : "",
			"historic" : "",
			"pioneer" : "",
			"modern" : "",
			"legacy" : "",
			"pauper" : "",
			"vintage" : "",
			"penny" : "",
			"commander" : "",
			"brawl" : "",
			"duel" : "",
			"oldschool" : ""
		}
		self.reserved = 0
		self.foil = 0
		self.nonfoil = 0
		self.oversized = 0
		self.promo = 0
		self.reprint = 0
		self.variation = 0
		self.mtgSet = ""
		self.setCode = ""
		self.setType = ""
		self.collectorNumber = ""
		self.rarity = ""
		self.watermark = ""
		self.artist = ""
		self.textless = 0
		self.curPrice = 0.0
		self.curFoilPrice = 0.0
		self.imageUrl = ""
		self.altText = ""

		#Array of card faces
		self.faces = []

		#To help the Deck class
		self.sideboard = 0
		self.copies = 0

	def setCard(self, json, dbm):
		self.scryfallId = json['id']

		try:
			self.tcgplayerId = json['tcgplayer_id']
		except:
			pass

		try:
			self.name = json['name']
		except:
			pass
		
		try:
			self.releaseDate = json['released_at']
		except:
			pass
		
		try:
			self.layout = json['layout']
		except:
			pass

		try:
			self.manaCost = json['mana_cost']
		except:
			pass

		try:
			self.cmc = json['cmc']
		except:
			pass

		try:
			self.typeLine = json['type_line']
		except:
			pass

		try:
			self.oracleText = json['oracle_text']
		except:
			pass

		try:
			self.flavorText = json['flavor_text']
		except:
			pass

		try:
			self.power = json['power']
		except:
			pass

		try:
			self.toughness = json['toughness']
		except:
			pass

		try:
			self.loyalty = json['loyalty']
		except:
			pass

		try:
			for c in json['colors']:
				self.colors.append(c)
		except:
			pass

		try:
			for c in json['color_identity']:
				self.colorIden.append(c)
		except:
			pass

		self.setLegalities(json['legalities'])

		self.reserved = json['reserved']

		if json['foil'] == False:
			self.foil = 0
		else:
			self.foil = 1

		if json['nonfoil'] == False:
			self.nonfoil = 0
		else:
			self.nonfoil = 1

		self.oversized = json['oversized']
		self.promo = json['promo']
		self.reprint = json['reprint']
		self.variation = json['variation']
		self.mtgSet = json['set_name']
		self.setCode = json['set']

		try:
			self.setType = json['set_type']
		except:
			pass

		self.collectorNumber = json['collector_number']
		self.rarity = json['rarity']

		try:
			self.watermark = json['watermark']
		except:
			pass

		try:
			self.artist = json['artist']
		except:
			pass

		try:
			self.textless = json['textless']
		except:
			pass

		if self.tcgplayerId != "":
			self.setPrice(self.tcgplayerId, dbm.token)

		try:
			self.imageUrl = json['image_uris']['normal']
		except:
			pass

		try:
			if len(json['card_faces']) > 0:
				for f in json['card_faces']:
					face = Face()
					face.setFace(f)
					self.faces.append(face)
		except:
			pass

	def getCard(self, dbm, cid, full = 0):
		with dbm.con:
			if full == 1:
				dbm.cur.execute("SELECT c.* FROM cards c WHERE c.id = %s LIMIT 1", (cid, ))
				fetch = dbm.cur.fetchone()

				self.scryfallId = fetch[0]
				self.name = fetch[1]
				self.releaseDate = fetch[2]
				self.layout = fetch[3]
				self.manaCost = fetch[4]
				self.cmc = fetch[5]
				self.typeLine = fetch[6]
				self.oracleText = fetch[7]
				self.flavorText = fetch[8]
				self.power = fetch[9]
				self.toughness = fetch[10]
				self.loyalty = fetch[11]
				self.reserved = fetch[12]
				self.foil = fetch[13]
				self.nonfoil = fetch[14]
				self.oversized = fetch[15]
				self.promo = fetch[16]
				self.reprint = fetch[17]
				self.variation = fetch[18]
				self.collectorNumber = fetch[19]
				self.rarity = fetch[20]
				self.watermark = fetch[21]
				self.artist = fetch[22]
				self.textless = fetch[23]
			elif full == 0:
				dbm.cur.execute("SELECT c.id, c.name FROM cards c WHERE c.id = %s LIMIT 1", (cid, ))
				fetch = dbm.cur.fetchone()

				self.scryfallId = fetch[0]
				self.name = fetch[0]

	def getCardId(self, name, dbm):
		with dbm.con:
			dbm.cur.execute("SELECT id FROM cards WHERE name = %s ", (name, ))

			if dbm.cur.rowcount > 0:
				fetch = dbm.cur.fetchone()
			else:
				tempName = '%' + name + '%'
				fill = '%//%'

				dbm.cur.execute("SELECT id FROM `cards` WHERE `name` LIKE %s AND `name` LIKE %s ", (tempName, fill))
				fetch = dbm.cur.fetchone()

			return fetch[0]

	def commitCard(self, dbm):
		with dbm.con:
			dbm.cur.execute("SELECT c.id, c.timestamp FROM cards c WHERE c.id = %s", (self.scryfallId, ))

			#Card already exists
			if dbm.cur.rowcount == 1:
				fetch = dbm.cur.fetchone()

				#If it's been a month since last update
				if fetch[1] < (int(time.time()) - 2629800):
					print("Updating %s from %s" % (self.name, self.setCode))

					dbm.cur.execute("UPDATE cards SET name = %s, releaseDate = %s, layout = %s, manaCost = %s, cmc = %s, typeLine = %s, oracleText = %s, flavorText = %s, power = %s, toughness = %s, loyalty = %s, reserved = %s, foil = %s, nonfoil = %s, oversized = %s, promo = %s, reprint = %s, variation = %s, collectorNumber = %s, rarity = %s, watermark = %s, artist = %s, textless = %s WHERE id = %s", (self.name, self.releaseDate, self.layout, self.manaCost, self.cmc, self.typeLine, self.oracleText, self.flavorText, self.power, self.toughness, self.loyalty, self.reserved, self.foil, self.nonfoil, self.oversized, self.promo, self.reprint, self.variation, self.collectorNumber, self.rarity, self.watermark, self.artist, self.textless, self.scryfallId))

					self.commitLegalities(dbm)
					self.commitImage(dbm)

				self.commitPrice(dbm)

			#Card doesn't exist
			else:
				dbm.cur.execute("INSERT INTO cards (id, name, releaseDate, layout, manaCost, cmc, typeLine, oracleText, flavorText, power, toughness, loyalty, reserved, foil, nonfoil, oversized, promo, reprint, variation, collectorNumber, rarity, watermark, artist, textless) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (self.scryfallId, self.name, self.releaseDate, self.layout, self.manaCost, self.cmc, self.typeLine, self.oracleText, self.flavorText, self.power, self.toughness, self.loyalty, self.reserved, self.foil, self.nonfoil, self.oversized, self.promo, self.reprint, self.variation, self.collectorNumber, self.rarity, self.watermark, self.artist, self.textless))

				self.commitLegalities(dbm)
				self.commitPrice(dbm)
				self.commitImage(dbm)
				self.commitSet(dbm)
				self.commitColors(dbm)
				self.commitColorIden(dbm)

				order = 0
				for f in self.faces:
					f.commitFace(self.scryfallId, order, dbm)
					order += 1

	def commitImage(self, dbm):

		if self.imageUrl != "":

			dbm.cur.execute("SELECT m.id, m.timestamp FROM media m JOIN mediaToCard mc ON mc.mediaId = m.id WHERE mc.cardId = %s", (self.scryfallId, ))

			if dbm.cur.rowcount == 1:
				fetch = dbm.cur.fetchone()
				if fetch[1] < (int(time.time()) - 7889400):
					dbm.cur.execute("UPDATE media SET mediaUrl = %s WHERE id = %s", (self.imageUrl, fetch[0]))
			else:
				dbm.cur.execute("INSERT INTO media (mediaUrl, altText) VALUES (%s, %s)", (self.imageUrl, "Image of " + self.name + " from " + self.mtgSet))
				mediaId = dbm.cur.lastrowid
				dbm.cur.execute("INSERT INTO mediaToCard (mediaId, cardId) VALUES (%s, %s)", (mediaId, self.scryfallId))

	def commitSet(self, dbm):
		#See if the set exists. If it doesn't make it and connect card. If it does connect card
		dbm.cur.execute("SELECT id FROM sets WHERE setCode = %s", (self.setCode, ))

		if dbm.cur.rowcount == 0:
			dbm.cur.execute("INSERT INTO sets (setCode, setName, setType) VALUES (%s, %s, %s)", (self.setCode, self.mtgSet, self.setType))
			dbm.cur.execute("SELECT id FROM sets WHERE setCode = %s", (self.setCode, ))

		tmp = dbm.cur.fetchone()
		setCode = tmp[0]

		dbm.cur.execute("INSERT INTO cardToSet (cardId, setId) VALUES (%s, %s)", (self.scryfallId, setCode))

	def commitColors(self, dbm):
		#Insert card colors into DB
		for color in self.colors:
			dbm.cur.execute("SELECT id FROM colors WHERE abbreviation = %s", (color, ))
			tmp = dbm.cur.fetchone()
			colorId = tmp[0]
			dbm.cur.execute("INSERT INTO cardToColor (cardId, colorId) VALUES (%s, %s)", (self.scryfallId, colorId))

	def commitColorIden(self, dbm):
		#Insert card colors into DB
		for color in self.colorIden:
			dbm.cur.execute("SELECT id FROM colors WHERE abbreviation = %s", (color, ))
			tmp = dbm.cur.fetchone()
			colorId = tmp[0]
			dbm.cur.execute("INSERT INTO cardToColorIdentity (cardId, colorId) VALUES (%s, %s)", (self.scryfallId, colorId))

	def setLegalities(self, json):
		self.legalities['standard'] = json['standard']
		self.legalities['future'] = json['future']
		self.legalities['historic'] = json['historic']
		self.legalities['pioneer'] = json['pioneer']
		self.legalities['modern'] = json['modern']
		self.legalities['legacy'] = json['legacy']
		self.legalities['pauper'] = json['pauper']
		self.legalities['vintage'] = json['vintage']
		self.legalities['penny'] = json['penny']
		self.legalities['commander'] = json['commander']
		self.legalities['brawl'] = json['brawl']
		self.legalities['duel'] = json['duel']
		self.legalities['oldschool'] = json['oldschool']

	def commitLegalities(self, dbm):
		dbm.cur.execute("DELETE FROM cardToFormat WHERE cardId = %s", (self.scryfallId, ))
		
		dbm.cur.execute("""INSERT INTO cardToFormat (cardId, formatId, legality) VALUES
		(%s, 1, %s),
		(%s, 2, %s),
		(%s, 3, %s),
		(%s, 4, %s),
		(%s, 5, %s),
		(%s, 6, %s),
		(%s, 7, %s),
		(%s, 8, %s),
		(%s, 9, %s),
		(%s, 10, %s),
		(%s, 11, %s),
		(%s, 12, %s),
		(%s, 13, %s)""", (self.scryfallId, self.legalities['standard'],
							self.scryfallId, self.legalities['future'],
							self.scryfallId, self.legalities['historic'],
							self.scryfallId, self.legalities['pioneer'],
							self.scryfallId, self.legalities['modern'],
							self.scryfallId, self.legalities['legacy'],
							self.scryfallId, self.legalities['pauper'],
							self.scryfallId, self.legalities['vintage'],
							self.scryfallId, self.legalities['penny'],
							self.scryfallId, self.legalities['commander'],
							self.scryfallId, self.legalities['brawl'],
							self.scryfallId, self.legalities['duel'],
							self.scryfallId, self.legalities['oldschool']))

	def setPrice(self, cid, token):
		try:
			#cid = '125843'

			url = "https://api.tcgplayer.com/v1.37.0/pricing/product/" + str(cid)
			r = requests.get(url, headers = {'Authorization' : "Bearer " + token['access_token'],})
			priceData = json.loads(r.text)

			#print(r.text)
			#print(priceData)

			if priceData['success'] == True:
				for result in priceData['results']:
					if result['marketPrice'] != None:
						if result['subTypeName'] == "Foil":
							self.curFoilPrice = result['marketPrice']
						else:
							self.curPrice = result['marketPrice']

		except:
			print("!!! No price data for: %s from %s" % (self.name, self.setCode))

	def commitPrice(self, dbm):
		dbm.cur.execute("INSERT INTO prices (price, foilPrice, currency) VALUES (%s, %s, 'dollars')", (self.curPrice, self.curFoilPrice))
		curPrice = dbm.cur.lastrowid
		dbm.cur.execute("INSERT INTO cardToPrice (cardId, priceId) VALUES (%s, %s)", (self.scryfallId, curPrice))

	def cardToDeck(self, dbm, deckId):
		with dbm.con:
			dbm.cur.execute("INSERT INTO cardToDeck (cardId, deckId, copies, sideboard) VALUES (%s, %s, %s, %s)", (self.scryfallId, deckId, self.copies, self.sideboard))

	def toString(self):
		return '{"name":"%s", "releaseDate":"%s", "layout":"%s", "manaCost":"%s", "cmc":"%s", "typeLine":"%s", "oracleText":"%s", "flavorText":"%s", "power":"%s", "toughness":"%s", "loyalty":"%s", "colors":"%s", "colorIdentity":"%s", "legalities":"%s", "reserved":"%s", "foil":"%s", "nonfoil":"%s", "oversized":"%s", "promo":"%s", "reprint":"%s", "variation":"%s", "mtgSet":"%s", "setCode":"%s", "collectorNumber":"%s", "rarity":"%s", "watermark":"%s", "artist":"%s", "curPrice":"%s", "curFoilPrice":"%s", "sideboard":"%s", "copies":"%s"}' % (self.name, self.releaseDate, self.layout, self.manaCost, self.cmc, self.typeLine, self.oracleText, self.flavorText, self.power, self.toughness, self.loyalty, str(self.colors), str(self.colorIden), str(self.legalities), self.reserved, self.foil, self.nonfoil, self.oversized, self.promo, self.reprint, self.variation, self.mtgSet, self.setCode, self.collectorNumber, self.rarity, self.watermark, self.artist, self.curPrice, self.curFoilPrice, self.sideboard, self.copies)

class Face:
	def __init__(self):
		self.name = ""
		self.manaCost = ""
		self.typeLine = ""
		self.oracleText = ""
		self.flavorText = ""
		self.colors = []
		self.power = ""
		self.toughness = ""
		self.loyalty = ""
		self.artist = ""
		self.imageUrl = ""
		self.altText = ""

	def setFace(self, json):
		self.name = json['name']
		self.manaCost = json['mana_cost']
		self.typeLine = json['type_line']
		self.oracleText = json['oracle_text']

		try:
			self.flavorText = json['flavor_text']
		except:
			pass

		try:
			for c in json['colors']:
				self.colors.append(c)
		except:
			pass

		try:
			self.power = json['power']
		except:
			pass

		try:
			self.toughness = json['toughness']
		except:
			pass

		try:
			self.loyalty = json['loyalty']
		except:
			pass

		try:
			self.artist = json['artist']
		except:
			pass

		try:
			self.imageUrl = json['image_uris']['normal']
		except:
			pass

	def commitFace(self, cardId, order, dbm):
		dbm.cur.execute("INSERT INTO cardFace (name, manaCost, typeLine, oracleText, flavorText, power, toughness, loyalty, artist) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (self.name, self.manaCost, self.typeLine, self.oracleText, self.flavorText, self.power, self.toughness, self.loyalty, self.artist))

		faceId = dbm.cur.lastrowid
		self.commitFaceColors(faceId, dbm)
		self.commitFaceImage(faceId, dbm)

		dbm.cur.execute("INSERT INTO cardFaceToCard (cardFaceId, cardId, displayOrder) VALUES (%s, %s, %s)", (faceId, cardId, order))

	def commitFaceColors(self, cid, dbm):
		#Insert card colors into DB
		for color in self.colors:
			dbm.cur.execute("SELECT id FROM colors WHERE abbreviation = %s", (color, ))
			tmp = dbm.cur.fetchone()
			colorId = tmp[0]
			dbm.cur.execute("INSERT INTO cardFaceToColor (cardFaceId, colorId) VALUES (%s, %s)", (cid, colorId))

	def commitFaceImage(self, cid, dbm):
		if self.imageUrl != "":
			dbm.cur.execute("INSERT INTO media (mediaUrl, altText) VALUES (%s, %s)", (self.imageUrl, "Image of " + self.name))
			mediaId = dbm.cur.lastrowid
			dbm.cur.execute("INSERT INTO cardFaceToMedia (cardFaceId, mediaId) VALUES (%s, %s)", (cid, mediaId))

	def toString(self):
		return '{"name":"%s", "manaCost":"%s", "typeLine":"%s", "oracleText":"%s", "flavorText":"%s", "colors":"%s", "power":"%s", "toughness":"%s", "loyalty":"%s", "artist":"%s"}' % (self.name, self.manaCost, self.typeLine, self.oracleText, self.flavorText, str(self.colors), self.power, self.toughness, self.loyalty, self.artist)