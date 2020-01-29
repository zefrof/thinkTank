import time, json, requests, pymysql

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

    def getCard(self, cid, dbm):
        with dbm.con:
            dbm.cur.execute("SELECT c.* FROM cards c WHERE c.id = %s", (cid, ))
            fetch = dbm.cur.fetchone()

    def getId(self, name, dbm):
        with dbm.con:
            dbm.cur.execute("SELECT c.id FROM cards c WHERE c.name = %s ", (name, ))
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

    def toString(self):
        return '{"name":"%s", "releaseDate":"%s", "layout":"%s", "manaCost":"%s", "cmc":"%s", "typeLine":"%s", "oracleText":"%s", "flavorText":"%s", "power":"%s", "toughness":"%s", "loyalty":"%s", "colors":"%s", "colorIdentity":"%s", "legalities":"%s", "reserved":"%s", "foil":"%s", "nonfoil":"%s", "oversized":"%s", "promo":"%s", "reprint":"%s", "variation":"%s", "mtgSet":"%s", "setCode":"%s", "collectorNumber":"%s", "rarity":"%s", "watermark":"%s", "artist":"%s", "curPrice":"%s", "curFoilPrice":"%s"}' % (self.name, self.releaseDate, self.layout, self.manaCost, self.cmc, self.typeLine, self.oracleText, self.flavorText, self.power, self.toughness, self.loyalty, str(self.colors), str(self.colorIden), str(self.legalities), self.reserved, self.foil, self.nonfoil, self.oversized, self.promo, self.reprint, self.variation, self.mtgSet, self.setCode, self.collectorNumber, self.rarity, self.watermark, self.artist, self.curPrice, self.curFoilPrice)

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

        self.archetype = ""

class Event:

    def __init__(self):
        self.name = ""
        self.date = ""
        self.location = ""
        self.format = ""
        self.numPlayers = 0
        self.decks = []

    def commitEvent(self, dbm):
        pass

class Database:
    def __init__(self):
        self.con = pymysql.connect('localhost', 'zefrof', 'hYbGFkPCgw@a', 'magic')
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