import requests
from classes.general import Database

def main():
	dbm = Database()
	url = 'https://api.moxfield.com/v2/decks/search?pageNumber=1&pageSize=100&sortType=updated&sortDirection=Descending&fmt=commander&filter='
	page = requests.get(url)
	j = page.json()

	for pub_id in j['data']:
		#deck_url = 'https://www.moxfield.com/decks/jt0J-87-dE6oJq1PtTFyZQ'
		deck_url = 'https://api.moxfield.com/v2/decks/all/' + pub_id['publicId']

		page = requests.get(deck_url)
		deck = page.json()

		with dbm.con:
			#print(deck)
			deck_id = deck['id']
			deck_name = deck['name']
			deck_url = deck['publicUrl']

			#Prevent duplicate issue
			dbm.cur.execute("SELECT id FROM commanderDecks WHERE id = %s", (deck_id, ))
			if dbm.cur.rowcount == 1:
				dbm.cur.execute("DELETE FROM commanderDecks WHERE id = %s", (deck_id, ))
			
			dbm.cur.execute("INSERT INTO commanderDecks (id, name, url) VALUES (%s, %s, %s)", (deck_id, deck_name, deck_url))

			card_query = "INSERT IGNORE INTO cardToCommander (cardId, deckId, copies, commander) VALUES "
			values_list = []
			for card in deck['mainboard']:
				card_query = card_query + "(%s, %s, %s, %s), "
				values_list.append(deck['mainboard'][card]['card']['scryfall_id'])
				values_list.append(deck_id)
				values_list.append(deck['mainboard'][card]['quantity'])
				values_list.append(0)
			dbm.cur.execute(card_query[:-2], tuple(values_list))

			card_query = "INSERT INTO cardToCommander (cardId, deckId, copies, commander) VALUES "
			values_list = []
			for card in deck['commanders']:
				card_query = card_query + "(%s, %s, %s, %s), "
				values_list.append(deck['commanders'][card]['card']['scryfall_id'])
				values_list.append(deck_id)
				values_list.append(deck['commanders'][card]['quantity'])
				values_list.append(1)
			dbm.cur.execute(card_query[:-2], tuple(values_list))

			#for card in deck['companions']:

if __name__ == "__main__":
	main()