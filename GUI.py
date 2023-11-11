from tkinter import *
from tkinter.ttk import Combobox, Scrollbar, Treeview


class Interface:
    
    def run(self):
        self.root = Tk()
        self.authorize_widgets()

    def authorize_widgets(self):
        self.root.geometry("600x400+400+100")
        self.root.title("Авторизация")
        self.authorize_window = Frame(self.root)


        self.top_frame = Frame(self.authorize_window)
        self.bottom_frame = Frame(self.authorize_window)


        self.login_button = Button(self.bottom_frame, text="Войти", font=30, command=self.enter_func)
        self.registration_button = Button(self.bottom_frame, text="Регистрация", font=30, command=self.registration_func)

        self.login_entry = Entry(self.top_frame)
        self.password_entry = Entry(self.top_frame)

        self.authorize_window.pack()
        self.top_frame.pack()
        self.bottom_frame.pack()
        Label(self.top_frame, text="Логин: ").grid(row=0, column=0)
        self.login_entry.grid(row=0, column=1)
        Label(self.top_frame, text="Пароль: ").grid(row=1, column=0)
        self.password_entry.grid(row=1, column=1)
        self.login_button.pack()
        self.registration_button.pack()

    def registration_widgets(self):
        self.authorize_window.destroy()
        self.root.title("Регистрация")
        self.registration_window = Frame(self.root)
        self.top_frame = Frame(self.registration_window)
        self.bottom_frame = Frame(self.registration_window)

        self.registration_button = Button(self.bottom_frame, text="Зарегистрироваться", font=30,
                                          command=self.new_registration_func)

        self.registration_back_button = Button(self.top_frame, text="Назад", font=30,
                                          command=self.registration_back_func)

        self.login_entry = Entry(self.top_frame)
        self.password_entry = Entry(self.top_frame)

        self.registration_window.pack()
        self.top_frame.pack()
        self.bottom_frame.pack()
        self.registration_back_button.grid(row=0, column=0, columnspan=2)
        Label(self.top_frame, text="Логин: ").grid(row=1, column=0)
        self.login_entry.grid(row=1, column=1)
        Label(self.top_frame, text="Пароль: ").grid(row=2, column=0)
        self.password_entry.grid(row=2, column=1)
        self.registration_button.pack()

    def messenger_widgets(self):
        # def on_resize(event):
        #     self.messenger_window.config(width=event.width, height=event.height)
        #
        # self.root.bind("<Configure>", on_resize)
        self.root.bind("<Delete>", self.delete_from_recent_clients)
        self.authorize_window.destroy()
        self.messenger_window = Frame(self.root)
        self.root.title("Мессенджер")
        self.root.geometry("900x500")

        self.choose_client = Frame(self.messenger_window)
        # self.messenger_back_button = Button(self.messenger_window, text="Назад", font=30,
        #                                        command=self.messenger_back_func)
        self.find_client_entry = Entry(self.choose_client, font=("", 20))
        self.find_client_button = Button(self.choose_client, text="Найти", font=("", 10), command=self.find_client_button_command)

        self.recent_clients = Listbox(self.choose_client)
        scrollbar_recent_clients = Scrollbar(self.recent_clients, orient=VERTICAL, command=self.recent_clients.yview)
        scrollbar_recent_clients.pack(side=RIGHT, fill=Y)
        self.recent_clients.config(yscrollcommand=scrollbar_recent_clients.set)
        self.recent_clients.bind("<<ListboxSelect>>", self.select_from_listbox)
        self.recent_clients.yview_scroll(number=1, what="units")



        self.messenger_window.place(relwidth=1, relheight=1)
        self.choose_client.place(relwidth=0.20, relheight=1)
        Label(self.choose_client, text="Поиск пользователя", font=("", 10)).pack()
        self.find_client_entry.pack()
        self.find_client_button.pack()
        Label(self.choose_client, text="Недавние чаты:", font=("", 10)).pack()
        self.recent_clients.pack(fill=BOTH, expand=True)
        # self.messenger_back_button.place(anchor=NE, relx=0.95)

    def chat_widgets(self):
        self.chat_frame = Frame(self.messenger_window)
        self.another_client_label = Label(self.chat_frame, font=("", 10))
        self.chat = Frame(self.chat_frame)
        self.message_enter = Entry(self.chat_frame, font=("", 20), justify=RIGHT)
        self.message_send_button = Button(self.chat_frame, text="Отправить", font=("", 10),
                                          command=self.send_message_button_command)
        self.message_enter.bind('<Return>', self.send_message_button_command)
        self.attach_a_file_button = Button(self.chat_frame, text="Прикрепить\nфайл", font=("", 10),
                                           command=self.attach_a_file_button_command)

        self.chat_frame.place(relx=0.2, relwidth=0.8, relheight=1)
        self.another_client_label.place(relheight=0.1, relx=0.4)
        self.chat.place(relwidth=1, relheight=0.9, rely=0.1)
        self.attach_a_file_button.place(relwidth=0.1, relheight=0.1, rely=0.9)
        self.message_enter.place(relwidth=0.8, relheight=0.1, rely=0.9, relx=0.1)
        self.message_send_button.place(relwidth=0.1, relheight=0.1, rely=0.9, relx=0.9)

    '''BUTTON FUNCTIONS'''
    def enter_func(self):
        raise NotImplementedError()

    def registration_func(self):
        self.registration_widgets()

    def new_registration_func(self):
        raise NotImplementedError()

    def find_client_button_command(self):
        raise NotImplementedError()

    def select_from_listbox(self, event):
        selected_index = self.recent_clients.curselection()
        selected_client = self.recent_clients.get(selected_index)
        self.open_chat_with_client(selected_client)

    def open_chat_with_client(self, selected_client):
        raise NotImplementedError()

    def registration_back_func(self):
        self.registration_window.destroy()
        self.authorize_widgets()

    def send_message_button_command(self, event):
        raise NotImplementedError()

    def attach_a_file_button_command(self):
        raise NotImplementedError()

    def delete_from_recent_clients(self, event):
        raise NotImplementedError()

    # def messenger_back_func(self):
    #     raise NotImplementedError()


