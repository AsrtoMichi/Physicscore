#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
# Physicscore
This app is aimed at counting points in physic competitions.
The app consists of two windows: one for viewing the scores,
one for entering answers and jolly (only one for team).
It also saves all anser and jolly in a .txt file, to make grafic.
"""

__author__ = "Michele Gallo", "https://github.com/AsrtoMichi"
__suorce_code__ = "https://github.com/AsrtoMichi/Physicscore"
__license__ = "https://raw.githubusercontent.com/AsrtoMichi/Physicscore/main/LICENSE"
__README__ = "https://raw.githubusercontent.com/AsrtoMichi/Physicscore/main/README.md"

__credits__ = """
Alessandro Chiozza, Federico Micelli, Giorgio Sorgente and Gabriele Triso for technical help
"""


from math import sqrt, e
from json import load, dump
from os.path import join, dirname
from sys import exit as sys_exit


from tkinter import Tk, Toplevel, Button, Label, Frame, Entry, Variable, Canvas, Scrollbar
from tkinter.ttk import Combobox
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import askokcancel
from _tkinter import TclError


class Main(Tk):
    def __init__(self):
        super().__init__()

        Label(self, text='Copyright (C) 2024 AsrtoMichi').pack(
            side='bottom', anchor='e', padx=8, pady=8)

        try:
            self.iconbitmap(default=join(dirname(__file__), 'MathScore.ico'))
        except TclError:
            pass

        self.protocol('WM_DELETE_WINDOW', lambda: sys_exit() if askokcancel(
            'Confirm exit', 'Data can be losted.',  master=self) else None)

        self.button1 = Button(self, text='Start competion',
                              command=self.load_data)
        self.button2 = Button(self, text='Draw graphs',
                              command=self.draw_graphs)

        self.button1.pack()
        self.button2.pack()

    # ----------------- Runtime competiton -----------------#

    def load_data(self):

        self.data = load(open(askopenfilename(
            master=self,
            title='Select the .json file',
            filetypes=[('JavaScript Object Notation', '*.json')])))

        self.title(self.data['Name'])

        self.NAMES_TEAMS = self.NAMES_TEAMS_REAL = self.data['Teams']
        self.NAMES_TEAMS += self.data['Teams_ghost']
        self._NUMBER_OF_TEAMS = len(self.NAMES_TEAMS)

        self._timer_seconds, self._TIME_FOR_JOLLY = self.data['Timers']['time'] * \
            60, self.data['Timers']['time_for_jolly'] * 60

        self.questions_data = [
            0] + [[1 / (1 + question[1] / 100), question[0], 1 + question[1] / 100, 0] for question in self.data['Solutions']]
        
        self.NUMBER_OF_QUESTIONS = len(self.data['Solutions'])
        self.NUMBER_OF_QUESTIONS_RANGE_1 = range(
            1, self.NUMBER_OF_QUESTIONS + 1)
        

        self.Bp, self.Dp, self.E, self.A, self.h = self.data['Patameters']['Bp'], self.data['Patameters'][
            'Dp'], self.data['Patameters']['E'], self.data['Patameters']['A'], self.data['Patameters']['h']

        self.teams_data = {name: [self.E * self.NUMBER_OF_QUESTIONS] + [[0] * 4
                                                         for _ in self.NUMBER_OF_QUESTIONS_RANGE_1
                                                         ] for name in self.NAMES_TEAMS}
        
        self._jolly,  self._answer = [], []


        self.button1.config(text='Start', command=self.start_competition)
        self.button2.pack_forget()

        self.timer_label = Label(
            self,
            font=(
                'Helvetica',
                18,
                'bold'),
            text=f'Time left: {self._timer_seconds // 3600:02d}:{(self._timer_seconds % 3600) // 60:02d}:00')
        self.timer_label.pack()

        self.canvas = Canvas(self)
        self.scrollbar = Scrollbar(
            self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        frame = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=frame, anchor='nw')

        self.var_question, colum_range = [None], range(
            2, self.NUMBER_OF_QUESTIONS + 2)

        for col in colum_range:

            Label(frame, width=6, text=col - 1).grid(row=0, column=col)

            question_var = StringVar(self)
            self.var_question.append(question_var)

            Entry(frame, width=6, bd=5,
                  state='readonly', readonlybackground='white',
                  textvariable=question_var
                  ).grid(row=1, column=col)

        self.var_start_row = []
        self.var_question_x_team = []
        self.entry_question_x_team = []

        for row in range(2, len(self.NAMES_TEAMS) + 2):

            team_var, total_points_team_var = StringVar(self), StringVar(self)

            Label(frame, anchor='e',
                  textvariable=team_var
                  ).grid(row=row, column=0)

            Entry(frame, width=6, bd=5,
                  state='readonly', readonlybackground='white',
                  textvariable=total_points_team_var
                  ).grid(row=row, column=1)

            self.var_start_row.append((team_var, total_points_team_var))

            var_list = [None]
            entry_list = [None]

            for col in colum_range:

                points_team_x_question = StringVar(self)

                entry = Entry(frame, width=6, bd=5,
                              state='readonly', readonlybackground='white',
                              textvariable=points_team_x_question
                              )

                entry.grid(row=row, column=col)

                var_list.append(points_team_x_question)
                entry_list.append(entry)

            self.var_question_x_team.append(var_list)
            self.entry_question_x_team.append(entry_list)

        frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox('all'))

        self.update_entry()

    def start_competition(self):

        self.arbiterGUI = ArbiterGUI(self)
        self.arbiterGUI.jolly_button.configure(state='normal')
        self.arbiterGUI.answer_button.configure(state='normal')
        self.arbiterGUI.bind(
            '<Return>', lambda key: self.arbiterGUI.submit_answer())
        self.arbiterGUI.bind(
            '<Shift-Return>', lambda key: self.arbiterGUI.submit_jolly())

        self.button1.pack_forget()
        self.button2.pack_forget()
        self.canvas_scrollbar_pack()

        TOTAL_TIME = self._timer_seconds

        # ------------------- Timer ------------------- #

        for time in range(1000, (TOTAL_TIME * 1000) + 1, 1000):
            self.after(time, self.update_timer)

        # ------------------ Answers ------------------ #

        for answer in self.data['Actions']['answers']:
            if answer[0] in self.data['Teams_ghost']:
                self.after(answer[3]*1000, self.submit_answer, *answer[:3])

        # ------------------- Jolly ------------------- #

        for jolly in self.data['Actions']['jokers']:
            if jolly[0] in self.data['Teams_ghost']:
                self.after(jolly[2]*1000, self.submit_jolly, *jolly[:2])

        self.after(self._TIME_FOR_JOLLY * 1000,
                   self.stop_jolly)

        # ----------------- Hinding points ----------------- #

        self.after((TOTAL_TIME - 30) * 1000, self.canvas_scrollbar_pack_forget)

        # ------------------- Conclusion ------------------- #

        self.after(TOTAL_TIME * 1000, self.conclusion)

    def stop_jolly(self):
        """
        Block the ability to send wildcards
        """
        self.arbiterGUI.jolly_button.configure(state='disabled')
        self.arbiterGUI.unbind('<Shift-Return>')

    def conclusion(self):
        """
        Block the ability to send replies and show the final ranking
        """

        self.button1.pack()
        self.button1.configure(text = 'Show ranking', command = self.show_ranking)
        self.timer_label.destroy()
    
    def show_ranking(self):
        """
        Show the final ranking and configure the main button to save data
        """

        self.button1.configure(
            text='Save data', command=lambda: dump({'Name': self.data['Name'],

            'Teams': [],
            'Teams_ghost': [],

              'Timers': {
            'time': self.data['Timers']['time'],
            'time_for_jolly': self.data['Timers']['time_for_jolly'],
            "time_format": 'use min'
        },

            'Patameters': {
            'Bp': self.data['Patameters']['Bp'],
            'Dp': self.data['Patameters']['Dp'],
            'E': self.data['Patameters']['E'],
            'A': self.data['Patameters']['A'],
            'h': self.data['Patameters']['h']
        },

            'Solutions': self.data['Solutions'],

            'Actions': {
            'teams': self.NAMES_TEAMS,
            'jokers': self._jolly,
            'jolly_format' : ['team', 'question', 'time in seconds'],
            'answers': self._answer,
            'answer_format' : ['team', 'question', 'answer', 'time in seconds']

        }
        }, open(asksaveasfilename(master=self, filetypes=(
            ('JavaScript Object Notation', '*.json')), title='Save date'), 'w')))

        self.button2.pack()
        self.button2.configure(text='Main menù', command=self.main_menù_1)
        self.canvas_scrollbar_pack()

        self.arbiterGUI.destroy()
    
    def main_menù_1(self):
        """
        Come back to Main menù
        """

        self.canvas_scrollbar_pack_forget()
        self.button1.config(text='Start competion',
                              command=self.load_data)
        self.button2.config(text='Draw graphs',
                              command=self.draw_graphs)
    
    # --------------------- Grafic's --------------------- #

    def canvas_scrollbar_pack(self):
        """
        Pack canvas for entryes and scrollbarr
        """

        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', expand=True, fill='both')

    def canvas_scrollbar_pack_forget(self):
        """
        Pack forget canvas for entryes and scrollbarr
        """
        self.scrollbar.pack_forget()
        self.canvas.pack_forget()

    # --------------------- Upadte's --------------------- #

    def update_timer(self):
        """
        Update the clock label
        """

        self._timer_seconds -= 1
        self.timer_label.configure(
            text=f'Time left: {self._timer_seconds // 3600:02d}: {(self._timer_seconds % 3600) // 60:02d}: {self._timer_seconds % 60:02d}')

    def update_entry(self):
        """
        Update values in points
        """

        # Create value labels for each question
        for question in self.NUMBER_OF_QUESTIONS_RANGE_1:

            self.var_question[question].set(
                self.value_question(question))

        # Populate team points and color-code entries
        for row, team in enumerate(sorted(self.NAMES_TEAMS,
                                          key=self.total_points_team,
                                          reverse=True)):

            self.var_start_row[row][0].set(team)

            self.var_start_row[row][1].set(self.total_points_team(team))

            for question in self.NUMBER_OF_QUESTIONS_RANGE_1:

                points, jolly = self.value_question_x_squad(
                    team, question), self.teams_data[team][question][2]

                self.var_question_x_team[row][question].set(
                    f'{points} J' if jolly else
                    points)

                self.entry_question_x_team[row][question].config(
                    readonlybackground='red' if points < 0 else 'green' if points > 0 else 'white',
                    fg='blue' if jolly else 'black',
                    font=f"Helvetica 9 {'bold' if jolly else 'normal'}")

    # --------------------- Submit's --------------------- #

    def submit_answer(self, team: str, question: int, answer: float):
        """
        The mehtod to submit answers
        """


        if team and question and answer and not self.teams_data[team][question][1]:

            data_point_team = self.teams_data[team][question]
            data_question = self.questions_data[question]

            # if correct
            if data_question[0] <= answer / \
                    data_question[1] <= data_question[2]:

                data_question[3] += 1

                data_point_team[1], data_point_team[3] = True, self.g(
                    20, data_question[3], sqrt(4 * self.Act_t()))

                # give bonus
                if [question[1]
                    for question in self.teams_data[team][1:]
                    ].count(True) == self.NUMBER_OF_QUESTIONS:

                    self.questions_data[0] += 1

                    self.teams_data[team][0] += self.g(
                        20 * self.NUMBER_OF_QUESTIONS,
                        self.questions_data[0],
                        sqrt(
                            2 * self.Act_t()))

            # if wrong
            else:
                data_point_team[0] += 1

            self.update_entry()

            self._answer.append([team, question, answer, self._timer_seconds])

    def submit_jolly(self, team: str, question: int):
        """
        The method to submit jolly
        """

        # check if other jolly are already been given
        if team and question and not any(
                question[2] for question in self.teams_data[team][1:]):

            self.teams_data[team][question][2] = True
            
            self._jolly.append([team, question, self._timer_seconds])

            self.update_entry()

    # ---------------- Point's calculation ---------------- #

    def g(self, p, k, m) -> int:

        return int(p * e ** (-4 * (k - 1) / m))

    def Act_t(self) -> int:
        """
        Retun the number of active teams
        """

        return max(self._NUMBER_OF_TEAMS / 2,
                   [any(question[1] for question in self.teams_data[team][1:])
                       for team in self.NAMES_TEAMS].count(True),
                   5)

    def value_question(self, question: int) -> int:
        """
        Return the value of answer
        """

        return self.Bp + self.g(self.Dp + self.A * sum(min(self.h,
                                                           self.teams_data[team][question][0]) for team in self.NAMES_TEAMS) / self.Act_t(),
                                self.questions_data[question][3],
                                self.Act_t())

    def value_question_x_squad(self, team: str, question: int) -> int:
        """
        Return the points made by a team in a question
        """

        list_point_team = self.teams_data[team][question]

        return (
            list_point_team[1] *
            (self.value_question(question) + list_point_team[3])
            - list_point_team[0] * self.E) * (list_point_team[2] + 1)

    def total_points_team(self, team: str) -> int:
        """
        Return the points of a team
        """
        return sum(self.value_question_x_squad(team, question)
                   for question in self.NUMBER_OF_QUESTIONS_RANGE_1
                   ) + self.teams_data[team][0]

    # ---------------------- Grafics ---------------------- #

    def draw_graphs(self):
        pass


class ArbiterGUI(Toplevel):
    """
    The window to submit jolly and answers
    """

    def __init__(self, main: Main):

        super().__init__(main)

        self.submit_jolly_main = main.submit_jolly
        self.submit_answer_main = main.submit_answer

        self.title('Reciver')
        self.geometry('250x290')
        self.resizable(False, False)

        Label(self, text="Team:").pack()
        self.team_var = StringVar(main)
        Combobox(
            self,
            textvariable=self.team_var,
            values=main.NAMES_TEAMS_REAL,
            state='readonly'
        ).pack()

        Label(self, text="Question number:").pack()
        self.question_var = IntVar(main)
        Entry(self, textvariable=self.question_var).pack()

        Label(self, text="Answer:").pack()
        self.answer_var = DoubleVar(main)
        Entry(self, textvariable=self.answer_var).pack()

        self.jolly_button = Button(
            self,
            text="Submit Jolly",
            command=self.submit_jolly,
            state='disabled')
        self.jolly_button.pack(pady=15)
        self.answer_button = Button(
            self,
            text="Submit Answer",
            command=self.submit_answer,
            state='disabled')
        self.answer_button.pack()

        Label(self, text='Copyright (C) 2024 AsrtoMichi').pack(
            side='bottom', anchor="e", padx=8, pady=8)

        self.protocol('WM_DELETE_WINDOW', lambda: None)

    def submit_jolly(self):
        """
        The method associated to the button answer
        """
        self.submit_jolly_main(
            self.team_var.get(),
            self.question_var.get())

        self.clean()

    def submit_answer(self):
        """
        The method associated to the button jolly
        """

        self.submit_answer_main(
            self.team_var.get(),
            self.question_var.get(),
            self.answer_var.get())

        self.clean()

    def clean(self):
        """
        Reset value of entryes
        """
        self.team_var.set()
        self.question_var.set()
        self.answer_var.set()

class StringVar(Variable):
    """Value holder for strings variables."""

    def __init__(self, master: Main):
        """Construct a string variable.

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to "")
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        """
        Variable.__init__(self, master)

    def set(self, value: str = ''):
        """Set the variable to VALUE."""
        self._tk.globalsetvar(self._name, value)

class IntVar(StringVar):
    """Value holder for integer variables."""

    def __init__(self, master: Main):
        """Construct an integer variable.

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to 0)
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        """
        StringVar.__init__(self, master)
        self.NUMBER_OF_QUESTIONS = master.NUMBER_OF_QUESTIONS

    def get(self) -> int:
        """Return the value of the variable as an integer."""
        try:
            value = int(self._tk.globalgetvar(self._name))
            return value if 0 < value <= self.NUMBER_OF_QUESTIONS else None
        except ValueError:
            return None


class DoubleVar(StringVar):
    """Value holder for float variables."""

    def __init__(self, master: Main):
        """Construct a float variable.

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to 0.0)
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        """
        StringVar.__init__(self, master)

    def get(self) -> float:
        """Return the value of the variable as an integer."""
        try:
            return float(self._tk.globalgetvar(self._name))
        except ValueError:
            return None


if __name__ == "__main__":
    Main().mainloop()
