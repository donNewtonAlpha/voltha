from twisted.internet import defer, reactor


@defer.inlineCallbacks
def get_arg():
    retval = yield another_async_func()
    defer.returnValue(retval)


@defer.inlineCallbacks
def print_file():
    try:
        arg = yield get_arg()
    except Exception as err:
        arg = None

    try:
        file_ = yield async_get_file(arg)
        yield async_print_file(file_)
        print "Success."
    except Exception as err:
        print "Error", err
    finally:
        print "Shutting down"
        reactor.stop()


if __name__ == '__main__':
    print_file()
    reactor.run()