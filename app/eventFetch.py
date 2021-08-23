import requests, re, datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from classes.general import Database
from classes.event import Event
from classes.deck import Deck
from classes.card import Card, Face

def urlFilter(url):
	if isUrl(url):
		if "wizards.com" in url:
			return mtgoScrape(url)
		else:
			return emptyEvent(url)
	else:
		print('not a url')
		return -1

def mtgoScrape(url):
	page = requests.get(url)
	dbm = Database()

	if(page.status_code == 404):
		print("404 Error")
		return -1

	event = Event()

	text = BeautifulSoup(page.content, features="html.parser")
	
	#Event name
	tmp = text.find("div", id="main-content")
	event.name = tmp.find("h1").text

	#Event format
	event.format = event.name.split()[0].strip()

	#Event date
	date = tmp.find("p", class_="posted-in").text.split("on")[1].strip()
	d = datetime.datetime.strptime(date, '%B %d, %Y')
	event.date = d.strftime('%Y-%m-%d')

	#Event source
	event.source = url

	#UN-COMMENT FOR PROD
	if event.eventExists(dbm) == True:
		return 0

	#print("### Name: %s | Date: %s | Format: %s | Players: %s" % (event.name, event.date, event.format, event.numPlayers))
	
	for index, div in enumerate(text.find_all("div", class_="deck-group")):
		deck = Deck()
		
		#Deck pilot
		deck.pilot = div.find("span", class_="deck-meta").text.split()[0].strip()

		#Deck pos
		if "Place" in div.find("span", class_="deck-meta").text:
			tmp = div.find("span", class_="deck-meta").text.split('(')[1].split(')')[0]
			deck.finish = re.sub('[^0-9]', "", tmp)

		event.decks.append(deck)	

		#Deck order
		deck.ord = index

		#print("### Pilot: %s | Finish: %s | Archetype: %s" % (deck.pilot, deck.finish, deck.archetype))

		#Mainboard
		deckText = div.find("div", class_="sorted-by-overview-container")
		
		numbahs = deckText.find_all("span", class_="card-count")
		mainboard = deckText.find_all("span", class_="card-name")

		if len(numbahs) != len(mainboard):
			print("!!! There's a problem with card counts in the mainboard")
		
		for n, m in zip(numbahs, mainboard):
			#print("{} {}".format(n.text, m.text))

			try:
				card = Card()
				cid = card.getCardId(m.text, dbm)
				card.getCard(dbm, cid, 0)
				card.copies = n.text
				deck.cards.append(card)
			except:
				print("{} {}".format(n.text, m.text))

		#Sideboard
		sideText = div.find("div", class_="sorted-by-sideboard-container")

		sideNums = sideText.find_all("span", class_="card-count")
		sideboard = sideText.find_all("span", class_="card-name")

		if len(sideNums) != len(sideboard):
			print("!!! There's a problem with card counts in the sideboard")

		for n, m in zip(sideNums, sideboard):
			#print("{} {}".format(n.text, m.text))
			
			card = Card()
			cid = card.getCardId(m.text, dbm)
			card.getCard(dbm, cid, 0)
			card.sideboard = 1
			card.copies = n.text
			deck.cards.append(card)

	#Event player count
	event.numPlayers = len(event.decks)
	
	event.commitEvent(dbm)

	return event.cid

def emptyEvent(url):
	dbm = Database()
	with dbm.con:
		dbm.cur.execute("INSERT INTO events (name, date, numPlayers, source) VALUES ('MANUAL ENTRY REQUIRED', '0000/00/00', 0, %s)", (url, ))
	return -2

def isUrl(url):
  try:
    result = urlparse(url)
    return all([result.scheme, result.netloc])
  except ValueError:
    return False
	

""" def main():
	url = "https://magic.wizards.com/en/articles/archive/mtgo-standings/legacy-super-qualifier-2020-05-15#decklists"
	
	urlFilter(url)


if __name__== "__main__":
	main() """