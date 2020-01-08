import json, requests, time, pymysql, json

def main():
    #https://archive.scryfall.com/json/scryfall-all-cards.json
    #https://archive.scryfall.com/json/scryfall-default-cards.json
    #https://archive.scryfall.com/json/scryfall-oracle-cards.json

    #TRUNCATE TABLE `prices`;
    #TRUNCATE TABLE mediaToCard;
    #TRUNCATE TABLE media;
    #TRUNCATE TABLE cardToSet;
    #TRUNCATE TABLE cardToPrice;
    #TRUNCATE TABLE cardToFormat;
    #TRUNCATE TABLE cardToColorIdentity;
    #TRUNCATE TABLE cardToColor;
    #TRUNCATE TABLE cards;
    #TRUNCATE TABLE cardFaceToCard;
    #TRUNCATE TABLE cardFace;

    #https://api.scryfall.com/cards/search?order=cmc&q=c%3Ared+pow%3D3 

    fd = open("scryfall-default-cards.json", "r")

    #Get auth token from TCGPlayer
    bearer = requests.post("https://api.tcgplayer.com/token",
        data = {
            "grant_type": "client_credentials",
            "client_id": "A7A184B3-923E-49EC-900F-204016D37EE2",
            "client_secret": "646E7BEC-556B-45EF-8746-3ADCF32FAB49",
        })
    token = bearer.json()

    con = pymysql.connect('localhost', 'zefrof', 'bop4YTNs', 'magicTCG')
    cur = con.cursor()

    #count = 0
    fd.readline()
    for line in fd:
        s = line.strip()
        if s[-1:] is ",":
            s = s[:-1]

        try:
            data = json.loads(s)
        except:
            continue

        with con:

            cur.execute("SELECT c.id, c.dateModified FROM cards c JOIN cardToSet cs ON cs.cardId = c.id JOIN sets s ON s.id = cs.setId WHERE c.name = %s AND s.setCode = %s", (data['name'], data['set']))

            if cur.rowcount == 1:
                print("**** " + data['name'] + " from " + data['set'] + " is already in the DB ****")

                fetch = cur.fetchone()

                #print(fetch[1])

                try:
                    cur.execute("SELECT id FROM media WHERE mediaUrl = %s", (data['image_uris']['large']))

                    if cur.rowcount == 0:
                        #Insert picture into DB
                        cur.execute("INSERT INTO media (mediaUrl, altText) VALUES (%s, %s)", (data['image_uris']['large'], data['name'] + " from " + data['set'] + " picture"))

                        cur.execute("SELECT id FROM media ORDER BY id DESC LIMIT 1")
                        mediaId = cur.fetchone()

                        cur.execute("INSERT INTO mediaToCard (mediaId, cardId, displayOrder) VALUES (%s, %s, 1)", (mediaId[0], fetch[0]))
                except:
                    pass

                #Set legalities for card
                cur.execute("DELETE FROM cardToFormat WHERE cardId = %s", (fetch[0]))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 1, %s)", (fetch[0], data['legalities']['standard']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 2, %s)", (fetch[0], data['legalities']['future']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 3, %s)", (fetch[0], data['legalities']['brawl']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 4, %s)", (fetch[0], data['legalities']['modern']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 5, %s)", (fetch[0], data['legalities']['legacy']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 6, %s)", (fetch[0], data['legalities']['pauper']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 7, %s)", (fetch[0], data['legalities']['vintage']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 8, %s)", (fetch[0], data['legalities']['penny']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 9, %s)", (fetch[0], data['legalities']['commander']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 10, %s)", (fetch[0], data['legalities']['duel']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 11, %s)", (fetch[0], data['legalities']['oldschool']))

                #Add additional card price
                if fetch[0] < (int(time.time()) - 172800):
                    try:
                        tcgplayerId = str(data['tcgplayer_id'])

                        url = "https://api.tcgplayer.com/v1.27.0/pricing/product/" + tcgplayerId
                        r = requests.get(url, headers = {'Authorization' : "Bearer " + token['access_token'],})
                        priceData = json.loads(r.text)

                        #print(priceData)

                        if priceData['success'] == True:
                            for result in priceData['results']:
                                if result['marketPrice'] != None:
                                    foil = 0
                                    if result['subTypeName'] == "Foil":
                                        foil = 1

                                    cur.execute("INSERT INTO prices (price, currency, foil, dateAdded) VALUES (%s, 'dollars', %s, %s)", (result['marketPrice'], foil, int(time.time())))

                                    curPrice = cur.lastrowid

                                    cur.execute("INSERT INTO cardToPrice (cardId, priceId) VALUES (%s, %s)", (fetch[0], curPrice))

                                    cur.execute("UPDATE cards SET dateModified = %s WHERE id = %s", (int(time.time()), fetch[0]))

                    except Exception:
                        pass  
            else:

                try:
                    manaCost = data['mana_cost']
                except:
                    manaCost = ""

                try:
                    oracleText = data['oracle_text']
                except:
                    oracleText = ""

                try:
                    flavorText = data['flavor_text']
                except:
                    flavorText = ""

                try:
                    power = data['power']
                except:
                    power = ""

                try:
                    toughness = data['toughness']
                except:
                    toughness = ""

                try:
                    loyalty = data['loyalty']
                except:
                    loyalty = ""

                if data['reserved'] == False:
                    reserved = 0
                else:
                    reserved = 1

                if data['foil'] == False:
                    foil = 0
                else:
                    foil = 1

                if data['nonfoil'] == False:
                    nonfoil = 0
                else:
                    nonfoil = 1

                if data['oversized'] == False:
                    oversized = 0
                else:
                    oversized = 1

                if data['promo'] == False:
                    promo = 0
                else:
                    promo = 1

                if data['reprint'] == False:
                    reprint = 0
                else:
                    reprint = 1

                if data['variation'] == False:
                    variation = 0
                else:
                    variation = 1

                try:
                    collectorNumber = data['collector_number']
                except:
                    collectorNumber = ""

                try:
                    rarity = data['rarity']
                except:
                    rarity = ""

                try:
                    artist = data['artist']
                except:
                    artist = ""

                if data['textless'] == False:
                    textless = 0
                else:
                    textless = 1

                if data['layout'] == "transform" or data['layout'] == "split" or data['layout'] == "flip" or data['layout'] == "double_faced_token" or data['layout'] == "adventure":

                    cur.execute("INSERT INTO cards (name, released, layout, manaCost, cmc, typeLine, oracleText, flavorText, power, toughness, loyalty, reserved, foil, nonfoil, oversized, promo, reprint, variation, collectorNumber, rarity, artist, textless, dateAdded) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (data['name'], data['released_at'], data['layout'], manaCost, data['cmc'], data['type_line'], oracleText, flavorText, power, toughness, loyalty, reserved, foil, nonfoil, oversized, promo, reprint, variation, collectorNumber, rarity, artist, textless, int(time.time())))

                    faceCt = 0
                    for face in data['card_faces']:

                        try:
                            faceManaCost = face['mana_cost']
                        except:
                            faceManaCost = ""

                        try:
                            faceOracleText = face['oracle_text']
                        except:
                            faceOracleText = ""

                        try:
                            faceFlavorText = face['flavor_text']
                        except:
                            faceFlavorText = ""

                        try:
                            facePower = face['power']
                        except:
                            facePower = ""

                        try:
                            faceToughness = face['toughness']
                        except:
                            faceToughness = ""

                        try:
                            faceLoyalty = face['loyalty']
                        except:
                            faceLoyalty = ""

                        try:
                            faceArtist = face['artist']
                        except:
                            faceArtist = ""

                        cur.execute("INSERT INTO cardFace (name, manaCost, typeLine, oracleText, flavorText, power, toughness, loyalty, artist, dateAdded) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (face['name'], faceManaCost, face['type_line'], faceOracleText, faceFlavorText, facePower, faceToughness, faceLoyalty, faceArtist, int(time.time())))

                        cur.execute("SELECT id FROM cards ORDER BY id DESC LIMIT 1")
                        fetch = cur.fetchone()

                        cur.execute("SELECT id FROM cardFace ORDER BY id DESC LIMIT 1")
                        fetchFace = cur.fetchone()

                        cur.execute("INSERT INTO cardFaceToCard (cardFaceId, cardId, displayOrder) VALUES (%s, %s, %s)", (fetchFace[0], fetch[0], faceCt))

                        #Insert picture into DB
                        if data['layout'] == "transform":
                            cur.execute("INSERT INTO media (mediaUrl, altText) VALUES (%s, %s)", (face['image_uris']['large'], "Picture of " + data['name'] + " from " + data['set']))

                            cur.execute("SELECT id FROM media ORDER BY id DESC LIMIT 1")
                            mediaId = cur.fetchone()

                            cur.execute("INSERT INTO mediaToCard (mediaId, cardId, displayOrder) VALUES (%s, %s, 0)", (mediaId[0], fetch[0]))

                        faceCt += 1


                else:
                    cur.execute("INSERT INTO cards (name, released, layout, manaCost, cmc, typeLine, oracleText, flavorText, power, toughness, loyalty, reserved, foil, nonfoil, oversized, promo, reprint, variation, collectorNumber, rarity, artist, textless, dateAdded) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (data['name'], data['released_at'], data['layout'], manaCost, data['cmc'], data['type_line'], oracleText, flavorText, power, toughness, loyalty, reserved, foil, nonfoil, oversized, promo, reprint, variation, collectorNumber, rarity, artist, textless, int(time.time())))

                #See if the set exists. If it doesn't make it and connect card. If it does connect card
                cur.execute("SELECT id, dateModified FROM cards ORDER BY id DESC LIMIT 1")
                fetch = cur.fetchone()
                
                cur.execute("SELECT id FROM sets WHERE setCode = %s", (data['set']))

                if cur.rowcount == 0:
                    cur.execute("INSERT INTO sets (setCode, setName, setType) VALUES (%s, %s, %s)", (data['set'], data['set_name'], data['set_type']))
                    cur.execute("SELECT id FROM sets WHERE setCode = %s", (data['set']))

                setCode = cur.fetchone()

                cur.execute("INSERT INTO cardToSet (cardId, setId) VALUES (%s, %s)", (fetch[0], setCode[0]))

                #Insert card colors into DB
                try:
                    for color in data['colors']:
                        cur.execute("SELECT id FROM colors WHERE abbreviation = %s", (color))
                        colorId = cur.fetchone()

                        cur.execute("INSERT INTO cardToColor (cardId, colorId) VALUES (%s, %s)", (fetch[0], colorId[0]))
                except:
                    print("!!!! " + data['name'] + " from " + data['set'] + " doesn't have colors !!!!")

                #Insert card color identity into DB
                try:
                    for color in data['color_identity']:
                        cur.execute("SELECT id FROM colors WHERE abbreviation = %s", (color))
                        colorId = cur.fetchone()

                        cur.execute("INSERT INTO cardToColorIdentity (cardId, colorId) VALUES (%s, %s)", (fetch[0], colorId[0]))
                except:
                    print("!!!! " + data['name'] + " from " + data['set'] + " doesn't have color identity !!!!")

                #Insert picture into DB
                try:
                    cur.execute("INSERT INTO media (mediaUrl, altText) VALUES (%s, %s)", (data['image_uris']['large'], "Picture of " + data['name'] + " from " + data['set']))

                    cur.execute("SELECT id FROM media ORDER BY id DESC LIMIT 1")
                    mediaId = cur.fetchone()

                    cur.execute("INSERT INTO mediaToCard (mediaId, cardId, displayOrder) VALUES (%s, %s, 0)", (mediaId[0], fetch[0]))
                except:
                    print("!!!! " + data['name'] + " from " + data['set'] + " doesn't have an image !!!!")

                #Set legalities for card
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 1, %s)", (fetch[0], data['legalities']['standard']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 2, %s)", (fetch[0], data['legalities']['future']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 3, %s)", (fetch[0], data['legalities']['brawl']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 4, %s)", (fetch[0], data['legalities']['modern']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 5, %s)", (fetch[0], data['legalities']['legacy']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 6, %s)", (fetch[0], data['legalities']['pauper']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 7, %s)", (fetch[0], data['legalities']['vintage']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 8, %s)", (fetch[0], data['legalities']['penny']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 9, %s)", (fetch[0], data['legalities']['commander']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 10, %s)", (fetch[0], data['legalities']['duel']))
                cur.execute("INSERT INTO cardToFormat (cardId, formatId, legality) VALUES (%s, 11, %s)", (fetch[0], data['legalities']['oldschool']))

                #Add initial card price
                if fetch[1] < (int(time.time()) - 172800):
                    try:
                        tcgplayerId = str(data['tcgplayer_id'])

                        url = "https://api.tcgplayer.com/v1.27.0/pricing/product/" + tcgplayerId
                        r = requests.get(url, headers = {'Authorization' : "Bearer " + token['access_token'],})
                        priceData = json.loads(r.text)

                        #print(priceData)

                        if priceData['success'] == True:
                            for result in priceData['results']:
                                if result['marketPrice'] != None:
                                    foil = 0
                                    if result['subTypeName'] == "Foil":
                                        foil = 1

                                    cur.execute("INSERT INTO prices (price, currency, foil, dateAdded) VALUES (%s, 'dollars', %s, %s)", (result['marketPrice'], foil, int(time.time())))

                                    curPrice = cur.lastrowid

                                    cur.execute("INSERT INTO cardToPrice (cardId, priceId) VALUES (%s, %s)", (fetch[0], curPrice))

                                    cur.execute("UPDATE cards SET dateModified = %s WHERE id = %s", (int(time.time()), fetch[0]))

                    except Exception:
                        pass

                print("#### " + data['name'] + " from " + data['set'] + " has been added to the DB ####")

        #count += 1

        #if count == 35:
        #    break


if __name__ == '__main__':
    main()