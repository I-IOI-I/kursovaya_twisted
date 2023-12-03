import csv
import datetime
import json
import os
import tkinter as tk
from sys import stderr
from tkinter import messagebox

from twisted.internet import defer, reactor, tksupport
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ReconnectingClientFactory as ClFactory
from twisted.internet.protocol import connectionDone
from twisted.python import failure

import GUI


class Client(Protocol, GUI.Interface):
    """Класс, представляющий клиентское приложение"""
    def connectionMade(self):
        """Вызывается при установлении соединения с сервером"""
        self.close_with_x = False
        self.run()
        self.root.protocol("WM_DELETE_WINDOW", self.stop_reactor_and_exit)
        tksupport.install(self.root, reactor=reactor)
        self.another_client = None

    def stop_reactor_and_exit(self):
        """Останавливает реактор и выходит из приложения"""
        self.close_with_x = True
        reactor.stop()

    @staticmethod
    def __encode_json(data):
        """Кодирует данные в формат JSON"""
        return json.dumps(data)

    def dataReceived(self, data):
        """Вызывается при получении данных с сервера"""
        _data = data.decode("utf-8").split("\n")
        for data in _data:
            if data == "":
                continue
            try:
                data = json.loads(data)
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
            elif data["type"] == "send_message":
                del data["type"]
                self.save_message(**data)

    def connectionLost(self, reason: failure.Failure = connectionDone):
        """Вызывается при потере соединения с сервером"""
        if not self.close_with_x:
            messagebox.showerror("ERROR", message="Соединение потеряно")
            self.stop_reactor_and_exit()

    def send_data(self, **kwargs):
        """Отправляет заданные аргументы в виде данных на сервер"""
        self.transport.write(self.__encode_json(kwargs).encode("utf-8"))

    """BUTTON FUNCTIONS"""

    def delete_from_recent_clients(self, event):
        """Удаляет выбранного клиента из списка последних клиентов"""
        selected_index = self.recent_clients.curselection()
        if selected_index:
            self.recent_clients.delete(selected_index)

    def new_registration_func(self):
        """Обрабатывает событие регистрации"""
        login = self.login_entry.get()
        password = self.password_entry.get()
        self.send_data(type="new_registration", login=login, password=password)

    def enter_func(self):
        """Обрабатывает событие авторизации"""
        login = self.login_entry.get()
        password = self.password_entry.get()
        self.send_data(type="authorize", login=login, password=password)

    def find_client_button_command(self):
        """Обрабатывает событие поиска клиента"""
        client = self.find_client_entry.get()
        self.send_data(type="find_client", client=client)

    def send_message_button_command(self, event=False):
        """Обрабатывает событие нажатия кнопки отправки сообщения"""
        message = self.message_enter.get()
        if not message:
            return
        receiver = self.another_client
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.message_enter.delete(0, tk.END)
        self.save_message(
            from_myself=True,
            sender=self.login,
            receiver=receiver,
            date=date,
            message=message,
        )
        if receiver != self.login:
            self.send_data(
                type="send_message",
                sender=self.login,
                receiver=receiver,
                date=date,
                message=message,
            )

    """RESPONES"""

    def registration(self, data):
        """Обрабатывает ответ сервера на регистрацию"""
        if data["answer"] == "allow":
            messagebox.showinfo(message="Вы успешно зарегистрировались")
            self.registration_window.destroy()
            self.authorize_widgets()
        else:
            messagebox.showinfo(
                message="Пользователь с таким логином уже заргистрирован"
            )

    def authorize(self, data):
        """Обрабатывает ответ сервера на авторизацию"""
        if data["answer"] == "wrong_login":
            messagebox.showinfo(message="Пользователя с такм логином не существует")
        elif data["answer"] == "wrong_password":
            messagebox.showinfo(message="Неправильный пароль")
        else:
            self.login = data["login"]
            if not os.path.exists(f"{self.login}_chats"):
                os.mkdir(f"{self.login}_chats")
            self.messenger_widgets()
            self.root.title(f"Мессенджер {self.login}")
            self.fill_recent_clients_listbox()

    def find_client(self, data):
        """Обрабатывает ответ сервера на поиска клиента"""
        if not data["answer"]:
            messagebox.showinfo(message="Такого пользователя не существует")
        else:
            self.open_chat_with_client(data["client"])

    """OTHER"""

    def fill_recent_clients_listbox(self):
        """Заполняет поле списка недавних клиентов последними клиентами"""
        if not os.path.exists(f"{self.login}_recent_clients.txt"):
            with open(f"{self.login}_recent_clients.txt", "w"):
                pass
        with open(f"{self.login}_recent_clients.txt", "r") as f:
            recent_clients_list = [line.rstrip("\n") for line in f]
            self.recent_clients_list_var = tk.StringVar(value=recent_clients_list)
            self.recent_clients.config(listvariable=self.recent_clients_list_var)

    def open_chat_with_client(self, selected_client):
        """Открывает окно чата с выбранным клиентом"""
        self.another_client = selected_client
        self.chat_widgets()
        self.chat.config(text="Чат с пользователем " + self.another_client)
        if not os.path.exists(f"{self.login}_chats\\{selected_client}.csv"):
            with open(f"{self.login}_chats\\{selected_client}.csv", "w") as f:
                writer = csv.writer(f, delimiter=",", lineterminator="\r")
                headers = ["sender", "date", "message"]
                writer.writerow(headers)
        with open(f"{self.login}_chats\\{selected_client}.csv", "r") as f:
            file_reader = csv.DictReader(f, delimiter=",")
            for message in file_reader:
                self.pack_message(message)

    def save_message(self, from_myself=False, **data):
        """Сохраняет данные сообщения в файл чата"""
        if from_myself:
            sender = data["receiver"]
        else:
            sender = data["sender"]
        del data["receiver"]
        if not os.path.exists(f"{self.login}_chats\\{sender}.csv"):
            with open(f"{self.login}_chats\\{sender}.csv", "w") as f:
                writer = csv.writer(f, delimiter=",", lineterminator="\r")
                headers = ["sender", "date", "message"]
                writer.writerow(headers)
        with open(f"{self.login}_chats\\{sender}.csv", "a") as f:
            file_writer = csv.writer(f, delimiter=",", lineterminator="\r")
            row = [v for i, v in data.items()]
            file_writer.writerow(row)
        if self.recent_clients.get(0) != sender:
            self.raise_the_client_in_listbox(sender)
        if self.another_client and self.another_client == sender:
            self.pack_message(data)

    def raise_the_client_in_listbox(self, client):
        """Поднимает клиента вверх в списке последних клиентов."""
        if client in self.recent_clients.get(0, tk.END):
            self.recent_clients.delete(self.recent_clients.get(0, tk.END).index(client))
        self.recent_clients.insert(0, client)
        values = self.recent_clients.get(0, tk.END)
        with open(f"{self.login}_recent_clients.txt", "w") as f:
            for i in values:
                f.write(i + "\n")

    def pack_message(self, message):
        """Помещает сообщение в окно чата."""
        if message["sender"] == self.login:
            tk.Label(
                self.chat,
                text=f"{message['sender']} {message['date']}",
                wraplength=450,
                justify=tk.LEFT,
            ).pack(anchor=tk.E)
            tk.Label(
                self.chat,
                text=message["message"],
                wraplength=450,
                bg="#b0ffff",
                justify=tk.LEFT,
            ).pack(anchor=tk.E, pady=5)
        else:
            tk.Label(
                self.chat,
                text=f"{message['sender']} {message['date']}",
                wraplength=450,
                justify=tk.LEFT,
            ).pack(anchor=tk.W)
            tk.Label(
                self.chat,
                text=message["message"],
                wraplength=450,
                bg="#B5B8B1",
                justify=tk.LEFT,
            ).pack(anchor=tk.W, pady=5)
        self.canvas.yview_moveto(1)


class ClientFactory(ClFactory):
    """Класс для создания экземпляров класса Client"""
    def buildProtocol(self, addr):
        """Создает и возвращает экземпляр клиентского класса"""
        return Client()


def handle_error(failure):
    """Обрабатывает ошибку, возникшую при подключении к серверу"""
    messagebox.showerror(message="Ошибка подключения к серверу", title="ERROR")
    reactor.stop()


def main():
    """Основная точка входа в программу
    Создает конечную точку TCP-сервера, подключается к указанному порту и запускает реактор"""
    endpoint = TCP4ClientEndpoint(reactor, "localhost", 8080)  # Тут менять IP
    con = endpoint.connect(ClientFactory())
    con.addErrback(handle_error)
    reactor.run()


if __name__ == "__main__":
    main()
