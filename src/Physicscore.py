#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
# Physicscore
This app is aimed at counting points in physic competitions.
The app consists of two windows: one for viewing the scores,
one for entering answers and jolly (only one for team).
It also saves all answer and jolly in a .json file, to make grafic.
"""

__author__ = "Michele Gallo", "https://github.com/AsrtoMichi"
__suorce_code__ = "https://github.com/AsrtoMichi/Physicscore"
__license__ = "https://raw.githubusercontent.com/AsrtoMichi/Physicscore/main/LICENSE"
__README__ = "https://raw.githubusercontent.com/AsrtoMichi/Physicscore/main/README.md"

__credits__ = """
Alessandro Chiozza, Federico Micelli, Giorgio Sorgente and Gabriele Trisolino for technical help
"""

from random import randrange
from math import sqrt, e, log10, ceil
from json import load, dump
from os.path import join, dirname, isdir
from sys import exit as sys_exit
from typing import Tuple, Dict, List

from tkinter import Tk, Toplevel, Canvas, Entry, Variable, BooleanVar, Checkbutton
from tkinter.ttk import Button, Label, Frame, Scrollbar, OptionMenu
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import askokcancel


class Main(Tk):
    def __init__(self):
        super().__init__()

        Label(self, text="v0.1.0.0\nCopyright (C) 2024 AsrtoMichi", justify='right').pack(
            side="bottom", anchor="e", padx=8, pady=8
        )


        dir_ico = join(dirname(__file__), "MathScore.ico")
        if isdir(dir_ico):
            self.iconbitmap(default=join(dirname(__file__), "MathScore.ico"))

        self.protocol(
            "WM_DELETE_WINDOW",
            lambda: sys_exit()
            if askokcancel("Confirm exit", "Data can be losted.", master=self)
            else None,
        )

        self.button1 = Button(self)
        self.button2 = Button(self)

        self.show_menù()

    def show_menù(self):
        self.button1.config(text="Start competion", command=self.new_competition)
        self.button2.config(text="Draw graphs", command=self.show_graph)

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
            self.data = load_data(self)
            self.button1.config(text="Start", command=self.start_competiton)
            self.button2.pack_forget()

        except FileNotFoundError:
            self.show_menù()

    def start_competiton(self):
        self.button1.pack_forget()
        self.frame = Competition_Frame(self, self.data)
        self.frame.pack()

        del self.data

    def show_graph(self):
        try:
            self.button1.config(text="Menù", command=self.destroy_frame)
            self.button2.pack_forget()
            self.frame = Graphs_Frame(self, load_data(self))
            self.frame.pack()
        except FileNotFoundError:
            self.show_menù()


class Competition_Frame(Frame):
    def __init__(self, master: Tk, data: dict):
        super().__init__(master)

        master.title(data["Name"])

        self.data = data

        self.competition = Competition(
            data["Teams"] + data["Teams_ghost"],
            data["Solutions"],
            data["Patameters"]["Bp"],
            data["Patameters"]["Dp"],
            data["Patameters"]["E"],
            data["Patameters"]["A"],
            data["Patameters"]["h"],
        )

        self.timer: int = data["Timers"]["time"] * 60

        self._jolly, self._answer = [], []

        self.timer_label = Label(
            self,
            font=("Helvetica", 18, "bold"),
            text=f"Time left: {self.timer // 3600:02d}:{(self.timer % 3600) // 60:02d}:00",
        )
        self.timer_label.pack()

        self.points_scroll_frame = ScrollableFrame(self)

        self.var_question, colum_range = [None], range(2, len(data["Solutions"]) + 2)

        for col in colum_range:
            Label(
                self.points_scroll_frame.scrollable_frame, width=6, text=col - 1
            ).grid(row=0, column=col)

            question_var = Variable(self)
            self.var_question.append(question_var)

            Entry(
                self.points_scroll_frame.scrollable_frame,
                width=6,
                bd=5,
                state="readonly",
                readonlybackground="white",
                textvariable=question_var,
            ).grid(row=1, column=col)

        self.var_start_row = []
        self.var_questiox_a_n_team = []
        self.entry_questiox_a_n_team = []

        for row in range(2, len(self.competition.NAMES_TEAMS) + 2):
            team_var, total_points_team_var = Variable(self), Variable(self)

            Label(
                self.points_scroll_frame.scrollable_frame,
                anchor="e",
                textvariable=team_var,
            ).grid(row=row, column=0)

            Entry(
                self.points_scroll_frame.scrollable_frame,
                width=6,
                bd=5,
                state="readonly",
                readonlybackground="white",
                textvariable=total_points_team_var,
            ).grid(row=row, column=1)

            self.var_start_row.append((team_var, total_points_team_var))

            var_list = [None]
            entry_list = [None]

            for col in colum_range:
                points_team_x_question = Variable(self)

                entry = Entry(
                    self.points_scroll_frame.scrollable_frame,
                    width=6,
                    bd=5,
                    state="readonly",
                    readonlybackground="white",
                    textvariable=points_team_x_question,
                )

                entry.grid(row=row, column=col)

                var_list.append(points_team_x_question)
                entry_list.append(entry)

            self.var_questiox_a_n_team.append(var_list)
            self.entry_questiox_a_n_team.append(entry_list)

        self.arbiterGUI = Toplevel(self)

        self.arbiterGUI.title("Reciver")
        self.arbiterGUI.geometry("250x290")
        self.arbiterGUI.resizable(False, False)

        Label(self.arbiterGUI, text="Team:").pack()
        self.team_var = Variable(self)
        OptionMenu(
            self.arbiterGUI,
            self.team_var,
            *self.competition.NAMES_TEAMS,
        ).pack()

        Label(self.arbiterGUI, text="Question number:").pack()
        self.question_var = IntVar(self, self.competition.NUMBER_OF_QUESTIONS)
        Entry(self.arbiterGUI, textvariable=self.question_var).pack()

        Label(self.arbiterGUI, text="Answer:").pack()
        self.answer_var = DoubleVar(self)
        Entry(self.arbiterGUI, textvariable=self.answer_var).pack()

        self.jolly_button = Button(
            self.arbiterGUI,
            text="Submit Jolly",
            command=self.submit_jolly,
            state="disabled",
        )
        self.jolly_button.pack(pady=15)

        self.answer_button = Button(
            self.arbiterGUI,
            text="Submit Answer",
            command=self.submit_answer,
            state="disabled",
        )
        self.answer_button.pack()

        Label(self.arbiterGUI, text="Copyright (C) 2024 AsrtoMichi").pack(
            side="bottom", anchor="e", padx=8, pady=8
        )

        self.arbiterGUI.protocol("WM_DELETE_WINDOW", lambda: None)

        self.jolly_button.configure(state="normal")
        self.answer_button.configure(state="normal")
        self.arbiterGUI.bind("<Return>", lambda key: self.submit_answer())
        self.arbiterGUI.bind("<Shift-Return>", lambda key: self.submit_jolly())

        self.points_scroll_frame.pack()
        self.update_entry()
        self.clean()

        TOTAL_TIME = self.timer

        # ------------------- Timer ------------------- #

        for time in range(1000, (TOTAL_TIME * 1000) + 1, 1000):
            master.after(time, self.update_timer)

        # ------------------ Answers ------------------ #

        for answer in data["Actions"]["answers"]:
            if answer[0] in data["Teams_ghost"]:
                master.after(
                    answer[3] * 1000, self.competition.submit_answer, *answer[:3]
                )

        # ------------------- Jolly ------------------- #

        for jolly in data["Actions"]["jokers"]:
            if jolly[0] in data["Teams_ghost"]:
                master.after(jolly[2] * 1000, self.competition.submit_jolly, *jolly[:2])

        def stop_jolly():
            """
            Block the ability to send jolly
            """
            self.jolly_button.destroy()
            self.arbiterGUI.unbind("<Shift-Return>")

        master.after(data["Timers"]["time_for_jolly"] * 60000, stop_jolly)

        # ----------------- Hinding points ----------------- #

        master.after((TOTAL_TIME - 30) * 1000, self.points_scroll_frame.pack_forget)

        # ------------------- Conclusion ------------------- #

        master.after(TOTAL_TIME * 1000, self.hide_rancking)

    def hide_rancking(self):
        """
        Block the ability to send answer
        """
        self.pack_forget()
        self.master.button1.pack()
        self.pack()
        self.master.button1.configure(text="Show ranking", command=self.show_ranking)
        self.timer_label.destroy()

    def show_ranking(self):
        """
        Show the final ranking and configure the button1 button to save data
        """

        self.master.button1.configure(
            text="Save data",
            command=lambda: dump(
                {
                    "Author": "Michele Gallo",
                    "Template": "https://raw.githubusercontent.com/AsrtoMichi/Physicscore/main/src/Template.json",
                    "Name": self.data["Name"],
                    "Teams": [],
                    "Teams_ghost": [],
                    "Timers": {
                        "time": self.data["Timers"]["time"],
                        "time_for_jolly": self.data["Timers"]["time_for_jolly"],
                        "time_format": "use min",
                    },
                    "Patameters": {
                        "Bp": self.data["Patameters"]["Bp"],
                        "Dp": self.data["Patameters"]["Dp"],
                        "E": self.data["Patameters"]["E"],
                        "A": self.data["Patameters"]["A"],
                        "h": self.data["Patameters"]["h"],
                    },
                    "Solutions": self.data["Solutions"],
                    "Actions": {
                        "teams": self.competition.NAMES_TEAMS,
                        "jokers": self._jolly,
                        "jolly_format": ["team", "question", "time in seconds"],
                        "answers": self._answer,
                        "answer_format": [
                            "team",
                            "question",
                            "answer",
                            "time in seconds",
                        ],
                    },
                },
                open(
                    asksaveasfilename(
                        master=self,
                        filetypes=[("JavaScript Object Notation", "*.json")],
                        title="Save date",
                    ),
                    "w",
                ),
            ),
        )

        self.master.button2.configure(
            text="Main menù", command=self.master.destroy_frame
        )
        self.pack_forget()
        self.master.button2.pack()
        self.pack()

        self.points_scroll_frame.pack()
        self.arbiterGUI.destroy()

    def update_timer(self):
        """
        Update the clock label
        """

        self.timer -= 1
        self.timer_label.configure(
            text=f"Time left: {self.timer // 3600:02d}: {(self.timer % 3600) // 60:02d}: {self.timer % 60:02d}"
        )

    def update_entry(self):
        """
        Update values in points
        """

        # Create value labels for each question
        for question in self.competition.NUMBER_OF_QUESTIONS_RANGE_1:
            self.var_question[question].set(self.competition.value_question(question))

        # Populate team points and color-code entries
        for row, team in enumerate(
            sorted(
                self.competition.NAMES_TEAMS,
                key=self.competition.total_points_team,
                reverse=True,
            )
        ):
            self.var_start_row[row][0].set(team)

            self.var_start_row[row][1].set(self.competition.total_points_team(team))

            for question in self.competition.NUMBER_OF_QUESTIONS_RANGE_1:
                points, jolly = (
                    self.competition.value_question_x_squad(team, question),
                    self.competition.teams_data[team]["jolly"] == question,
                )

                self.var_questiox_a_n_team[row][question].set(
                    f"{points} J" if jolly else points
                )

                self.entry_questiox_a_n_team[row][question].config(
                    readonlybackground="red"
                    if points < 0
                    else "green"
                    if points > 0
                    else "white",
                    fg="blue" if jolly else "black",
                    font=f"Helvetica 9 {'bold' if jolly else 'normal'}",
                )

    def submit_answer(self):
        team, question, answer = (
            self.team_var.get(),
            self.question_var.get(),
            self.answer_var.get(),
        )

        if self.competition.submit_answer(team, question, answer):
            self.update_entry()
            self._answer.append((team, question, answer, self.timer))

        self.clean()

    def submit_jolly(self):
        team, question = self.team_var.get(), self.question_var.get()

        if self.competition.submit_jolly(team, question):
            self._jolly.append((team, question, self.timer))

            self.update_entry()

        self.clean()

    def clean(self):
        """
        Reset value of entryes
        """
        self.team_var.set("")
        self.question_var.set("")
        self.answer_var.set("")


class Graphs_Frame(Frame):
    def __init__(self, master: Tk, data: dict):
        super().__init__(master)

        master.title(data["Name"])

        competition = Competition(
            data["Actions"]["teams"],
            data["Solutions"],
            data["Patameters"]["Bp"],
            data["Patameters"]["Dp"],
            data["Patameters"]["E"],
            data["Patameters"]["A"],
            data["Patameters"]["h"],
        )

        TOTAL_TIME = data["Timers"]["time"] * 60

        data_teams = {team: [] for team in competition.NAMES_TEAMS}
        data_question = {
            question: [] for question in competition.NUMBER_OF_QUESTIONS_RANGE_1
        }

        def register_data():
            for team in competition.NAMES_TEAMS:
                data_teams[team].append((timer, competition.total_points_team(team)))

            for question in competition.NUMBER_OF_QUESTIONS_RANGE_1:
                data_question[question].append(
                    (timer, competition.value_question(question))
                )

        timer = TOTAL_TIME
        register_data()

        for action in sorted(
            data["Actions"]["answers"] + data["Actions"]["jokers"],
            key=lambda x: x[-1],
            reverse=True,
        ):
            timer = action[-1]
            competition.submit_jolly(*action[:2]) if len(
                action
            ) == 3 else competition.submit_answer(*action[:3])
            register_data()

        timer = 0
        register_data()

        Graph_Frame(self, data_teams, TOTAL_TIME).pack()
        Graph_Frame(self, data_question, TOTAL_TIME).pack(padx=20)


class Graph_Frame(Frame):
    def __init__(
        self,
        master: Frame,
        data: Dict[int | str, List[Tuple[int, int, int, int]]],
        max_x: int,
    ):
        super().__init__(master)

        height = 400
        width_canvas = 700
        width_frame = 300

        keys = data.keys()

        # Create the canvas for the teams graph
        canvas = Canvas(self, width=width_canvas, height=height, bg="white")
        canvas.grid(column=0, row=0)

        scroll_frame = ScrollableFrame(self, width=width_frame, height=height)
        scroll_frame.grid(column=1, row=0)
        Label(scroll_frame.scrollable_frame, text="Show/Hide Teams").pack()

        # Create checkboxes for each team
        vars = {key: BooleanVar(self) for key in keys}
        colors_iterable = iter(
            [
                "red",
                "green",
                "blue",
                "orange",
                "purple",
                "pink",
                "brown",
                "black",
                "white",
                "gray",
                "cyan",
                "magenta",
                "lime",
                "indigo",
                "violet",
                "gold",
                "silver",
                "yellow",
                "maroon",
                "navy",
                "teal",
                "lavender",
                "olive",
                "coral",
                "turquoise",
                "salmon",
                "plum",
                "orchid",
                "chocolate",
                "ivory",
                "beige",
                "mint",
                "peach",
                "amber",
            ]
        )
        colors = {
            key: next(
                colors_iterable,
                f"#{randrange(256):02x}{randrange(256):02x}{randrange(256):02x}",
            )
            for key in keys
        }

        def update_graph():
            # Draw lines for each team if the checkbox is selected
            for key in keys:
                for element in canvas.find_withtag(f"tag_{key}"):
                    canvas.itemconfigure(
                        element, state="normal" if vars[key].get() else "hidden"
                    )

        for key in keys:
            Checkbutton(
                scroll_frame.scrollable_frame,
                text=key,
                variable=vars[key],
                fg=colors[key],
                command=update_graph,
            ).pack(anchor="w")

        def max_axis(max: int) -> int:
            fact = 10 ** int(log10(max))
            return int(ceil(max / fact) * fact)

        # cordinate O
        x_o = 70
        y_o = height - 50

        # axis lenght
        x_a_l = width_canvas - 100
        y_a_l = height - 80

        # number of indicator
        x_a_i_n = 10
        y_a_i_n = 10

        # max value of each axis
        max_a_x = max_axis(max_x)
        max_a_y = max_axis(
            max(line[-1] for data_set in data.values() for line in data_set)
        )

        # distance between indicator
        x_a_i_d = x_a_l / x_a_i_n
        y_a_i_d = y_a_l / y_a_i_n

        # interval betwen indicator
        x_a_d_i = max_a_x / x_a_i_n
        y_a_d_i = max_a_y / y_a_i_n

        # unit on the axis
        u_x_a = x_a_l / max_a_x
        u_y_a = y_a_l / max_a_y

        # Draw the x and y axes
        canvas.create_line(x_o, y_o, x_o + x_a_l, y_o, arrow="last", tags="x-axis")
        canvas.create_line(x_o, y_o, x_o, y_o - y_a_l, arrow="last", tags="y-axis")

        # Label the axes
        canvas.create_text(
            x_o + x_a_l / 2, canvas.winfo_reqheight() - 15, text="Time", tags="time"
        )
        canvas.create_text(15, y_o - y_a_l / 2, text="Value", angle=90, tags="value")

        # Add grid lines and labels
        for i in range(1, x_a_i_n + 1):
            x = x_o + i * x_a_i_d
            canvas.create_line(x, y_o, x, y_o - y_a_i_d * y_a_i_n, dash=(2, 2))
            canvas.create_text(x, y_o + 10, text=str((max_x - i * x_a_d_i) / 60))
        canvas.create_text(x_o, y_o + 10, text=str(max_x / 60))

        for i in range(1, y_a_i_n + 1):
            y = y_o - i * y_a_i_d
            canvas.create_line(x_o, y, x_o + x_a_i_n * x_a_i_d, y, dash=(2, 2))
            canvas.create_text(x_o - 25, y, text=str(i * y_a_d_i))

        for tag, points in data.items():
            line_tag = f"tag_{tag}"
            color = colors[tag]
            for point_index in range(len(points) - 1):
                y1_2_coord = y_o - points[point_index][1] * u_y_a
                x2_3_coord = (max_x - points[point_index + 1][0]) * u_x_a + x_o
                canvas.create_line(
                    ((max_x - points[point_index][0]) * u_x_a + x_o, y1_2_coord),
                    (x2_3_coord, y1_2_coord),
                    tags=line_tag,
                    width=2,
                    fill=color,
                )
                canvas.create_line(
                    (x2_3_coord, y1_2_coord),
                    (x2_3_coord, y_o - points[point_index + 1][1] * u_y_a),
                    tags=line_tag,
                    width=2,
                    fill=color,
                )

        update_graph()


class Competition:
    def __init__(
        self,
        teams: Tuple[str | Tuple[str, int]],
        questions_data: Tuple[Tuple[float, float]],
        Bp: int,
        Dp: int,
        E: int,
        A: int,
        h: int,
    ):
        def unpack_team_nh(data):
            return data, 0 if isinstance(data, str) else data

        self.NAMES_TEAMS, self._NUMBER_OF_TEAMS = tuple(unpack_team_nh(team_nh)[0] for team_nh in teams), len(teams)

        self.questions_data = {
            question: {
                "min": 1 / (1 + question_data[1] / 100),
                "avg": question_data[0],
                "max": 1 + question_data[1] / 100,
                "ca": 0,
            }
            for question, question_data in enumerate(questions_data, 1)
        }
        self.fulled = 0

        self.NUMBER_OF_QUESTIONS = len(questions_data)
        self.NUMBER_OF_QUESTIONS_RANGE_1 = range(1, self.NUMBER_OF_QUESTIONS + 1)

        self.Bp, self.Dp, self.E, self.A, self.h = Bp, Dp, E, A, h            

        self.teams_data = {
            unpack_team_nh(team_nh)[0]: {
                "bonus": unpack_team_nh(team_nh)[1],
                "jolly": None,
                "active": False,
                **{
                    question: {"err": 0, "sts": False, "bonus": 0}
                    for question in self.NUMBER_OF_QUESTIONS_RANGE_1
                },
            }
            for team_nh in teams
        }

    def submit_answer(self, team: str, question: int, answer: float) -> bool:
        """
        The mehtod to submit answers
        """

        if team and question and answer and not self.teams_data[team][question]["sts"]:
            data_point_team = self.teams_data[team][question]
            data_question = self.questions_data[question]

            self.teams_data[team]["active"] = True

            # if correct
            if (
                data_question["min"]
                <= answer / data_question["avg"]
                <= data_question["max"]
            ):
                data_question["ca"] += 1

                data_point_team["sts"], data_point_team["bonus"] = True, self.g(
                    20, data_question["ca"], sqrt(4 * self.Act_t())
                )

                # give bonus
                if all(
                    self.teams_data[team][quest]["sts"]
                    for quest in self.NUMBER_OF_QUESTIONS_RANGE_1
                ):
                    self.fulled += 1

                    self.teams_data[team]["bonus"] += self.g(
                        20 * self.NUMBER_OF_QUESTIONS,
                        self.fulled,
                        sqrt(2 * self.Act_t()),
                    )

            # if wrong
            else:
                data_point_team["err"] += 1

            return True

    def submit_jolly(self, team: str, question: int) -> bool:
        """
        The method to submit jolly
        """

        # check if other jolly are already been given
        if team and question and not self.teams_data[team]["jolly"]:
            self.teams_data[team]["jolly"] = True

            return True

    def g(self, p, k, m) -> int:
        return int(p * e ** (-4 * (k - 1) / m))

    def Act_t(self) -> int:
        """
        Retun the number of active teams
        """

        return max(
            self._NUMBER_OF_TEAMS / 2,
            [self.teams_data[team]["active"] for team in self.NAMES_TEAMS].count(True),
            5,
        )

    def value_question(self, question: int) -> int:
        """
        Return the value of answer
        """

        return self.Bp + self.g(
            self.Dp
            + self.A
            * sum(
                min(self.h, self.teams_data[team][question]["err"])
                for team in self.NAMES_TEAMS
            )
            / self.Act_t(),
            self.questions_data[question]["ca"],
            self.Act_t(),
        )

    def value_question_x_squad(self, team: str, question: int) -> int:
        """
        Return the points made by a team in a question
        """

        list_point_team = self.teams_data[team][question]

        return (
            list_point_team["sts"]
            * (self.value_question(question) + list_point_team["bonus"])
            - list_point_team["err"] * self.E
        ) * ((self.teams_data[team]["jolly"] == question) + 1)

    def total_points_team(self, team: str) -> int:
        """
        Return the points of a team
        """
        return (
            sum(
                self.value_question_x_squad(team, question)
                for question in self.NUMBER_OF_QUESTIONS_RANGE_1
            )
            + self.teams_data[team]["bonus"]
            + (
                self.E * self.NUMBER_OF_QUESTIONS
                if self.teams_data[team]["active"]
                else 0
            )
        )


class IntVar(Variable):
    """Value holder for integer variables."""

    def __init__(self, master: Main, n_question: int):
        """Construct an integer variable.

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to 0)
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        """
        Variable.__init__(self, master)
        self.n_question = n_question

    def get(self) -> int:
        """Return the value of the variable as an integer."""
        try:
            value = int(self._tk.globalgetvar(self._name))
            return value if 0 < value <= self.n_question else None
        except ValueError:
            return None


class DoubleVar(Variable):
    """Value holder for float variables."""

    def __init__(self, master: Main):
        """Construct a float variable.

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to 0.0)
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        """
        Variable.__init__(self, master)

    def get(self) -> float:
        """Return the value of the variable as an integer."""
        try:
            return float(self._tk.globalgetvar(self._name))
        except ValueError:
            return None


class ScrollableFrame(Frame):
    def __init__(self, container, **kwargs):
        super().__init__(container, **kwargs)
        canvas = Canvas(self, **kwargs)
        scrollbar = Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = Frame(canvas, **kwargs)

        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


def load_data(master: Tk):
    return load(
        open(
            askopenfilename(
                master=master,
                title="Select the .json file",
                filetypes=[("JavaScript Object Notation", "*.json")],
            )
        )
    )


if __name__ == "__main__":
    Main().mainloop()
