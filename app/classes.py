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
    cmc = 0
    typeLine = ""
    oracleText = ""
    flavorText = ""
    typeLine = ""
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
        print(json)

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