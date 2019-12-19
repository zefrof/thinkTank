import threading, time, requests

threadLimiter = threading.BoundedSemaphore(4)

class Thread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        threadLimiter.acquire()

        print("Starting " + self.name)
        print_time(self.name, 5, self.counter)
        print("Exiting " + self.name)

        threadLimiter.release()

def print_time(threadName, counter, delay):
    while counter:
        time.sleep(delay)
        print("%s: %s" % (threadName, time.ctime(time.time())))
        counter -= 1

def download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()
    r.close()
    return local_filename

def main():

    cardData = download_file("https://archive.scryfall.com/json/scryfall-default-cards.json")

    print(cardData)

    threads = []

    for i in range(0, 10):
        threadX = Thread(i, "Thread-" + str(i), i)
        threads.append(threadX)
        threadX.start()

    for t in threads:
        t.join()

    print("exiting main()")

if __name__== "__main__":
  main()