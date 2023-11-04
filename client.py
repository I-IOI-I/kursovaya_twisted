from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory as ClFactory
from twisted.internet.endpoints import TCP4ClientEndpoint
from sys import stderr
import json
import GUI
from tkinter import messagebox
from twisted.internet import tksupport


class Client(Protocol, GUI.Interface):

    def connectionMade(self):
        self.run()
        self.root.protocol("WM_DELETE_WINDOW", self.stop_reactor_and_exit)
        tksupport.install(self.root, reactor=reactor)

    def stop_reactor_and_exit(self):
        reactor.stop()
        self.root.destroy()

    @staticmethod
    def __encode_json(data):
        return json.dumps(data)

    def dataReceived(self, data):
        try:
            data = json.loads(data.decode("utf-8"))
        except UnicodeDecodeError or json.JSONDecodeError:
            print("Something went wrong", file=stderr)
            return
        if data["type"] == "error":
            print(data.get("value", "Unknown error"), file=stderr)
        elif data["type"] == "new_registration":
            if data["answer"] == "allow":
                messagebox.showinfo(message="Вы успешно зарегистрировались")
                self.registration_window.destroy()
                self.authorize_widgets()
            else:
                messagebox.showinfo(message="Пользователь с таким логином уже заргистрирован")
        else:
            print(data.get("value", "no value in the message"))

    def send_data(self, **kwargs):
        self.transport.write(self.__encode_json(kwargs).encode("utf-8"))

    def message_input(self):
        while True:
            self.send_data(value=input("value: "), type=input("type: "))

    '''INTERFACE'''

    def new_registration_func(self):
        login = self.login_entry.get()
        password = self.password_entry.get()
        self.send_data(type="new_registration", login=login,  password=password)


class ClientFactory(ClFactory):
    def buildProtocol(self, addr):
        return Client()

    def clientConnectionLost(self, connector, unused_reason):
        pass

    def clientConnectionFailed(self, connector, reason):
        print(reason)
        pass


def handle_error(failure):
    print(f"Ошибка подключения: {failure.getErrorMessage()}")
    messagebox.showerror("ERROR", message="Ошибка подключения")
    reactor.stop()


if __name__ == '__main__':
    endpoint = TCP4ClientEndpoint(reactor, "localhost", 12345)
    con = endpoint.connect(ClientFactory())
    con.addErrback(handle_error)
    reactor.run()