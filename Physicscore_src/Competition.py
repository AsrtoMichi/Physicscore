from math import e, sqrt
from typing import Tuple


class Competition:
    def __init__(
        self,
        data: dict,
        teams: Tuple[str | Tuple[str, int]
                     ]

    ):
        
        def unpack_team_nh(data) -> Tuple[str, int]:
            return (data, 0) if isinstance(data, str) else data

        self.NAMES_TEAMS, self._NUMBER_OF_TEAMS = tuple(
            unpack_team_nh(team_nh)[0] for team_nh in teams), len(teams)
        
        data_solutions: Tuple[int, float] = data['Solutions']

        self.questions_data = {
            question: {
                'min': 1 / (1 + question_data[1] / 100),
                'avg': question_data[0],
                'max': 1 + question_data[1] / 100,
                'ca': 0,
            }
            for question, question_data in enumerate(data_solutions, 1)
        }
        self.fulled = 0
        self.questions_penalized = data['Questions_penalized']

        self.NUMBER_OF_QUESTIONS = len(data_solutions)
        self.NUMBER_OF_QUESTIONS_RANGE_1 = range(
            1, self.NUMBER_OF_QUESTIONS + 1)

        self.Bp: int = data['Patameters']['Bp']
        self.Dp: int = data['Patameters']['Dp']
        self.E: int =  data['Patameters']['E']
        self.A: int = data['Patameters']['A']
        self.h: int = data['Patameters']['h']

        self.teams_data = {
            unpack_team_nh(team_nh)[0]: {
                'bonus': unpack_team_nh(team_nh)[1],
                'jolly': None,
                'active': False,
                **{
                    question: {'err': 0, 'sts': False, 'bonus': 0}
                    for question in self.NUMBER_OF_QUESTIONS_RANGE_1
                },
            }
            for team_nh in teams
        }

    def submit_answer(self, team: str, question: int, answer: float) -> bool:
        """
        The mehtod to submit answers
        """

        if team and question and answer and not self.teams_data[team][question]['sts']:
            data_point_team = self.teams_data[team][question]
            data_question = self.questions_data[question]

            self.teams_data[team]['active'] = True

            # if correct
            if (
                data_question['min']
                <= answer / data_question['avg']
                <= data_question['max']
            ):
                data_question['ca'] += 1

                data_point_team['sts'], data_point_team['bonus'] = True, self.g(
                    20, data_question['ca'], sqrt(4 * self.Act_t())
                )

                # give bonus
                if all(
                    self.teams_data[team][quest]['sts']
                    for quest in self.NUMBER_OF_QUESTIONS_RANGE_1
                ):
                    self.fulled += 1

                    self.teams_data[team]['bonus'] += self.g(
                        20 * self.NUMBER_OF_QUESTIONS,
                        self.fulled,
                        sqrt(2 * self.Act_t()),
                    )

            # if wrong
            else:
                data_point_team['err'] += 1

            return True

    def submit_jolly(self, team: str, question: int) -> bool:
        """
        The method to submit jolly
        """

        # check if other jolly are already been given
        if team and question and not self.teams_data[team]['jolly']:
            self.teams_data[team]['jolly'] = True

            return True

    def g(self, p, k, m) -> int:
        return int(p * e ** (-4 * (k - 1) / m))

    def Act_t(self) -> int:
        """
        Retun the number of active teams
        """

        return max(
            self._NUMBER_OF_TEAMS / 2,
            [self.teams_data[team]['active']
                for team in self.NAMES_TEAMS].count(True),
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
                min(self.h, self.teams_data[team][question]['err'])
                for team in self.NAMES_TEAMS
            )
            / self.Act_t(),
            self.questions_data[question]['ca'],
            self.Act_t(),
        )

    def value_question_x_squad(self, team: str, question: int) -> int:
        """
        Return the points made by a team in a question
        """

        list_point_team = self.teams_data[team][question]

        return (
            list_point_team['sts']
            * (self.value_question(question) + list_point_team['bonus'])
            - list_point_team['err'] * self.E * ((question in self.questions_penalized) +1)
        ) * ((self.teams_data[team]['jolly'] == question) + 1)

    def total_points_team(self, team: str) -> int:
        """
        Return the points of a team
        """
        return (
            sum(
                self.value_question_x_squad(team, question)
                for question in self.NUMBER_OF_QUESTIONS_RANGE_1
            )
            + self.teams_data[team]['bonus']
            + (
                self.E * self.NUMBER_OF_QUESTIONS
                if self.teams_data[team]['active']
                else 0
            )
        )
