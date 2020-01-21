import threading, time, json, requests, pymysql

threadLimiter = threading.BoundedSemaphore(4)

class Thread(threading.Thread):
    def __init__(self, threadId, json):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.json = json
    def run(self):
        threadLimiter.acquire()

        #print(self.json['name'])

        card = Card()
        card.setCard(self.json)

        print(self.threadId)

        threadLimiter.release()

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
        self.collectorNumber = ""
        self.rarity = ""
        self.watermark = ""
        self.artist = ""
        self.textless = 0
        self.curPrice = ""
        self.curFoilPrice = ""
        self.imageUrl = " "

        self.faces = []

    def setCard(self, json):
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
        self.foil = json['foil']
        self.nonfoil = json['nonfoil']
        self.oversized = json['oversized']
        self.promo = json['promo']
        self.reprint = json['reprint']
        self.variation = json['variation']
        self.mtgSet = json['set_name']
        self.setCode = json['set']
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
            self.setPrice(self.tcgplayerId)

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
        except Exception as e:
            print(e)

    def getCard(self, id):
        pass

    def commitCard(self):
        dbm = Database()

        with dbm.con:
            dbm.cur.execute("SELECT c.id, c.dateModified FROM cards c WHERE c.id = %s", (self.scryfallId, ))

            #Card already exists
            if cur.rowcount == 1:
                fetch = dbm.cur.fetchone()

                #If it's been a month since last update
                if fetch[1] < (int(time.time()) - 2629800):
                    dbm.cur.execute("UPDATE cards SET name = %s, releaseDate = %s, layout = %s, manaCost = %s, cmc = %s, typeLine = %s, oracleText = %s, flavorText = %s, power = %s, toughness = %s, loyalty = %s, reserved = %s, foil = %s, nonfoil = %s, oversized = %s, promo = %s, reprint = %s, variation = %s, collectorNumber = %s, rarity = %s, watermark = %s, artist = %s, textless = %s, dateModified = %s WHERE id = %s", (self.name, self.releaseDate, self.layout, self.manaCost, self.cmc, self.typeLine, self.oracleText, self.flavorText, self.power, self.toughness, self.loyalty, self.reserved, self.foil, self.nonfoil, self.oversized, self.promo, self.reprint, self.variation, self.collectorNumber, self.rarity, self.watermark, self.artist, self.textless, int(time.time()), self.scryfallId))

                    commitLegalities()
                    commitPrice()
                    commitImage()



            #Card doesn't exist
            else:
                dbm.cur.execute("INSERT INTO cards (id, name, releaseDate, layout, manaCost, cmc, typeLine, oracleText, flavorText, power, toughness, loyalty, reserved, foil, nonfoil, oversized, promo, reprint, variation, collectorNumber, rarity, watermark, artist, textless, dateAdded) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (self.scryfallId, self.name, self.releaseDate, self.layout, self.manaCost, self.cmc, self.typeLine, self.oracleText, self.flavorText, self.power, self.toughness, self.loyalty, self.reserved, self.foil, self.nonfoil, self.oversized, self.promo, self.reprint, self.variation, self.collectorNumber, self.rarity, self.watermark, self.artist, self.textless, int(time.time())))

                commitLegalities()
                commitPrice()
                commitImage()

    def commitImage(self):
        dbm = Database()
        dbm.cur.execute("SELECT m.id, m.dateAdded FROM media AS m JOIN mediaToCard AS mc ON mc.mediaId = m.id WHERE mc.cardId = %s", (self.scryfallId, ))

        if dbm.cur.rowcount == 1:
            fetch = dbm.cur.fetchone()
            if fetch[1] < (int(time.time()) - 7889400):
                dbm.cur.execute("UPDATE media SET mediaUrl = %s WHERE id = %s", (self.imageUrl, fetch[0]))
        else:
            dbm.cur.execute("INSERT INTO media (mediaUrl, altText) VALUES (%s, %s)", (self.imageUrl, "Image of " + self.name + " from " + self.mtgSet))
            mediaId = cur.fetchone()
            cur.execute("INSERT INTO mediaToCard (mediaId, cardId, displayOrder) VALUES (%s, %s, 1)", (mediaId[0], self.scryfallId))

    def commitSet(self):


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

    def commitLegalities(self):
        dbm = Database()

        dbm.cur.execute("DELETE FROM cardToFormat WHERE cardId = %s", (self.scryfallId)
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 1, %s)", (self.scryfallId, self.legalities['standard']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 2, %s)", (self.scryfallId, self.legalities['future']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 2, %s)", (self.scryfallId, self.legalities['historic']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 3, %s)", (self.scryfallId, self.legalities['pioneer']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 3, %s)", (self.scryfallId, self.legalities['modern']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 3, %s)", (self.scryfallId, self.legalities['legacy']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 3, %s)", (self.scryfallId, self.legalities['pauper']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 3, %s)", (self.scryfallId, self.legalities['vintage']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 3, %s)", (self.scryfallId, self.legalities['penny']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 3, %s)", (self.scryfallId, self.legalities['commander']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 3, %s)", (self.scryfallId, self.legalities['brawl']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 3, %s)", (self.scryfallId, self.legalities['duel']))
        dbm.cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 3, %s)", (self.scryfallId, self.legalities['oldschool']))

    def setPrice(self, id):
        #Get auth token from TCGPlayer
        bearer = requests.post("https://api.tcgplayer.com/token",
            data = {
                "grant_type": "client_credentials",
                "client_id": "A7A184B3-923E-49EC-900F-204016D37EE2",
                "client_secret": "646E7BEC-556B-45EF-8746-3ADCF32FAB49",
            })
        token = bearer.json()

        try:
            #id = '125843'

            url = "https://api.tcgplayer.com/v1.27.0/pricing/product/" + str(id)
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
            pass

    def commitPrice(self):
        dbm = Database()

        cur.execute("INSERT INTO prices (price, currency, foil, dateAdded) VALUES (%s, 'dollars', %s, %s)", (self.curPrice, self.curFoilPrice, int(time.time())))
        curPrice = cur.lastrowid
        cur.execute("INSERT INTO cardToPrice (cardId, priceId) VALUES (%s, %s)", (self.scryfallId, curPrice))

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

    def commitFace(self, cardId):
        pass

    def toString(self):
        return '{"name":"%s", "manaCost":"%s", "typeLine":"%s", "oracleText":"%s", "flavorText":"%s", "colors":"%s", "power":"%s", "toughness":"%s", "loyalty":"%s", "artist":"%s"}' % (self.name, self.manaCost, self.typeLine, self.oracleText, self.flavorText, str(self.colors), self.power, self.toughness, self.loyalty, self.artist)

class Deck:
    name = ""
    archetype = ""
    pilot = ""
    finish = 0

class Event:
    name = ""
    date = ""
    location = ""

class Database:
    def __init__(self):
        self.con = pymysql.connect('localhost', 'zefrof', 'hYbGFkPCgw@a', 'magic')
        self.cur = con.cursor()