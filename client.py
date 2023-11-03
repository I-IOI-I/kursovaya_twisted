from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ReconnectingClientFactory as ClFactory
from twisted.internet.endpoints import TCP4ClientEndpoint
from sys import stderr
import json


class Client(Protocol):
    def __init__(self):
        reactor.callInThread(self.message_input)

    @staticmethod
    def __encode_json(**kwargs):
        return json.dumps(kwargs)

    def connectionMade(self):
        pass

    def dataReceived(self, data):
        try:
            data = json.loads(data.decode("utf-8"))
        except UnicodeDecodeError or json.JSONDecodeError:
            print("Something went wrong", file=stderr)
            return
        if data["type"] == "error":
            print(data.get("value", "Unknown error"), file=stderr)
        else:
            print(data.get("value", "no value in the message"))

    def send_data(self, **kwargs):
        self.transport.write(self.__encode_json(**kwargs).encode("utf-8"))

    def message_input(self):
        while True:
            self.send_data(value=input("value: "), type=input("type: "))


class ClientFactory(ClFactory):
    def buildProtocol(self, addr):
        return Client()

    # def clientConnectionFailed(self, connector, reason):
    #     print(reason)
    #     ClFactory.clientConnectionFailed(self, connector, reason)

    # def clientConnectionLost(self, connector, reason):
    #     print(reason)
    #     ClFactory.clientConnectionLost(self, connector, reason)
    def clientConnectionLost(self, connector, unused_reason):
        self.retry(connector)

    def clientConnectionFailed(self, connector, reason):
        print(reason)
        self.retry(connector)


if __name__ == '__main__':
    endpoint = TCP4ClientEndpoint(reactor, "localhost", 12345)
    endpoint.connect(ClientFactory())
    reactor.run()
