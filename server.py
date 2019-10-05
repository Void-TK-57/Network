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
        print("Connection Made")

    def connectionLost(self, reason):
        print("Connection Lost")

    def dataReceived(self, data):
        print("[Client]:" + str(data))
        self.transport.write(data.upper())

# main factory
class EchoFactory(Factory):

    def buildProtocol(self, addr):
        return Echo(self)

# 8007 is the port you want to run under. Choose something >1024
reactor.listenTCP(8057, EchoFactory())
reactor.run()