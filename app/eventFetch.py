import requests
from bs4 import BeautifulSoup
from classes import Event, Database

def main():

    errCount = 0
    url = "https://www.tcdecks.net/deck.php?id="

    index = 1
    while errCount < 5:
        page = requests.get(url + str(index))

        if(page.status_code == 404):
            errCount += 1
            continue

        event = Event()

        text = BeautifulSoup(page.text, "html.parser")
        split = text.find('h5').text.split('|')

        event.format = split[0].replace("Format:", "")
        event.format = event.format.replace("Archive", "")
        event.format = event.format.strip()

        event.numPlayers = split[1].replace("Number of Players:", "")
        event.numPlayers = event.numPlayers.strip()

        event.date = split[2].replace("Date:", "")
        event.date = event.date.strip()

        event.name = text.find('h3').text

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

        index += 1

        if index == 5:
            break




if __name__== "__main__":
    main()