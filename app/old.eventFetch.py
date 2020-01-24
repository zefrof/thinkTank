import json, requests, time, pymysql, json, re
from bs4 import BeautifulSoup

#https://serverfault.com/questions/212269/tips-for-securing-a-lamp-server/212462#212462

#TRUNCATE TABLE `cardToDeck`;
#TRUNCATE TABLE decks;
#TRUNCATE TABLE deckToEvent;
#TRUNCATE TABLE events;
#TRUNCATE TABLE eventToFormat;
#TRUNCATE TABLE archetypeToDeck;

def commitEvent(eventName, eventLocation, eventDate, eventFormat, numPlayers):
    #print(eventName)

    con = pymysql.connect('localhost', 'zefrof', 'bop4YTNs', 'magicTCG')
    cur = con.cursor()
    with con:
        cur.execute("SELECT id FROM events WHERE title = %s AND date = %s", (eventName, eventDate))

        if cur.rowcount == 1:
            return -1


        cur.execute("INSERT INTO events (title, location, date, dateAdded) VALUES (%s, %s, %s, %s)", (eventName, eventLocation, eventDate, int(time.time())))

        eventId = cur.lastrowid

        #eventFormat = eventFormat.lower()
        #eventFormat = eventFormat.trim()

        if eventFormat == "standard":
            formatId = 1
        elif eventFormat == "future":
            formatId = 2
        elif eventFormat == "brawl":
            formatId = 3
        elif eventFormat == "modern":
            formatId = 4
        elif eventFormat == "legacy":
            formatId = 5
        elif eventFormat == "pauper":
            formatId = 6
        elif eventFormat == "vintage":
            formatId = 7
        elif eventFormat == "penny":
            formatId = 8
        elif eventFormat == "commander":
            formatId = 9
        elif eventFormat == "duel":
            formatId = 10
        elif eventFormat == "oldschool":
            formatId = 11

        cur.execute("INSERT INTO eventToFormat (eventId, formatId) VALUES (%s, %s)", (eventId, formatId))

        print("### Event " + eventName + " was inserted")

        return eventId

def commitDeck(deckName, deckPilot, deckPlace, eventId):
    #print(deckName)

    con = pymysql.connect('localhost', 'zefrof', 'bop4YTNs', 'magicTCG')
    cur = con.cursor()
    with con:
        cur.execute("INSERT INTO decks (title, pilot, place, dateAdded) VALUES (%s, %s, %s, %s)", (deckName, deckPilot, deckPlace, int(time.time())))

        deckId = cur.lastrowid

        cur.execute("INSERT INTO deckToEvent (deckId, eventId) VALUES (%s, %s)", (deckId, eventId))

        print("$$$ " + deckName + " attached to " + str(eventId))

        return deckId

def commitCard(cardName, deckId, cardAmount, sideboard):
    #print(cardName)

    con = pymysql.connect('localhost', 'zefrof', 'bop4YTNs', 'magicTCG')
    cur = con.cursor()
    with con:
        cur.execute("SELECT id FROM cards WHERE name = %s ", (cardName, ))

        if cur.rowcount > 0:
            cardId = cur.fetchone()
        else:
            tempName = '%' + cardName + '%'

            fill = '%//%'

            cur.execute("SELECT id FROM `cards` WHERE `name` LIKE %s AND `name` LIKE %s ", (tempName, fill))
            cardId = cur.fetchone()

        if cardId:
            #print(cardId[0])

            print("@@@ " + cardAmount + " of " + cardName + " (" + str(cardId[0]) + ") attached to " + str(deckId) + " as a " + str(sideboard))

            cur.execute("INSERT INTO cardToDeck (cardId, deckId, quantity, sideboard) VALUES (%s, %s, %s, %s)", (cardId[0], deckId, cardAmount, sideboard))

def main():
    url = 'https://www.tcdecks.net/format.php?format=Standard%20[Xln_M19_Grn]&page=12' #Last page proccessed Modern = page 30
    deckListPage = requests.get(url)
    soup = BeautifulSoup(deckListPage.text, "html.parser")

    #print(soup)

    eventFormat = eventName = eventDate = ""
    #eventCheck = deckCheck = 0
    eventId = deckId = 0

    #Iterate through events
    for td in soup.findAll('td'):
        try:
            if "principal" in td['class']:
                eventPage = requests.get('https://www.tcdecks.net/' + td.a['href'])
                eventText = BeautifulSoup(eventPage.text, "html.parser")

                #print(eventText.findAll('h3')[0].text)

                split = eventText.findAll('h5')[0].text.split('|')

                eventDate = split[2].strip().split(' ')[1]
                eventFormat = split[0].strip().split(' ')[1].lower()
                numPlayers = split[1].strip().split(' ')[3]

                eventName = eventText.findAll('h3')[0].text

                eventId = commitEvent(eventName, '', eventDate, eventFormat, numPlayers)

                if eventId == -1:
                    print("*** " + eventName + " on " + eventDate + " already exists")
                    continue

                #Iterate through decks at event
                for row in eventText.findAll('td'):
                    try:
                        if "principal" in row['class']:
                            deckPage = requests.get('https://www.tcdecks.net/' + row.a['href'])
                            deckText = BeautifulSoup(deckPage.text, "html.parser")

                            deckInfo = deckText.findAll('th')[0].text.strip()
                            place = deckText.findAll('th')[1].text.strip()

                            pilot = deckInfo.split('playing')[0].strip()
                            deckName = deckInfo.split('playing')[1].strip()
                            pos = place.split(' ')[1]

                            deckId = commitDeck(deckName, pilot, pos, eventId)

                            #Iterate though cards in a deck
                            for card in deckText.findAll('tr'):
                                try:
                                    if "left" in card['align']:
                                        numbahs = re.sub('[a-zA-Z]', '', card.text)
                                        numbahs = re.sub(r'\[.+?\]', '', numbahs)
                                        #numbahs = numbahs.replace('-', '')
                                        numbahs = re.sub(r'[^a-zA-Z0-9 \n\.]', '', numbahs)
                                        numbahs = re.sub(r'\s', ' ', numbahs)
                                        numbahs = re.sub(' +', ' ', numbahs)
                                        numbahs = numbahs.strip()
                                        numbahs = numbahs.split(' ')

                                        names = re.sub(r'\[.+?\]', '', card.text)
                                        names = names.replace('Creatures', '')
                                        names = names.replace('Sorceries', '')
                                        names = names.replace('Artifacts', '')
                                        names = names.replace('Lands', '')
                                        names = names.replace('Instants', '')
                                        names = names.replace('Planeswalkers', '')
                                        names = names.replace('Enchantments', '')
                                        names = re.sub('[0-9]', '|', names.strip())
                                        names = re.sub(r'\s', ' ', names)
                                        names = names.split('|')
                                        names = names[1:]

                                        if names.count('') >= 1:
                                            names.remove('')

                                        #print(names)
                                        #print(numbahs)

                                        if len(numbahs) != len(names):
                                            print(deckName + " num cards ({}) != num of numbahs ({}).".format(len(names), len(numbahs)))
                                            continue

                                        mainboard = 0
                                        for x in range(len(names)):
                                            #Needs to be 'fixed' for commander decks
                                            #print(mainboard)
                                            if mainboard < 60:
                                                sideboard = 0
                                            else:
                                                sideboard = 1

                                            commitCard(names[x].strip(), deckId, numbahs[x], sideboard)
                                            mainboard += int(numbahs[x])

                                except Exception as e:
                                    #print(e)
                                    pass
                            #break
                    except Exception as e:
                        #print(e)
                        pass
        except Exception as e:
            #print(e)
            pass

        #break

if __name__ == '__main__':
    main()