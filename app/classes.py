import time, json, requests, pymysql, string, random
from passlib.hash import bcrypt

class Card:

    def __init__(self):
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

        self.faces = []

        self.sideboard = 0
        self.copies = 0

    def setCard(self, json, dbm):
        self.scryfallId = json['id']

        try:
            self.tcgplayerId = json['tcgplayer_id']
        except:
            pass

        self.name = json['name']
        self.releaseDate = json['released_at']
        self.layout = json['layout']

        try:
            self.manaCost = json['mana_cost']
        except:
            pass

        self.cmc = json['cmc']
        self.typeLine = json['type_line']

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

        for c in json['color_identity']:
            self.colorIden.append(c)

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

        self.artist = json['artist']

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
            dbm.cur.execute("SELECT c.id, c.dateModified FROM cards c WHERE c.id = %s", (self.scryfallId, ))

            #Card already exists
            if dbm.cur.rowcount == 1:
                fetch = dbm.cur.fetchone()

                #If it's been a month since last update
                if fetch[1] < (int(time.time()) - 2629800):
                    print("Updating %s from %s" % (self.name, self.setCode))

                    dbm.cur.execute("UPDATE cards SET name = %s, releaseDate = %s, layout = %s, manaCost = %s, cmc = %s, typeLine = %s, oracleText = %s, flavorText = %s, power = %s, toughness = %s, loyalty = %s, reserved = %s, foil = %s, nonfoil = %s, oversized = %s, promo = %s, reprint = %s, variation = %s, collectorNumber = %s, rarity = %s, watermark = %s, artist = %s, textless = %s, dateModified = %s WHERE id = %s", (self.name, self.releaseDate, self.layout, self.manaCost, self.cmc, self.typeLine, self.oracleText, self.flavorText, self.power, self.toughness, self.loyalty, self.reserved, self.foil, self.nonfoil, self.oversized, self.promo, self.reprint, self.variation, self.collectorNumber, self.rarity, self.watermark, self.artist, self.textless, int(time.time()), self.scryfallId))

                    self.commitLegalities(dbm)
                    self.commitImage(dbm)

                self.commitPrice(dbm)

            #Card doesn't exist
            else:
                dbm.cur.execute("INSERT INTO cards (id, name, releaseDate, layout, manaCost, cmc, typeLine, oracleText, flavorText, power, toughness, loyalty, reserved, foil, nonfoil, oversized, promo, reprint, variation, collectorNumber, rarity, watermark, artist, textless, dateAdded) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (self.scryfallId, self.name, self.releaseDate, self.layout, self.manaCost, self.cmc, self.typeLine, self.oracleText, self.flavorText, self.power, self.toughness, self.loyalty, self.reserved, self.foil, self.nonfoil, self.oversized, self.promo, self.reprint, self.variation, self.collectorNumber, self.rarity, self.watermark, self.artist, self.textless, int(time.time())))

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

            dbm.cur.execute("SELECT m.id, m.dateAdded FROM media m JOIN mediaToCard mc ON mc.mediaId = m.id WHERE mc.cardId = %s", (self.scryfallId, ))

            if dbm.cur.rowcount == 1:
                fetch = dbm.cur.fetchone()
                if fetch[1] < (int(time.time()) - 7889400):
                    dbm.cur.execute("UPDATE media SET mediaUrl = %s WHERE id = %s", (self.imageUrl, fetch[0]))
            else:
                dbm.cur.execute("INSERT INTO media (mediaUrl, altText, dateAdded) VALUES (%s, %s, %s)", (self.imageUrl, "Image of " + self.name + " from " + self.mtgSet, int(time.time())))
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
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 1, %s)", (self.scryfallId, self.legalities['standard']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 2, %s)", (self.scryfallId, self.legalities['future']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 2, %s)", (self.scryfallId, self.legalities['historic']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 4, %s)", (self.scryfallId, self.legalities['pioneer']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 5, %s)", (self.scryfallId, self.legalities['modern']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 6, %s)", (self.scryfallId, self.legalities['legacy']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 7, %s)", (self.scryfallId, self.legalities['pauper']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 8, %s)", (self.scryfallId, self.legalities['vintage']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 9, %s)", (self.scryfallId, self.legalities['penny']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 10, %s)", (self.scryfallId, self.legalities['commander']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 11, %s)", (self.scryfallId, self.legalities['brawl']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 12, %s)", (self.scryfallId, self.legalities['duel']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 13, %s)", (self.scryfallId, self.legalities['oldschool']))

    def setPrice(self, cid, token):
        try:
            #cid = '125843'

            url = "https://api.tcgplayer.com/v1.27.0/pricing/product/" + str(cid)
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

        if self.curPrice != 0 and self.curFoilPrice != 0:
            dbm.cur.execute("INSERT INTO prices (price, foilPrice, currency, dateAdded) VALUES (%s, %s, 'dollars', %s)", (self.curPrice, self.curFoilPrice, int(time.time())))
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

class Deck:

    def __init__(self):
        self.name = ""
        self.pilot = ""
        self.finish = ""
        self.cards = []
        self.sideboard = []
        self.archetype = ""

        self.cid = 0

    def commitDeck(self, dbm, eventId, new = 1):
        with dbm.con:
            if new == 1:
                dbm.cur.execute("INSERT INTO decks (name, pilot, finish, dateAdded) VALUES (%s, %s, %s, %s)", (self.name, self.pilot, self.finish, int(time.time())))
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

    def toString(self):
        s = '{"name":"%s", "pilot":"%s", "finish":"%s", "archetype":"%s"}' % (self.name, self.pilot, self.finish, self.archetype)

        for card in self.cards:
            s += card.toString()

        return s

class Event:

    def __init__(self):
        self.name = ""
        self.date = ""
        self.format = ""
        self.numPlayers = 0
        self.decks = []

        self.cid = 0

    def commitEvent(self, dbm):
        """ Commits an event to the database """
        with dbm.con:

            dbm.cur.execute("INSERT INTO events (name, date, numPlayers, dateAdded) VALUES (%s, %s, %s, %s)", (self.name, self.date, self.numPlayers, int(time.time())))
            eventId = dbm.cur.lastrowid

            self.eventToFormat(dbm, eventId)

            for deck in self.decks:
                deck.commitDeck(dbm, eventId)

            print("### Inserted %s on %s in format %s" % (self.name, self.date, self.format))

    def updateEvent(self, dbm):
        with dbm.con:
            dbm.cur.execute("UPDATE events SET name = %s, date = %s, numPlayers = %s WHERE id = %s", (self.name, self.date, self.numPlayers, self.cid))

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

    def getEvent(self, dbm, cid, full = 0):
        with dbm.con:
            dbm.cur.execute("SELECT e.*, f.name as formatName FROM `events` e JOIN eventToFormat ef ON ef.eventId = e.id JOIN formats f ON f.id = ef.formatId WHERE e.id = %s", (cid, ))
            fetch = dbm.cur.fetchone()

            self.cid = fetch[0]
            self.name = fetch[1]
            self.date = fetch[2]
            self.numPlayers = fetch[3]
            self.format = fetch[7]

            if full == 1:
                dbm.cur.execute("SELECT d.id, d.name, d.pilot, d.finish, d.active, a.id AS arkId, a.name AS arkName FROM decks d JOIN archetypeToDeck ad ON ad.deckId = d.id JOIN archetypes a ON a.id = ad.archetypeId JOIN deckToEvent de ON de.deckId = d.id WHERE de.eventId = %s", (cid, ))
                fetch = dbm.cur.fetchall()

                for d in fetch:
                    deck = Deck()
                    deck.cid = d[0]
                    deck.name = d[1]
                    deck.pilot = d[2]
                    deck.finish = d[3]
                    deck.archetype = d[6]

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
                        elif card.sideboard == 1:
                            deck.sideboard.append(card)

                    self.decks.append(deck)

class Content:
    def __init__(self):
        pass

    def fetchEvents(self, dbm, page):
        events = []
        with dbm.con:
            offset = (page - 1) * 20
            dbm.cur.execute("SELECT id FROM `events` WHERE active = 1 ORDER BY date DESC, name LIMIT %s, 20 ", (offset, ))
            fetch = dbm.cur.fetchall()

            for x in fetch:
                event = Event()
                event.getEvent(dbm, x)
                events.append(event)

        return events

    def searchEventNames(self, dbm, name):
        events = []
        name = "%" + name + "%"
        with dbm.con:
            dbm.cur.execute("SELECT id FROM `events` WHERE `name` LIKE %s", (name, ))
            fetch = dbm.cur.fetchall()

            for x in fetch:
                event = Event()
                event.getEvent(dbm, x)
                events.append(event)

        return events

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

class Database:
    def __init__(self):
        self.con = pymysql.connect('18.223.101.184', 'zefrof', 'hYbGFkPCgw@a', 'magic')
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
            dbm.cur.execute("INSERT INTO admin.users (username, email, password) VALUES (%s, %s)", (username, email, password))

        return True

    def loginUser(self, username, password):
        dbm = Database()

        with dbm.con:
            dbm.cur.execute("SELECT id FROM admin.users WHERE username = %s", (username, ))

            if dbm.cur.rowcount == 1:
                dbm.cur.execute("SELECT password FROM admin.users WHERE username = %s", (username, ))
                fetch = dbm.cur.fetchone()
                check = bcrypt.verify(password, fetch[0])

                if check == True:
                    sessionId = bcrypt.hash(username + ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(40)))
                    dbm.cur.execute("UPDATE admin.users SET session = %s, lastLogin = %s WHERE username = %s", (sessionId, int(time.time()), username))
                    self.username = username
                    return sessionId
                else:
                    return False
            else:
                return False

    def verifyUser(self, sessionId):
        dbm = Database()

        with dbm.con:
            dbm.cur.execute("SELECT lastLogin FROM admin.users WHERE session = %s", (sessionId, ))
            fetch = dbm.cur.fetchone()
            if dbm.cur.rowcount == 1:
                if fetch[0] < (int(time.time()) - 1800):
                    return False
                else:
                    dbm.cur.execute("UPDATE admin.users SET lastLogin = %s WHERE username = %s", (int(time.time()), self.username))
                    return True
            else:
                return False
