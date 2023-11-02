from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory as ClFactory
from twisted.internet.endpoints import TCP4ClientEndpoint


class Client(Protocol):
    def __init__(self):
        reactor.callInThread(self.send_data)

    def connectionMade(self):
        print("Write your name")

    def dataReceived(self, data):
        print(data.decode("utf-8"))

    def send_data(self):
        while True:
            self.transport.write(input().encode("utf-8"))


class ClientFactory(ClFactory):
    def buildProtocol(self, addr):
        return Client()

    def clientConnectionFailed(self, connector, reason):
        print(reason)
        ClFactory.clientConnectionFailed(self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        print(reason)
        ClFactory.clientConnectionLost(self, connector, reason)


if __name__ == '__main__':
    endpoint = TCP4ClientEndpoint(reactor, "localhost", 12345)
    endpoint.connect(ClientFactory())
    reactor.run()
