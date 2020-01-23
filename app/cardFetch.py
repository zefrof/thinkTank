import requests, json
from classes import Card

def downloadFile(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream = True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size = 8192):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()
    r.close()
    return local_filename

def main():

    bulkFile = downloadFile("https://archive.scryfall.com/json/scryfall-default-cards.json")
    #bulkFile = "testFile.json"
    threads = []

    try:
        fd = open(bulkFile, "r", encoding="utf8")
        print("### File downloaded and opened")
    except:
        print("!!! Opening the file failed")

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
        card.setCard(data)
        card.commitCard()

    print("Done")

if __name__== "__main__":
  main()