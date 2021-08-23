from classes.general import Database
from collections import defaultdict

#https://stackoverflow.com/questions/40598532/finding-keys-with-most-values-in-dictionary
def max_card(db, offset = 0):
	maxcount = max(len(v) for v in db.values())
	return [k for k, v in db.items() if len(v) == maxcount - offset]

def main():
	#cards_input = ['Lightning Bolt', 'Lava Spike', 'Mountain']
	#cards_input = ['Sylvan Caryatid', 'Goblin Trashmaster', 'Conclave Phalanx']
	cards_input = ['Grapeshot', 'Fatal Push', 'Stoneforge Mystic']

	card_query = 'SELECT c.id FROM cards c WHERE ( '
	for c in cards_input:
		card_query += 'c.name = %s OR '

	card_query = card_query[:-3]
	card_query += ') AND c.uniqueCard = 1;'

	#print(card_query)

	dbm = Database()
	with dbm.con:
		dbm.cur.execute(card_query, tuple(cards_input))
		card_ids = dbm.cur.fetchall()
		card_ids = [x for x, in card_ids]

		results = []
		for cId in card_ids:
			dbm.cur.execute("SELECT ctc.card1_id, ctc.card2_id, ctc.percent FROM cardToCard ctc WHERE (ctc.card1_id = %s OR ctc .card2_id  = %s) AND ctc.percent > 0.005 ORDER BY ctc.percent DESC LIMIT 10", (cId, cId))
			results.append(dbm.cur.fetchall())

		#print(card_ids[0])

		card_dict = defaultdict(set)
		for x in results:
			for item in x:
				#print(item[0] + "   " + item[1])
				if item[0] == card_ids[0]:
					#print("match 1")
					card_dict[item[1]].add(item[2])
				else:
					#print("match 2")
					card_dict[item[0]].add(item[2])
		#print(card_dict)

		#print(max_card(card_dict))

		if len(card_dict) == 0:
			#Return no results found
			print("no results found")
			quit()
		
		results = []
		offset = 0
		while len(results) < 7:
			results.extend(max_card(card_dict, offset))
			offset += 1

		print(results)

if __name__ == "__main__":
	main()