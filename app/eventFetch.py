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
        dbm.cur.execute("SELECT COUNT(id) FROM events;")
        tmp = dbm.cur.fetchone()
        index = tmp[0] - 5
        end = index + 200


    while errCount < 5:
        page = requests.get(url + str(index))
        #page.encoding = 'utf-8'

        if(page.status_code == 404):
            print("404 Error at: %d" % (index))
            errCount += 1
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

        #print("Name: %s | Date: %s | Format: %s | Players: %s" % (event.name, event.date, event.format, event.numPlayers))

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

                    #print("!!! Name: %s | Pilot: %s | Finish: %s | Archetype: %s" % (deck.name, deck.pilot, deck.finish, deck.archetype))
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

        index += 1

    print(index)


if __name__== "__main__":
    main()