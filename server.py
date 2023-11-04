from twisted.internet import reactor
from twisted.internet.protocol import Protocol, connectionDone
from twisted.internet.protocol import ServerFactory as ServFactory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.python import failure
import json
import os


if not os.path.exists('clients.json'):
    clients = {}
else:
    with open('clients.json', "r") as f:
        clients = json.load(f)


class Server(Protocol):
    def connectionMade(self):
        pass

    @staticmethod
    def __encode_json(**kwargs):
        return json.dumps(kwargs)

    def send_message(self, **kwargs):
        if kwargs.get("receiver"):
            receiver = kwargs["receiver"]
            del kwargs["receiver"]
            receiver.transport.write(self.__encode_json(**kwargs).encode("utf-8"))
        else:
            print(kwargs)
            self.transport.write(self.__encode_json(**kwargs).encode("utf-8"))

    def dataReceived(self, data):
        try:
            data = json.loads(data.decode("utf-8"))
        except UnicodeDecodeError:
            self.send_message(message="Cannot decode, use utf-8", type="error")
            return
        except json.JSONDecodeError:
            self.send_message(message="Cannot decode, use json", type="error")
            return
        # if not self.name:
        #     self.add_user(data)
        #     return
        if not data.get("type"):
            self.send_message(message="Wrong data", type="error")
        elif data["type"] == "new_registration":
            login = data["login"]
            password = data["password"]
            if login not in clients:
                new_client = {login: {"password": password,
                                "protocol": f"{self}",
                                "need_to_send": ""
                                      }}
                clients.update(new_client)
                self.send_message(type="new_registration", answer="allow")
                with open('clients.json', "w") as f:
                    json.dump(clients, f, indent=4)
            else:
                self.send_message(type="new_registration", answer="forbid")

    def disconnect(self):
        "сделать офлайн статус"
        print("Пользователь отлючился")

    def connectionLost(self, reason: failure.Failure = connectionDone):
        print("Соединение с пользователем потеряно")
        self.disconnect()


class ServerFactory(ServFactory):
    def __init__(self):
        pass

    def buildProtocol(self, addr):
        return Server()


if __name__ == '__main__':
    endpoint = TCP4ServerEndpoint(reactor, 12345)
    endpoint.listen(ServerFactory())
    reactor.run()
