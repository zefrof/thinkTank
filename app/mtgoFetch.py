import requests, re, datetime
from bs4 import BeautifulSoup
from eventFetch import urlFilter

def main():
	yesterday = yesterday = datetime.date.today() - datetime.timedelta(1)
	yesterday = yesterday.strftime('%m/%d/%Y')
	today = datetime.datetime.today().strftime('%m/%d/%Y')
	
	url = "https://magic.wizards.com/en/section-articles-see-more-ajax?l=en&f=9041&search-result-theme=&limit=20&fromDate=" + yesterday + "&toDate=" + today + "&sort=DESC&word=&offset=0"

	page = requests.get(url)
	j = page.json()
	
	text = BeautifulSoup(str(j['data']), features="html.parser")

	for a in text.find_all('a', href=True):
		#print("https://magic.wizards.com" + a['href'])
		urlFilter("https://magic.wizards.com" + a['href'])
		

if __name__== "__main__":
	main()