#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
# Physicscore
This app is aimed at counting points in physic competitions.
The app consists of two windows: one for viewing the scores,
one for entering answers and jolly (only one for team).
It also saves all answer and jolly in a .json file, to make grafic.
'''

__author__ = 'Michele Gallo', 'https://github.com/AsrtoMichi'
__suorce_code__ = 'https://github.com/AsrtoMichi/Physicscore'
__license__ = 'https://raw.githubusercontent.com/AsrtoMichi/Physicscore/main/LICENSE'
__README__ = 'https://raw.githubusercontent.com/AsrtoMichi/Physicscore/main/README.md'

__credits__ = '''
Alessandro Chiozza, Federico Micelli, Giorgio Sorgente and Gabriele Trisolino for technical help
'''


from os.path import join, dirname, isdir
from sys import exit as sys_exit


from tkinter import Tk, Button, Label
from tkinter.messagebox import askokcancel


from .GraphsFrame import GraphsFrame
from .CompetitionFrame import CompetitionFrame
from .JsonLoader import json_load


class Main(Tk):
    def __init__(self):
        super().__init__()


        dir_ico = join(dirname(__file__), 'MathScore.ico')
        if isdir(dir_ico):
            self.iconbitmap(default=dir_ico)

        self.protocol(
            'WM_DELETE_WINDOW',
            lambda: sys_exit()
            if askokcancel('Confirm exit', 'Data can be losted.', master=self)
            else None,
        )

        self.button1 = Button(self)
        self.button2 = Button(self)

        self.show_menù()

    def show_menù(self):
        self.button1.config(text='Start competion',
                            command=self.new_competition)
        self.button2.config(text='Draw graphs', command=self.show_graph)

        self.button1.pack_forget()
        self.button2.pack_forget()
        self.button1.pack()
        self.button2.pack()

    def destroy_frame(self):
        self.frame.destroy()
        self.show_menù()

    # ----------------- Runtime competiton -----------------#

    def new_competition(self):
        try:
            self.data = json_load(self)
            self.button1.config(text='Start', command=self.start_competiton)
            self.button2.pack_forget()

        except FileNotFoundError:
            self.show_menù()

    def start_competiton(self):
        self.button1.pack_forget()
        self.frame = CompetitionFrame(self, self.data)
        self.frame.pack()

        del self.data

    def show_graph(self):
        try:
            self.button1.config(text='Menù', command=self.destroy_frame)
            self.button2.pack_forget()
            self.frame = GraphsFrame(self, json_load(self))
            self.frame.pack()
        except FileNotFoundError:
            self.show_menù()


if __name__ == '__main__':
    Main().mainloop()
