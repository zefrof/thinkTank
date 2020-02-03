import requests, re
from bs4 import BeautifulSoup
from classes import Database, Event, Deck, Card

def main():

    errCount = 0
    url = "https://www.tcdecks.net/deck.php?id="

    dbm = Database()

    index = 0
    end = 0

    with dbm.con:
        dbm.cur.execute("SELECT `index` FROM scrapeInfo WHERE id = 1;")
        tmp = dbm.cur.fetchone()
        print(tmp[0])
        index = tmp[0] - 3
        if index <= 0:
            index = 1

        end = index + 203


    while errCount < 5:
        page = requests.get(url + str(index))

        if(page.status_code == 404):
            print("404 Error at: %d" % (index))
            errCount += 1
            index += 1
            continue

        event = Event()

        text = BeautifulSoup(page.content, features="html.parser")
        split = text.find('h5').text.split('|')

        event.format = split[0].replace("Format:", "")
        event.format = re.sub('[\(\[].*?[\)\]]', ' ', event.format)
        event.format = event.format.replace("Archive", "")
        event.format = event.format.strip()

        if event.format == "Vintage Old School":
            event.format = "Old School"

        event.numPlayers = split[1].replace("Number of Players:", "")
        event.numPlayers = event.numPlayers.strip()

        if event.numPlayers == "Unknown":
            event.numPlayers = 0

        event.date = split[2].replace("Date:", "")
        event.date = event.date.strip()

        event.name = text.find('h3').text

        if event.name == "":
            index += 1
            continue

        if event.eventExists(dbm) == True:
            index += 1
            continue

        #print("### Name: %s | Date: %s | Format: %s | Players: %s" % (event.name, event.date, event.format, event.numPlayers))

        #Iterate through decks at event
        for row in text.findAll('td'):
            try:
                if "principal" in row['class']:
                    deckPage = requests.get('https://www.tcdecks.net/' + row.a['href'])
                    deckText = BeautifulSoup(deckPage.content, features="html.parser")

                    deck = Deck()

                    deckInfo = deckText.find('th').text.strip()
                    split = deckInfo.split('playing')
                    deck.pilot = split[0].strip()
                    deck.archetype = split[1].strip()

                    place = deckText.findAll('th')[1].text.strip()
                    deck.finish = place.split(' ')[1]

                    ark = deckText.findAll('th')[2].text.strip()
                    deck.name = ark.replace("Deck Name:", "")
                    deck.name = deck.name.strip()

                    #print("### Name: %s | Pilot: %s | Finish: %s | Archetype: %s" % (deck.name, deck.pilot, deck.finish, deck.archetype))
                    event.decks.append(deck)

                    #Number and name of each card
                    s = deckText.findAll('tr')[2]

                    names = []
                    for tmp in s('a'):
                        names.append(tmp.extract().text.strip())

                    for tmp in s('h6'):
                        tmp.extract()

                    s = re.sub(r'\s', ' ', s.text)
                    s = re.sub(' +', ' ', s)
                    s = s.strip()

                    numbahs = s.split(" ")
                    numbahs = list(map(int, numbahs))

                    if event.format == "Commander" or event.format == "Duel":
                        total = 100
                    else:
                        total = 60

                    #print(names)
                    #print(numbahs)

                    if len(names) != len(numbahs):
                        print("!!! Huston we have a problem at deck %s from event %s on %s" % (deck.name, event.name, event.date))
                        print(names)
                        print(numbahs)
                        index += 1
                        continue

                    mainboard = 0
                    for x in range(len(names)):
                        card = Card()
                        cid = card.getCardId(names[x], dbm)
                        card.getCard(cid, dbm)

                        if mainboard < total:
                            sideboard = 0
                        else:
                            sideboard = 1

                        card.sideboard = sideboard
                        card.copies = numbahs[x]
                        deck.cards.append(card)

                        mainboard += numbahs[x]

            except:
                pass

        event.commitEvent(dbm)

        if index == end:
            break

        print(index)

        index += 1

    if errCount == 5:
        index -= 10
    
    with dbm.con:
        dbm.cur.execute("UPDATE scrapeInfo SET `index` = %s WHERE id = 1", (index, ))


if __name__== "__main__":
    main()