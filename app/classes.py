import threading, time, json, requests

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
        self.relaseDate = ""
        self.layout = ""
        self.manaCost = ""
        self.cmc = 0.0
        self.typeLine = ""
        self.oracleText = ""
        self.flavorText = ""
        self.power = ""
        self.toughness = ""
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
        self.curPrice = ""
        self.curFoilPrice = ""

    def setCard(self, json):
        self.scryfallId = json['id']
        self.tcgplayerId = json['tcgplayer_id']
        self.name = json['name']
        self.relaseDate = json['released_at']
        self.layout = json['layout']
        self.manaCost = json['mana_cost']
        self.cmc = json['cmc']
        self.typeLine = json['type_line']
        self.oracleText = json['oracle_text']
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

        for c in json['colors']:
            self.colors.append(c)

        for c in json['color_identity']:
            self.colorIden.append(c)

        self.setLegalities(json['legalities'])

        self.reserved = json['reserved']
        self.foil = json['foil']
        self.nonfoil = json['nonfoil']
        self.oversized = json['oversized']
        self.promo = json['promo']
        self.reprint = json['reprint']
        self.mtgSet = json['set_name']
        self.setCode = json['set']
        self.collectorNumber = json['collector_number']
        self.rarity = json['rarity']

        try:
            self.watermark = json['watermark']
        except:
            pass

        #self.curPrice = json['prices']['usd']
        #self.curFoilPrice = json['prices']['usd_foil']

        try:
            if len(json['card_faces']) > 0:
                print("this car has faces yo")
        except:
            print("no faces yo?")

        print(self.legalities['vintage'])

    def getCard(self, id):
        pass

    def commitCard(self):
        pass

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

    def setPrice(self):
        #Get auth token from TCGPlayer
        bearer = requests.post("https://api.tcgplayer.com/token",
            data = {
                "grant_type": "client_credentials",
                "client_id": "A7A184B3-923E-49EC-900F-204016D37EE2",
                "client_secret": "646E7BEC-556B-45EF-8746-3ADCF32FAB49",
            })
        token = bearer.json()

        try:
            tcgplayerId = '125843'

            url = "https://api.tcgplayer.com/v1.27.0/pricing/product/" + tcgplayerId
            r = requests.get(url, headers = {'Authorization' : "Bearer " + token['access_token'],})
            priceData = json.loads(r.text)

            #print(r.text)

            print(priceData)

        except Exception as e:
            print(e)


    def toString(self):
        return ""

class Deck:
    name = ""
    archetype = ""
    pilot = ""
    finish = 0

class Event:
    name = ""
    date = ""
    location = ""