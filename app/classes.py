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

        threadLimiter.release()

class Card:
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
    reserve = 0
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

    def __init__(self):
        pass

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
        self.flavorText = json['flavor_text']
        self.power = json['power']
        self.toughness = json['toughness']

        self.colors
        self.colorIden
        self.legalities

        self.reserve = json['reserve']
        self.foil = json['foil']
        self.nonfoil = json['nonfoil']
        self.oversized = json['oversized']
        self.promo = json['promo']
        self.reprint = json['reprint']
        self.mtgSet = json['set_name']
        self.setCode = json['set']
        self.collectorNumber = json['collector_number']
        self.rarity = json['rarity']
        self.watermark = json['watermark']

        self.curPrice

        print(json['name'])

    def getCard(self):
        pass

    def commitCard(self):
        pass

class Deck:
    name = ""
    archetype = ""
    pilot = ""
    finish = 0

class Event:
    name = ""
    date = ""
    location = ""