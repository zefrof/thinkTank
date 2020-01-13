import requests, json
from classes import Thread

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
    threads = []

    try:
        fd = open(bulkFile, "r", encoding="utf8")
        print("### File downloaded and opened")
    except:
        print("!!! Opening the file failed")

    i = 0
    fd.readline()
    for line in fd:
        s = line.strip()
        if s[-1:] is ",":
            s = s[:-1]

        try:
            data = json.loads(s)
        except Exception as e:
            print(e)

        #print(data)

        threadX = Thread(i, data)
        threads.append(threadX)
        threadX.start()

        i += 1

        if i == 3:
            break

    for t in threads:
        t.join()

    print("exiting main()")

if __name__== "__main__":
  main()