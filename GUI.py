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

        self.login_entry = Entry(self.top_frame)
        self.password_entry = Entry(self.top_frame)

        self.registration_window.pack()
        self.top_frame.pack()
        self.bottom_frame.pack()
        Label(self.top_frame, text="Логин: ").grid(row=0, column=0)
        self.login_entry.grid(row=0, column=1)
        Label(self.top_frame, text="Пароль: ").grid(row=1, column=0)
        self.password_entry.grid(row=1, column=1)
        self.registration_button.pack()

    def messenger_widgets(self):
        # def on_resize(event):
        #     self.messenger_window.config(width=event.width, height=event.height)
        #
        # self.root.bind("<Configure>", on_resize)

        self.authorize_window.destroy()
        self.messenger_window = Frame(self.root)
        self.root.title("Мессенджер")
        self.root.geometry("900x500")

        self.choose_client = Frame(self.messenger_window)
        self.chat_frame = Frame(self.messenger_window)
        self.find_client_entry = Entry(self.choose_client, font=("", 20))
        self.find_client_button = Button(self.choose_client, text="Найти", font=("", 10), command=self.find_client_button_command)

        self.recent_clients = Listbox(self.choose_client)
        self.recent_clients.bind("<<ListboxSelect>>", self.select_from_listbox)
        self.recent_clients.yview_scroll(number=1, what="units")

        self.messenger_window.place(relwidth=1, relheight=1)
        self.choose_client.place(relwidth=0.20, relheight=1)
        Label(self.choose_client, text="Поиск пользователя", font=("", 10)).pack()
        self.find_client_entry.pack()
        self.find_client_button.pack()
        Label(self.choose_client, text="Недавние чаты:", font=("", 10)).pack()
        self.recent_clients.pack(fill=BOTH, expand=True)

        self.chat_frame.place(relx=0.20, relwidth=0.80, relheight=1)

    def chat_widgets(self):
        self.another_client = Label(self.chat_frame)
        self.chat = Text(self.chat_frame, state=DISABLED, wrap=WORD)

        self.another_client.pack()
        self.chat.pack()




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
        selected_client = self.recent_clients.curselection()
        self.open_chat_with_client(selected_client)

    def open_chat_with_client(self, selected_client):
        raise NotImplementedError()

