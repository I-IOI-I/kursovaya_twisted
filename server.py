from twisted.internet import reactor
from twisted.internet.protocol import Protocol, connectionDone
from twisted.internet.protocol import ServerFactory as ServFactory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.python import failure
import json


class Server(Protocol):
    def __init__(self, clients, my_id):
        self.clients = clients
        self.another_client = None
        self.my_id = my_id

    def connectionMade(self):
        self.clients[self.my_id] = self
        print(self.clients)

    # def add_user(self, name):
    #     if name not in self.clients:
    #         self.clients[self.my_id] = self

    @staticmethod
    def __encode_json(**kwargs):
        return json.dumps(kwargs)

    def send_message(self, **kwargs):
        if kwargs.get("receiver"):
            receiver = kwargs["receiver"]
            del kwargs["receiver"]
            receiver.transport.write(self.__encode_json(**kwargs).encode("utf-8"))
        else:
            self.transport.write(self.__encode_json(**kwargs).encode("utf-8"))
        # if receiver:
        #     receiver.transport.write(data.encode("utf-8"))
        # else:
        #     self.transport.write(data.encode("utf-8"))

    def dataReceived(self, data):
        try:
            data = json.loads(data.decode("utf-8"))
        except UnicodeDecodeError:
            self.send_message(value="Cannot decode, use utf-8", type="error")
            return
        except json.JSONDecodeError:
            self.send_message(value="Cannot decode, use json", type="error")
            return
        # if not self.name:
        #     self.add_user(data)
        #     return
        if not data.get("type") or not data.get("value"):
            self.send_message(value="Wrong data", type="error")
            return

        if data["type"] == "user_choose":
            try:
                another_client = int(data["value"])
                if another_client in self.clients.keys():
                    self.another_client = another_client
                else:
                    raise KeyError
            except KeyError:
                self.send_message(value="Can't find that client", type="error")
            except ValueError:
                self.send_message(value="Write another id as int", type="error")
            else:
                self.send_message(value=f"Talk to {self.another_client}", type="user_chosen")
        elif data["type"] == "new_message":
            if not self.another_client:
                self.send_message(value="Try another client", type="error")
            try:
                self.send_message(value=data["value"], receiver=self.clients[self.another_client], type="new_message")
            except KeyError:
                self.send_message(value="Try another client", type="error")
                self.another_client = None

        # for protocol in self.clients.keys():
        #     if protocol != self:
        #         self.send_message(data, protocol)

    def disconnect(self):
        del self.clients[self.my_id]

    def connectionLost(self, reason: failure.Failure = connectionDone):
        self.disconnect()


class ServerFactory(ServFactory):
    def __init__(self):
        self.clients = {}
        self.last_id = 0

    def buildProtocol(self, addr):
        self.last_id += 1
        return Server(self.clients, self.last_id)


if __name__ == '__main__':
    endpoint = TCP4ServerEndpoint(reactor, 12345)
    endpoint.listen(ServerFactory())
    reactor.run()
