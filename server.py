from twisted.internet import reactor
from twisted.internet.protocol import Protocol, connectionDone
from twisted.internet.protocol import ServerFactory as ServFactory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.python import failure


class Server(Protocol):
    def __init__(self, clients):
        self.clients = clients
        self.name = ""

    def connectionMade(self):
        print("New connection")

    def add_user(self, name):
        if name not in self.clients:
            self.clients[self] = name
            self.name = name
        else:
            self.transport.write("Wrong username, try another".encode("utf-8"))

    def send_message(self, data, receiver=None):
        if receiver:
            receiver.transport.write(f"{self.name}: {data}".encode("utf-8"))
        else:
            self.transport.write(data.encode("utf-8"))

    def dataReceived(self, data):
        data = data.decode("utf-8")
        if not self.name:
            self.add_user(data)
            return

        for protocol in self.clients.keys():
            if protocol != self:
                self.send_message(data, protocol)

    def connectionLost(self, reason: failure.Failure = connectionDone):
        del self.clients[self]


class ServerFactory(ServFactory):
    def __init__(self):
        self.clients = {}

    def buildProtocol(self, addr):
        return Server(self.clients)


if __name__ == '__main__':
    endpoint = TCP4ServerEndpoint(reactor, 12345)
    endpoint.listen(ServerFactory())
    reactor.run()
