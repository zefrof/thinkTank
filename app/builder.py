from classes.general import Database
from collections import defaultdict
from itertools import combinations

def main():
	dbm = Database()
	formats = [1, 4, 5, 6, 7, 8]
	with dbm.con:
		# Remove uniqueCards so new ones can be set. Truncate cardToCard for updated values
		dbm.cur.execute("UPDATE cards SET uniqueCard = 0")
		dbm.cur.execute("TRUNCATE TABLE cardToCard")

		# https://stackoverflow.com/questions/6011052/selecting-rows-with-the-highest-date
		dbm.cur.execute("SELECT c.name, c.id FROM cards c INNER JOIN (SELECT name, MAX(releaseDate) as TopDate FROM cards GROUP BY name) AS EachItem ON EachItem.TopDate = c.releaseDate AND EachItem.name = c.name GROUP BY c.name")
		cards = dbm.cur.fetchall()
		for c in cards:
			dbm.cur.execute("UPDATE cards SET uniqueCard = 1 WHERE id = %s", (c[1], ))
		
		for form in formats:
			dbm.cur.execute("""SELECT c.id, c.name, ctd.deckId FROM cards c 
			JOIN cardToDeck ctd ON ctd.cardId = c.id 
			JOIN deckToEvent dte ON dte.deckId = ctd.deckId 
			JOIN eventToFormat etf ON etf.eventId = dte.eventId 
			WHERE etf.formatId = %s
			ORDER BY ctd.deckId""", (form, ))
			decks = dbm.cur.fetchall()
			
			deck_set = set()
			card_set = set()
			card_dict = defaultdict(set)
			for card_id, card_name, deck_id in decks:
				deck_set.add(deck_id)
				card_set.add(card_name)
				card_dict[card_name].add(deck_id)
				
			deck_count = len(deck_set)
			
			cards_id_dict = dict(cards)
			#print(cards_id_dict['Lightning Bolt'])
			for card1, card2 in combinations(card_set, 2):
				shared_decks = card_dict[card1] & card_dict[card2]
				deckPerc = len(shared_decks) / deck_count
				if deckPerc > 0:
					#print(f'{card1} + {card2}: {deckPerc}') # needs to go into the db
					#print(f'{cards_id_dict[card1]} + {cards_id_dict[card2]}: {deckPerc}')
					dbm.cur.execute("INSERT INTO cardToCard (card1_id, card2_id, percent, format) VALUES (%s, %s, %s, %s)", (cards_id_dict[card1], cards_id_dict[card2], deckPerc, form))

		#Now to it once more for commander decks
		cmdr_format = 10
		dbm.cur.execute("""SELECT c.id, c.name, ctc.deckId FROM cards c 
			JOIN cardToCommander ctc ON ctc.cardId = c.id 
			ORDER BY ctc.deckId""")
		decks = dbm.cur.fetchall()

		deck_set = set()
		card_set = set()
		card_dict = defaultdict(set)
		for card_id, card_name, deck_id in decks:
			deck_set.add(deck_id)
			card_set.add(card_name)
			card_dict[card_name].add(deck_id)
				
		deck_count = len(deck_set)

		cards_id_dict = dict(cards)
		#print(cards_id_dict['Lightning Bolt'])
		for card1, card2 in combinations(card_set, 2):
			shared_decks = card_dict[card1] & card_dict[card2]
			deckPerc = len(shared_decks) / deck_count
			if deckPerc > 0:
				#print(f'{card1} + {card2}: {deckPerc}') # needs to go into the db
				#print(f'{cards_id_dict[card1]} + {cards_id_dict[card2]}: {deckPerc}')
				dbm.cur.execute("INSERT INTO cardToCard (card1_id, card2_id, percent, format) VALUES (%s, %s, %s, %s)", (cards_id_dict[card1], cards_id_dict[card2], deckPerc, cmdr_format))

		#And one last time for every deck (kitchen table)
		dbm.cur.execute("""SELECT c.id, c.name, ctd.deckId FROM cards c 
			JOIN cardToDeck ctd ON ctd.cardId = c.id 
			JOIN deckToEvent dte ON dte.deckId = ctd.deckId 
			JOIN eventToFormat etf ON etf.eventId = dte.eventId 
			ORDER BY ctd.deckId""", (form, ))
		decks = dbm.cur.fetchall()
			
		deck_set = set()
		card_set = set()
		card_dict = defaultdict(set)
		for card_id, card_name, deck_id in decks:
			deck_set.add(deck_id)
			card_set.add(card_name)
			card_dict[card_name].add(deck_id)
				
		deck_count = len(deck_set)
			
		cards_id_dict = dict(cards)
		#print(cards_id_dict['Lightning Bolt'])
		for card1, card2 in combinations(card_set, 2):
			shared_decks = card_dict[card1] & card_dict[card2]
			deckPerc = len(shared_decks) / deck_count
			if deckPerc > 0:
				#print(f'{card1} + {card2}: {deckPerc}') # needs to go into the db
				#print(f'{cards_id_dict[card1]} + {cards_id_dict[card2]}: {deckPerc}')
				dbm.cur.execute("INSERT INTO cardToCard (card1_id, card2_id, percent, format) VALUES (%s, %s, %s, %s)", (cards_id_dict[card1], cards_id_dict[card2], deckPerc, form))

if __name__ == "__main__":
	main()