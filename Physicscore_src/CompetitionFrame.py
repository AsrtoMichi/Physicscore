from json import dump
from tkinter.filedialog import asksaveasfilename
from tkinter import Tk, Toplevel, Entry, Variable, Frame, Label, OptionMenu, Button
from typing import Tuple
from .Var import IntVar, DoubleVar
from .Competition import Competition
from .PointsScrollFrame import PointsScrollFrame


class CompetitionFrame(Frame):
    def __init__(self, master: Tk, data: dict):
        super().__init__(master)

        master.title(data['Name'])

        self.data = data
        self.competition = Competition(
            data,  data['Teams'] + data['Teams_ghost'])
        self._jolly, self._answer = [], []

        self.timer: int = data['Timers']['time'] * 60
        self.timer_label = Label(
            self,
            font=('Helvetica', 18, 'bold'),
            text=f'Time left: {self.timer // 3600:02d}:{(self.timer % 3600) // 60:02d}:00',
        )
        self.timer_label.pack()

        self.points_scroll_frame = PointsScrollFrame(self, self.competition)
        self.points_scroll_frame.pack(fill='both', expand=True)
        self.points_scroll_frame.update_entry()

        self.reciver = Reciver(self)
        self.reciver.jolly_button.configure(state='normal')
        self.reciver.answer_button.configure(state='normal')
        self.reciver.bind('<Return>', lambda key: self.submit_answer())
        self.reciver.bind('<Shift-Return>', lambda key: self.submit_jolly())

        TOTAL_TIME = self.timer

        # ------------------- Timer ------------------- #

        for time in range(1000, (TOTAL_TIME * 1000) + 1, 1000):
            master.after(time, self.update_timer)

        # ------------------ Answers ------------------ #

        for answer in data['Actions']['answers']:
            if answer[0] in data['Teams_ghost']:
                master.after(
                    answer[3] * 1000, self.competition.submit_answer, *answer[:3]
                )
                master.after(
                    answer[3] * 1000+100, self.points_scroll_frame.update_entry
                )

        # ------------------- Jolly ------------------- #

        for jolly in data['Actions']['jokers']:
            if jolly[0] in data['Teams_ghost']:
                master.after(jolly[2] * 1000,
                             self.competition.submit_jolly, *jolly[:2])
                master.after(
                    jolly[2] * 1000+100, self.points_scroll_frame.update_entry
                )

        def stop_jolly():
            """
            Block the ability to send jolly
            """
            self.reciver.jolly_button.destroy()
            self.reciver.unbind('<Shift-Return>')

        master.after(data['Timers']['time_for_jolly'] * 60000, stop_jolly)

        # ----------------- Hinding points ----------------- #

        master.after((TOTAL_TIME - 30) * 1000,
                     self.points_scroll_frame.pack_forget)

        # ------------------- Conclusion ------------------- #

        master.after(TOTAL_TIME * 1000, self.hide_rancking)

    def hide_rancking(self):
        """
        Block the ability to send answer
        """
        self.pack_forget()
        self.master.button1.pack()
        self.master.button1.configure(
            text='Show ranking', command=self.show_ranking)
        self.pack(fill='both', expand=True)
        
        self.timer_label.destroy()
        self.points_scroll_frame.update_entry()

    def show_ranking(self):
        """
        Show the final ranking and configure the button1 button to save data
        """

        self.master.button1.configure(
            text='Save data',
            command=lambda: dump(
                {
                    'Author': 'Michele Gallo',
                    'Template': 'https://raw.githubusercontent.com/AsrtoMichi/Physicscore/main/src/Template.json',
                    'Name': self.data['Name'],
                    'Teams': [],
                    'Teams_ghost': [],
                    'Timers': {
                        'time': self.data['Timers']['time'],
                        'time_for_jolly': self.data['Timers']['time_for_jolly'],
                        'time_format': 'use min',
                    },
                    'Patameters': {
                        'Bp': self.data['Patameters']['Bp'],
                        'Dp': self.data['Patameters']['Dp'],
                        'E': self.data['Patameters']['E'],
                        'A': self.data['Patameters']['A'],
                        'h': self.data['Patameters']['h'],
                    },
                    'Solutions': self.data['Solutions'],
                    'Actions': {
                        'teams': self.competition.NAMES_TEAMS,
                        'jokers': self._jolly,
                        'jolly_format': ['team', 'question', 'time in seconds'],
                        'answers': self._answer,
                        'answer_format': [
                            'team',
                            'question',
                            'answer',
                            'time in seconds',
                        ],
                    },
                },
                open(
                    asksaveasfilename(
                        master=self,
                        defaultextension='.json',
                        filetypes=[('JavaScript Object Notation', '*.json')],
                        title='Save date',
                    ),
                    'w',
                ),
            ),
        )

        self.master.button2.configure(
            text='Main menù', command=self.master.destroy_frame
        )

        self.pack_forget()
        self.master.button2.pack()
        self.pack(fill='both', expand=True)

        self.points_scroll_frame.pack(fill='both', expand=True)
        self.reciver.destroy()

    def update_timer(self):
        """
        Update the clock label
        """

        self.timer -= 1
        self.timer_label.configure(
            text=f'Time left: {self.timer // 3600:02d}: {(self.timer % 3600) // 60:02d}: {self.timer % 60:02d}'
        )

    def submit_answer(self):
        team, question, answer = self.reciver.get()

        if self.competition.submit_answer(team, question, answer):
            self.points_scroll_frame.update_entry()
            self._answer.append((team, question, answer, self.timer))

    def submit_jolly(self):
        team, question, _ = self.reciver.get()

        if self.competition.submit_jolly(team, question):
            self.points_scroll_frame.update_entry()
            self._jolly.append((team, question, self.timer))   


class Reciver(Toplevel):
    def __init__(self, master: CompetitionFrame):

        self.competition = master.competition

        super().__init__(master)
        self.title('Reciver')
        self.geometry('250x290')
        self.resizable(False, False)

        Label(self, text='Team:').pack()
        self.team_var = Variable(self)
        OptionMenu(
            self,
            self.team_var,
            *self.competition.NAMES_TEAMS,
        ).pack()

        Label(self, text='Question number:').pack()
        self.question_var = IntVar(self, self.competition.NUMBER_OF_QUESTIONS)
        Entry(self, textvariable=self.question_var).pack()

        Label(self, text='Answer:').pack()
        self.answer_var = DoubleVar(self)
        Entry(self, textvariable=self.answer_var).pack()

        self.jolly_button = Button(
            self,
            text='Submit Jolly',
            command=master.submit_jolly,
            state='disabled',
        )
        self.jolly_button.pack(pady=15)

        self.answer_button = Button(
            self,
            text='Submit Answer',
            command=master.submit_answer,
            state='disabled',
        )
        self.answer_button.pack()

        self.protocol('WM_DELETE_WINDOW', lambda: None)

    def get(self) -> Tuple[str, int, float]:
        """
        Return values of entryes
        Reset values of entryes
        """
        output = self.team_var.get(), self.question_var.get(), self.answer_var.get()

        self.team_var.set('')
        self.question_var.set('')
        self.answer_var.set('')

        return output
