from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, connectionDone
from twisted.internet.protocol import ReconnectingClientFactory as ClFactory
from twisted.internet.endpoints import TCP4ClientEndpoint
from sys import stderr
import json
import tkinter as tk
import os
from time import sleep

from twisted.python import failure

import GUI
from tkinter import messagebox
from twisted.internet import tksupport



class Client(Protocol, GUI.Interface):

    def connectionMade(self):
        self.close_with_x = False
        self.run()
        self.root.protocol("WM_DELETE_WINDOW", self.stop_reactor_and_exit)
        tksupport.install(self.root, reactor=reactor)

    def stop_reactor_and_exit(self):
        self.close_with_x = True
        reactor.stop()

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
            print(data.get("message", "Unknown error"), file=stderr)
        elif data["type"] == "new_registration":
            self.registration(data)
        elif data["type"] == "authorize":
            self.authorize(data)
        elif data["type"] == "find_client":
            self.find_client(data)

    def connectionLost(self, reason: failure.Failure = connectionDone):
        if not self.close_with_x:
            messagebox.showerror("ERROR", message="Соединение потеряно")
            self.stop_reactor_and_exit()

    def send_data(self, **kwargs):
        self.transport.write(self.__encode_json(kwargs).encode("utf-8"))

    # def message_input(self):
    #     while True:
    #         self.send_data(value=input("value: "), type=input("type: "))

    '''BUTTON FUNCTIONS'''
    def new_registration_func(self):
        login = self.login_entry.get()
        password = self.password_entry.get()
        self.send_data(type="new_registration", login=login,  password=password)

    def enter_func(self):
        login = self.login_entry.get()
        password = self.password_entry.get()
        self.send_data(type="authorize", login=login, password=password)

    def find_client_button_command(self):
        client = self.find_client_entry.get()
        self.send_data(type="find_client", client=client)

    def open_chat_with_client(self, selected_client):
        self.chat_widgets()
        self.another_client.config(text=selected_client)
        self.chat.config(state=tk.NORMAL)
        if not os.path.exists(f"{self.login}_chats"):
            os.mkdir(f"{self.login}_chats")
            with open(f"{self.login}_chats\\{selected_client}.txt", "w"):
                pass
        with open(f"{self.login}_chats\\{selected_client}.txt", "r") as f:
            chat = f.read()
        self.chat.insert(tk.END, chat)

    '''REQUESTS'''
    def registration(self, data):
        if data["answer"] == "allow":
            messagebox.showinfo(message="Вы успешно зарегистрировались")
            self.registration_window.destroy()
            self.authorize_widgets()
        else:
            messagebox.showinfo(message="Пользователь с таким логином уже заргистрирован")

    def authorize(self, data):
        if data["answer"] == "wrong_login":
            messagebox.showinfo(message="Пользователя с такм логином не существует")
        elif data["answer"] == "wrong_password":
            messagebox.showinfo(message="Неправильный пароль")
        else:
            self.login = data["login"]
            self.messenger_widgets()

    def find_client(self, data):
        if data["answer"] == False:
            messagebox.showinfo(message="Такого пользователя не существует")
        else:
            self.open_chat_with_client(data["client"])


class ClientFactory(ClFactory):
    def buildProtocol(self, addr):
        return Client()

    def clientConnectionLost(self, connector, unused_reason):
        print(unused_reason)
        pass

    def clientConnectionFailed(self, connector, reason):
        print(reason)
        pass


def handle_error(failure):
    messagebox.showerror(message="Ошибка подключения к серверу", title="ERROR")
    reactor.stop()


if __name__ == '__main__':
    endpoint = TCP4ClientEndpoint(reactor, "localhost", 8080)
    con = endpoint.connect(ClientFactory())
    con.addErrback(handle_error)
    reactor.run()