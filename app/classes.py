import threading, time

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
        scryfallId = ""
        tcgplayerId = 0
        name = ""
        relaseDate = ""
        layout = ""
        manaCost = ""
        cmc = 0.0
        typeLine = ""
        oracleText = ""
        flavorText = ""
        power = ""
        toughness = ""
        colors = []
        colorIden = []
        legalities = []
        reserved = 0
        foil = 0
        nonfoil = 0
        oversized = 0
        promo = 0
        reprint = 0
        variation = 0
        mtgSet = ""
        setCode = ""
        collectorNumber = ""
        rarity = ""
        watermark = ""
        curPrice = ""
        curFoilPrice = ""

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

        #self.colors.clear()
        for c in json['colors']:
            self.colors.append(c)

        #self.colorIden.clear()
        #for c in json['color_identity']:
        #    self.colorIden.append(c)

        #self.legalities.clear()
        #for c in json['legalities']:
        #    self.legalities.append(c)

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

        print(self.colors)

    def getCard(self):
        pass

    def commitCard(self):
        pass

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