# from howto.lintel.in/inlinecallbacks

import txredisapi as redis

from twisted.internet import defer
from twisted.internet import reactor

def get_text(i):
    return "This is a text string.... number = {}".format(i)

@defer.inlineCallbacks
def start():
    for i in range(0, 20):
        rc = yield get_text(i)
        print rc
    yield stop()

@defer.inlineCallbacks
def stop():
    print("Stopping")
    reactor.stop()


def main():
    start()





if __name__ == "__main__":
    main()
    reactor.run()
    print("Done")