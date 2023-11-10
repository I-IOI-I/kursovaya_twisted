from twisted.internet import reactor
from twisted.internet.protocol import Protocol, connectionDone
from twisted.internet.protocol import ServerFactory as ServFactory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.python import failure
import json
import os
import csv


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
        return json.dumps(kwargs) + "\n"

    def send_data(self, **kwargs):
        if kwargs.get("receiver"):
            receiver = online_clients[kwargs["receiver"]]
            del kwargs["receiver"]
            receiver.transport.write(self.__encode_json(**kwargs).encode("utf-8"))
        else:
            self.transport.write(self.__encode_json(**kwargs).encode("utf-8"))

    def dataReceived(self, data):
        try:
            data = json.loads(data.decode("utf-8"))
        except UnicodeDecodeError:
            self.send_data(message="Cannot decode, use utf-8", type="error")
            return
        except json.JSONDecodeError:
            self.send_data(message="Cannot decode, use json", type="error")
            return
        
        if data["type"] == "new_registration":
            self.new_registration(data)
        elif data["type"] == "authorize":
            self.authorize(data)
        elif data["type"] == "find_client":
            self.find_client(data)
        elif data["type"] == "send_message":
            self.process_the_message(data)
        
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
            self.send_data(type="new_registration", answer="allow")
            with open('clients.json', "w") as f:
                json.dump(clients, f, indent=4)
        else:
            self.send_data(type="new_registration", answer="forbid")

    def authorize(self, data):
        login = data["login"]
        password = data["password"]
        if login not in clients:
            self.send_data(type="authorize", answer="wrong_login")
        elif password != clients[login]:
            self.send_data(type="authorize", answer="wrong_password")
        else:
            #сделать отправку data_to_send
            self.login = login
            print(f"Пользователь '{self.login}' авторизовался")
            online_clients[self.login] = self
            self.send_data(type="authorize", answer="allow", login=login)
            if os.path.exists(f"data_to_send\\{self.login}.csv"):
                with open(f"data_to_send\\{self.login}.csv", "r") as f:
                    reader = csv.DictReader(f, delimiter=",", lineterminator="\r")
                    for row in reader:
                        self.send_data(type=row["type"], sender=row["sender"], date=row["date"], message=row["message"])

    def find_client(self, data):
        client = data["client"]
        if client not in clients:
            self.send_data(type="find_client", answer=False)
        else:
            self.send_data(type="find_client", answer=True, client=client)

    def process_the_message(self, data):
        if data["receiver"] in online_clients:
            self.send_data(**data)
        else:
            if not os.path.exists(f"data_to_send\\{data['receiver']}.csv"):
                with open(f"data_to_send\\{data['receiver']}.csv", "w") as f:
                    writer = csv.writer(f)
                    headers = ["type", "sender", "date", "message"]
                    writer.writerow(headers)
            with open(f"data_to_send\\{data['receiver']}.csv", "a") as f:
                del data["receiver"]
                writer = csv.writer(f, delimiter=",", lineterminator="\r")
                row = [v for i, v in data.items()]
                writer.writerow(row)


class ServerFactory(ServFactory):
    def __init__(self):
        pass

    def buildProtocol(self, addr):
        return Server()


if __name__ == '__main__':
    endpoint = TCP4ServerEndpoint(reactor, 8080)
    endpoint.listen(ServerFactory())
    reactor.run()
