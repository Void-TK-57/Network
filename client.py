# import main libs
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor
from sys import stdout

from functools import partial

# main basic echo protocol
class Echo(Protocol):

    def __init__(self, factory, msg = "hello World"):
        self.factory = factory
        self.msg = msg

    def dataReceived(self, data):
        print("[Server]: " + str(data))
        self.transport.loseConnection()

    def connectionMade(self):
        self.transport.write(self.msg)

class EchoClientFactory(ClientFactory):

    def startedConnecting(self, connector):
        print('Started to connect.')

    def buildProtocol(self, addr):
        print('Connected.')
        return Echo(self)

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)

# if executed
if __name__ == "__main__":
    factory = EchoClientFactory()
    reactor.connectTCP('localhost', 8057, factory)
    reactor.run()