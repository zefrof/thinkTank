import threading, time

threadLimiter = threading.BoundedSemaphore(4)

class Thread(threading.Thread):
    def __init__(self, threadId, json):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.json = json
    def run(self):
        threadLimiter.acquire()

        print(self.json['name'])

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