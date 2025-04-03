from math import e, sqrt
from typing import Tuple, Iterable
from tkinter.messagebox import showerror

class Competition:
    """
    A class to simulate and manage a team-based physics competition.
    
    Attributes:
    data: dict
        Dictionary containing the competition data and solutions.
    teams: Tuple[str | Tuple[str, int]]
        Tuple containing the names of the teams or tuples of team names with their respective handicaps.
    """

    def __init__(self, data: dict, teams: Tuple[str | Tuple[str, int]]):
        """
        Initializes the Competition class with data and teams.
        
        Parameters:
        data (dict): Dictionary containing competition data and solutions.
        teams (Tuple[str | Tuple[str, int]]): Tuple of team names or tuples of team names with handicaps.
        """
        
        def unpack_data(data: str | Tuple[str, int]) -> Tuple[str, int]:
            """
            Unpacks team name and handicap.

            Parameters:
            data: str or Tuple[str, int]
                Team data which can be a string (team name) or a tuple (team name, handicap).
                
            Returns:
            Tuple[str, int]: Unpacked team name and handicap.
            """

            if isinstance(data, str):
                return (data, 0)
            elif isinstance(data, Iterable) and len(data) == 2 and isinstance(data[0], str) and isinstance(data[1], int):
                return data
            else:
                showerror("Invalid Teams Format", f"The team's data: '{data}' is in an invalid format.", detail="Error code: 221")
                raise RuntimeError


        def delete_duplicate(data: Tuple[str | Tuple[str, int]]) -> Tuple[Tuple[str, int]]:
            """
            Removes duplicate team names and ensures consistent handicap values.

            Parameters:
            data: Tuple[str | Tuple[str, int]]
                List of team data, which can contain both strings and tuples.

            Returns:
            Tuple[Tuple[str, int]]: Cleaned list of unique team names with consistent handicap values.
            """

            result = []

            for team, handicap in map(unpack_data, data):
                if any(sublist[0] == team for sublist in result):
                    if any(sublist[1] != handicap for sublist in result if sublist[0] == team):
                        showerror("Bad Duplicated Teams", f"The team '{team}' appears twice with different handicaps.", detail="Error code: 222")
                        raise RuntimeWarning 
                else:
                    result.append((team, handicap))

            return result


        teams = delete_duplicate(teams)
        self.NAMES_TEAMS, self._NUMBER_OF_TEAMS = tuple([team[0] for team in teams]), len(teams)
        if self._NUMBER_OF_TEAMS == 0:
            showerror("Insufficient Teams", "There are no teams.", detail="Error code: 223")
            raise RuntimeWarning
            
        try:
            self.questions_data = {
                question: {
                    'min': 1 / (1 + question_data[1] / 100),
                    'avg': question_data[0],
                    'max': 1 + question_data[1] / 100,
                    'ca': 0,
                }
                for question, question_data in enumerate(data['Solutions'], 1)
            }
            self.fulled = 0

            self.NUMBER_OF_QUESTIONS = len(self.questions_data)
            self.NUMBER_OF_QUESTIONS_RANGE_1 = range(1, self.NUMBER_OF_QUESTIONS + 1)
            
            self.Bp: int = data['Parameters']['Bp']
            self.Dp: int = data['Parameters']['Dp']
            self.E: int = data['Parameters']['E']
            self.A: int = data['Parameters']['A']
            self.h: int = data['Parameters']['h']
            
            self.teams_data = {
                team[0]: {
                    'bonus': team[1],
                    'jolly': None,
                    'active': False,
                    **{
                        question: {'err': 0, 'sts': False, 'bonus': 0}
                        for question in self.NUMBER_OF_QUESTIONS_RANGE_1
                    },
                }
                for team in teams
            }
            
        except KeyError as e:
            showerror("Missign Data", "Some data are missing in the JSON", detail=f"{e}{chr(10)}Error code: 224")
            raise RuntimeWarning
        except ValueError as e:
            showerror("Bad Data", "Some data are invalid", detail=f"{e}{chr(10)}Error code: 225")
            raise RuntimeWarning            

    def submit_answer(self, team: str, question: int, answer: float) -> bool:
        """
        Submits an answer for a team to a specific question.
        
        Parameters:
        team (str): The name of the team submitting the answer.
        question (int): The number of the question being answered.
        answer (float): The answer provided by the team.
        
        Returns:
        bool: True if the answer was successfully submitted, otherwise False.
        """
        if team and question and (answer is not None) and not self.teams_data[team][question]['sts']:
            data_point_team = self.teams_data[team][question]
            data_question = self.questions_data[question]

            self.teams_data[team]['active'] = True

            # if correct
            if ((answer == 0 and data_question['avg'] == 0) or (
                    data_question['min'] <= answer / data_question['avg'] <= data_question['max'])):
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
        return False

    def submit_jolly(self, team: str, question: int) -> bool:
        """
        Submits a jolly for a team to a specific question.
        
        Parameters:
        team (str): The name of the team submitting the jolly.
        question (int): The number of the question for which the jolly is submitted.
        
        Returns:
        bool: True if the jolly was successfully submitted, otherwise False.
        """
        if team and question and not self.teams_data[team]['jolly']:
            self.teams_data[team]['jolly'] = question
            return True
        return False

    def g(self, p: int, k: int, m: float) -> int:
        """
        Calculates the bonus points for a team.
        
        Parameters:
        p (int): Base points.
        k (int): Number of correct answers.
        m (float): Modifier based on active teams.
        
        Returns:
        int: Calculated bonus points.
        """
        return int(p * e ** (-4 * (k - 1) / m))

    def Act_t(self) -> int:
        """
        Returns the number of active teams.
        
        Returns:
        int: Number of active teams.
        """
        return max(
            self._NUMBER_OF_TEAMS / 2,
            [self.teams_data[team]['active'] for team in self.NAMES_TEAMS].count(True),
            5,
        )

    def value_question(self, question: int) -> int:
        """
        Returns the value of a question.
        
        Parameters:
        question (int): The number of the question.
        
        Returns:
        int: Value of the question.
        """
        return self.Bp + self.g(
            self.Dp + self.A * sum(
                min(self.h, self.teams_data[team][question]['err'])
                for team in self.NAMES_TEAMS
            ) / self.Act_t(),
            self.questions_data[question]['ca'],
            self.Act_t(),
        )

    def value_question_x_squad(self, team: str, question: int) -> int:
        """
        Returns the points made by a team for a specific question.
        
        Parameters:
        team (str): The name of the team.
        question (int): The number of the question.
        
        Returns:
        int: Points made by the team for the question.
        """
        list_point_team = self.teams_data[team][question]

        return (
            list_point_team['sts'] * (self.value_question(question) + list_point_team['bonus'])
            - list_point_team['err'] * self.E
        ) * ((self.teams_data[team]['jolly'] == question) + 1)

    def total_points_team(self, team: str) -> int:
        """
        Returns the total points of a team.
        
        Parameters:
        team (str): The name of the team.
        
        Returns:
        int: Total points of the team.
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
