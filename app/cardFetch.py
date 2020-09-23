import requests, json, sys
from classes.general import Database
from classes.card import Card, Face

def downloadFile(url):
	localFilename = url.split('/')[-1]
	# NOTE the stream=True parameter below
	with requests.get(url, stream = True) as r:
		r.raise_for_status()
		with open(localFilename, 'wb') as f:
			for chunk in r.iter_content(chunk_size = 8192):
				if chunk: # filter out keep-alive new chunks
					f.write(chunk)
					# f.flush()
	r.close()
	return localFilename

def main():
	getBulkUrl = requests.get("https://api.scryfall.com/bulk-data/default_cards")
	url = getBulkUrl.json()
	
	bulkFile = downloadFile(url['download_uri'])
	#bulkFile = "testFile.json"

	try:
		fd = open(bulkFile, "r", encoding="utf8")
		print("### File downloaded and opened")
	except:
		print("!!! Opening the file failed")
		sys.exit()

	#Connect to the database
	dbm = Database()

	fd.readline()
	for line in fd:
		s = line.strip()
		if s[-1:] is ",":
			s = s[:-1]

		if s is "]":
			break

		try:
			data = json.loads(s)
		except Exception as e:
			print(e)

		card = Card()
		card.setCard(data, dbm)
		card.commitCard(dbm)

	print("Done")

if __name__== "__main__":
	main()