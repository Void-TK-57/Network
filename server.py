# import main libraries
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

# creat a basic echo protocol
class Echo(Protocol):

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        # increase the numbers of protocols connected of the factory
        self.factory.numProtocols = self.factory.numProtocols + 1
        # initially write to the connetion the initial message
        self.transport.write( "Welcome! There are currently %d open connections.\n" % (self.factory.numProtocols,)) 

    def connectionLost(self, reason):
        # decrease the numbers of protocols connected of the factory
        self.factory.numProtocols = self.factory.numProtocols - 1

    def dataReceived(self, data):
        # write the data back (raw)
        self.transport.write(data)

# main factory
class EchoFactory(Factory):

    def buildProtocol(self, addr):
        return Echo(self)

# 8007 is the port you want to run under. Choose something >1024
reactor.listenTCP(8057, EchoFactory())
reactor.run()