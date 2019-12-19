class Thread(threading.Thread):
    def __init__(self, threadID, name, counter, json):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        threadLimiter.acquire()

        print("Starting " + self.name)




        print("Exiting " + self.name)

        threadLimiter.release()

def print_time(threadName, counter, delay):
    while counter:
        time.sleep(delay)
        print("%s: %s" % (threadName, time.ctime(time.time())))
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