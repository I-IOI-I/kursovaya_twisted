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

    def chat_widgets(self):
        self.chat_window = Frame(self.root)

    '''BUTTON FUNCTIONS'''
    def enter_func(self):
        raise NotImplementedError()

    def registration_func(self):
        self.registration_widgets()

    def new_registration_func(self):
        raise NotImplementedError()
