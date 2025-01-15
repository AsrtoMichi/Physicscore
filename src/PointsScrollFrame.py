from tkinter import Label, Variable, Entry
from .Competition import Competition
from .ScrollableFrame import ScrollableFrame
from .CompetitionFrame import Competition_Frame


class PointsScrollFrame(ScrollableFrame):

    def __init__(self, master: Competition_Frame, competition: Competition):

        super().__init__(master)

        self.competition = competition

        self.var_question, colum_range = [None], range(2, len(self.competition.questions_data) + 2)

        for col in colum_range:
            Label(
                self.scrollable_frame, width=6, text=col - 1
            ).grid(row=0, column=col)

            question_var = Variable(self)
            self.var_question.append(question_var)

            Entry(
                self.scrollable_frame,
                width=6,
                bd=5,
                state='readonly',
                readonlybackground='white',
                textvariable=question_var,
            ).grid(row=1, column=col)

        self.var_start_row = []
        self.var_questiox_a_n_team = []
        self.entry_questiox_a_n_team = []

        for row in range(2, len(self.competition.teams_data) + 2):
            team_var, total_points_team_var = Variable(self), Variable(self)

            Label(
                self.scrollable_frame,
                anchor='e',
                textvariable=team_var,
            ).grid(row=row, column=0)

            Entry(
                self.scrollable_frame,
                width=6,
                bd=5,
                state='readonly',
                readonlybackground='white',
                textvariable=total_points_team_var,
            ).grid(row=row, column=1)

            self.var_start_row.append((team_var, total_points_team_var))

            var_list = [None]
            entry_list = [None]

            for col in colum_range:
                points_team_x_question = Variable(self)

                entry = Entry(
                    self.scrollable_frame,
                    width=6,
                    bd=5,
                    state='readonly',
                    readonlybackground='white',
                    textvariable=points_team_x_question,
                )

                entry.grid(row=row, column=col)

                var_list.append(points_team_x_question)
                entry_list.append(entry)

            self.var_questiox_a_n_team.append(var_list)
            self.entry_questiox_a_n_team.append(entry_list)

    def update_entry(self):
        '''
        Update values in points
        '''

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
                    self.competition.teams_data[team]['jolly'] == question,
                )

                self.var_questiox_a_n_team[row][question].set(
                    f'{points} J' if jolly else points
                )

                self.entry_questiox_a_n_team[row][question].config(
                    readonlybackground='red'
                    if points < 0
                    else 'green'
                    if points > 0
                    else 'white',
                    fg='blue' if jolly else 'black',
                    font=f"Helvetica 9 {'bold' if jolly else 'normal'}",
                )
