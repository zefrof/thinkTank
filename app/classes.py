import threading, time

threadLimiter = threading.BoundedSemaphore(4)

class Thread(threading.Thread):
    def __init__(self, threadID, name, counter, json):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.json = json
    def run(self):
        threadLimiter.acquire()

        print("Starting " + self.name)

        self.printJson(self.name, self.counter, 1, self.json)

        print("Exiting " + self.name)

        threadLimiter.release()

    def printJson(self, threadName, counter, delay, json):
        while counter:
            time.sleep(delay)
            print("%s: %s - %s" % (threadName, time.ctime(time.time()), json))
            counter -= 1

class card:
    name = ""
    manaCost = ""
    cmc = 0
    typeLine = ""
    oracleText = ""

    def __init__(self):
        pass

class deck:
    name = ""
    archetype = ""
    pilot = ""
    finish = 0

class event:
    name = ""
    date = ""
    location = ""