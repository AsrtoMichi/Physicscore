from json import dump
from tkinter.filedialog import asksaveasfilename
from tkinter import Tk, Toplevel, Entry, Variable, Frame, Label, OptionMenu, Button
from .Var import IntVar, DoubleVar
from .Competition import Competition
from .PointsScrollFrame import PointsScrollFrame

class CompetitionFrame(Frame):
    def __init__(self, master: Tk, data: dict):
        super().__init__(master)

        master.title(data['Name'])

        self.data = data


        self.competition = Competition(
            data['Teams'] + data['Teams_ghost'],
            data['Solutions'],
            data['Patameters']['Bp'],
            data['Patameters']['Dp'],
            data['Patameters']['E'],
            data['Patameters']['A'],
            data['Patameters']['h'],
        )

        self.timer: int = data['Timers']['time'] * 60

        self._jolly, self._answer = [], []

        self.timer_label = Label(
            self,
            font=('Helvetica', 18, 'bold'),
            text=f'Time left: {self.timer // 3600:02d}:{(self.timer % 3600) // 60:02d}:00',
        )

        self.timer_label.pack()

        self.points_scroll_frame = PointsScrollFrame(self, self.competition)
        
        self.arbiterGUI = Toplevel(self)

        self.arbiterGUI.title('Reciver')
        self.arbiterGUI.geometry('250x290')
        self.arbiterGUI.resizable(False, False)

        Label(self.arbiterGUI, text='Team:').pack()
        self.team_var = Variable(self)
        OptionMenu(
            self.arbiterGUI,
            self.team_var,
            *self.competition.NAMES_TEAMS,
        ).pack()

        Label(self.arbiterGUI, text='Question number:').pack()
        self.question_var = IntVar(self, self.competition.NUMBER_OF_QUESTIONS)
        Entry(self.arbiterGUI, textvariable=self.question_var).pack()

        Label(self.arbiterGUI, text='Answer:').pack()
        self.answer_var = DoubleVar(self)
        Entry(self.arbiterGUI, textvariable=self.answer_var).pack()

        self.jolly_button = Button(
            self.arbiterGUI,
            text='Submit Jolly',
            command=self.submit_jolly,
            state='disabled',
        )
        self.jolly_button.pack(pady=15)

        self.answer_button = Button(
            self.arbiterGUI,
            text='Submit Answer',
            command=self.submit_answer,
            state='disabled',
        )
        self.answer_button.pack()

        Label(self.arbiterGUI, text='Copyright (C) 2024 AsrtoMichi').pack(
            side='bottom', anchor='e', padx=8, pady=8
        )

        self.arbiterGUI.protocol('WM_DELETE_WINDOW', lambda: None)

        self.jolly_button.configure(state='normal')
        self.answer_button.configure(state='normal')
        self.arbiterGUI.bind('<Return>', lambda key: self.submit_answer())
        self.arbiterGUI.bind('<Shift-Return>', lambda key: self.submit_jolly())

        self.points_scroll_frame.pack()
        self.points_scroll_frame.update_entry()
        self.clean()

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

        # ------------------- Jolly ------------------- #

        for jolly in data['Actions']['jokers']:
            if jolly[0] in data['Teams_ghost']:
                master.after(jolly[2] * 1000, self.competition.submit_jolly, *jolly[:2])

        def stop_jolly():
            '''
            Block the ability to send jolly
            '''
            self.jolly_button.destroy()
            self.arbiterGUI.unbind('<Shift-Return>')

        master.after(data['Timers']['time_for_jolly'] * 60000, stop_jolly)

        # ----------------- Hinding points ----------------- #

        master.after((TOTAL_TIME - 30) * 1000, self.points_scroll_frame.pack_forget)

        # ------------------- Conclusion ------------------- #

        master.after(TOTAL_TIME * 1000, self.hide_rancking)

    def hide_rancking(self):
        '''
        Block the ability to send answer
        '''
        self.pack_forget()
        self.master.button1.pack()
        self.pack()
        self.master.button1.configure(text='Show ranking', command=self.show_ranking)
        self.timer_label.destroy()

    def show_ranking(self):
        '''
        Show the final ranking and configure the button1 button to save data
        '''

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
        self.pack()

        self.points_scroll_frame.pack()
        self.arbiterGUI.destroy()

    def update_timer(self):
        '''
        Update the clock label
        '''

        self.timer -= 1
        self.timer_label.configure(
            text=f'Time left: {self.timer // 3600:02d}: {(self.timer % 3600) // 60:02d}: {self.timer % 60:02d}'
        )
 
    def submit_answer(self):
        team, question, answer = (
            self.team_var.get(),
            self.question_var.get(),
            self.answer_var.get(),
        )

        if self.competition.submit_answer(team, question, answer):
            self.points_scroll_frame.update_entry()
            self._answer.append((team, question, answer, self.timer))

        self.clean()

    def submit_jolly(self):
        team, question = self.team_var.get(), self.question_var.get()

        if self.competition.submit_jolly(team, question):
            self._jolly.append((team, question, self.timer))

            self.points_scroll_frame.update_entry()

        self.clean()

    def clean(self):
        '''
        Reset value of entryes
        '''
        self.team_var.set('')
        self.question_var.set('')
        self.answer_var.set('')
