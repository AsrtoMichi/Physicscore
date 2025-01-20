from os.path import join, dirname, isfile
from sys import exit as sys_exit, platform
from tkinter import Tk, Button
from tkinter.messagebox import askokcancel, showinfo

from .GraphsFrame import GraphsFrame
from .CompetitionFrame import CompetitionFrame
from .JsonLoader import json_load

class Physicscore(Tk):
    def __init__(self):
        super().__init__()

        Button(self, text="About", command=lambda: showinfo("License", open(join(dirname(dirname(__file__)), "LICENSE"), encoding="utf-8").read(), master=self)).pack(
            side='bottom', anchor='e', padx=8, pady=8
        )

        if platform.startswith('win'):
            dir_ico = join(dirname(dirname(__file__)), 'Resources', 'Physicscore.ico')

            if isfile(dir_ico):
                    self.iconbitmap(default=dir_ico)

        self.protocol(
            'WM_DELETE_WINDOW',
            lambda: sys_exit()
            if askokcancel("Confirm exit", "Data can be losted.", master=self)
            else None,
        )

        self.button1 = Button(self)
        self.button2 = Button(self)

        self.show_menù()

    def show_menù(self):
        self.button1.config(text="Start competion",
                            command=self.new_competition)
        self.button2.config(text="Draw graphs", command=self.show_graph)

        self.button1.pack_forget()
        self.button2.pack_forget()
        self.button1.pack()
        self.button2.pack()

    def destroy_frame(self):
        self.frame.destroy()
        self.show_menù()

    def new_competition(self):
        try:
            self.data = json_load(self)
            self.button1.config(text="Start", command=self.start_competiton)
            self.button2.pack_forget()

        except (FileNotFoundError, TypeError):
            self.show_menù()

    def start_competiton(self):
        self.button1.pack_forget()
        self.frame = CompetitionFrame(self, self.data)
        self.frame.pack(fill='both', expand=True)

        del self.data

    def show_graph(self):
        try:
            self.button1.config(text="Menù", command=self.destroy_frame)
            self.button2.pack_forget()
            self.frame = GraphsFrame(self, json_load(self))
            self.frame.pack()
        except (FileNotFoundError, TypeError):
            self.show_menù()

