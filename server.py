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
        
if not os.path.exists("data_to_send"):
    os.mkdir("data_to_send")

online_clients = {}


class Server(Protocol):
    def connectionMade(self):
        print(f"Неавторизовнный пользователь {self} подключился")
        self.login = None
        
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

    def dataReceived(self, data):
        try:
            data = json.loads(data.decode("utf-8"))
        except UnicodeDecodeError:
            self.send_message(message="Cannot decode, use utf-8", type="error")
            return
        except json.JSONDecodeError:
            self.send_message(message="Cannot decode, use json", type="error")
            return
        
        if data["type"] == "new_registration":
            self.new_registration(data)
        elif data["type"] == "authorize":
            self.authorize(data)
        
    def connectionLost(self, reason: failure.Failure = connectionDone):

        if self.login:
            print(f"Соединение с пользователем '{self.login}' потеряно")
            del online_clients[self.login]
        else:
            print(f"Неавторизованный пользователь {self} отключился")

    '''REQUESTS'''

    def new_registration(self, data):
        login = data["login"]
        password = data["password"]
        if login not in clients:
            new_client = {login: password}
            clients.update(new_client)
            self.send_message(type="new_registration", answer="allow")
            with open('clients.json', "w") as f:
                json.dump(clients, f, indent=4)
        else:
            self.send_message(type="new_registration", answer="forbid")

    def authorize(self, data):
        login = data["login"]
        password = data["password"]
        if login not in clients:
            self.send_message(type="authorize", answer="wrong_login")
        elif password != clients[login]:
            self.send_message(type="authorize", answer="wrong_password")
        else:
            '''сделать отправку data_to_send'''
            self.login = login
            print(f"Пользователь '{self.login}' авторизовался")
            online_clients[self.login] = self
            self.send_message(type="authorize", answer="allow")


class ServerFactory(ServFactory):
    def __init__(self):
        pass

    def buildProtocol(self, addr):
        return Server()


if __name__ == '__main__':
    endpoint = TCP4ServerEndpoint(reactor, 8080)
    endpoint.listen(ServerFactory())
    reactor.run()
