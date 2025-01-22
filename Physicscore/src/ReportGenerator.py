from tkinter.filedialog import asksaveasfilename
import matplotlib.pyplot as plt
from io import BytesIO
from base64 import b64encode
from os.path import join, dirname
from .Competition import Competition
from .JsonLoader import json_load

def generate_report():
    """
    Generates a detailed HTML report of the competition results, including graphs and data visualizations.

    The report includes the following sections and visualizations:
    - Final screen: A table showing the final points for each team and question.
    - Teams:
        - Total points over time: A graph showing the total points for each team over time.
    - Questions:
        - Total points over time: A graph showing the value of each question over time.
        - Correct vs Incorrect Answers: A histogram comparing the number of correct and incorrect answers for each question.
        - Answers to each question: Scatter plots showing the answers to each question and their averages.
        - Jolly per question: A bar chart showing the number of jolly used for each question.
    """

    def avg(data) -> float:
        """
        Calculates the average value of a list.
        
        Parameters:
        data (list): The list of numbers.
        
        Returns:
        float: The average value of the list, or None if the list is empty.
        """
        return None if len(data) == 0 else sum(data) / len(data)

    # ---------------- load data  ---------------- #
    data = json_load()

    competition = Competition(data, data['Actions']['teams'])
    N_Q_R, N_T = list(competition.NUMBER_OF_QUESTIONS_RANGE_1), competition.NAMES_TEAMS
    TOTAL_TIME = data['Timers']['time'] * 60

    data_teams = {team: [] for team in N_T}
    data_question = {question: [] for question in N_Q_R}

    def register_data():
        """
        Registers the data points for teams and questions at the current timer value.
        """
        for team in N_T:
            data_teams[team].append((timer, competition.total_points_team(team)))

        for question in N_Q_R:
            data_question[question].append((timer, competition.value_question(question)))

    timer = TOTAL_TIME
    register_data()

    for action in sorted(data['Actions']['answers'] + data['Actions']['jokers'], key=lambda x: x[-1], reverse=True):
        timer = action[-1]
        if len(action) == 3:
            competition.submit_jolly(*action[:2])
        else:
            competition.submit_answer(*action[:3])
        register_data()

    timer = 0
    register_data()

    # ---------------- Total points over time  ---------------- #
    plt.figure()
    plt.xlabel('Time')
    plt.ylabel('Points')

    for team, points in data_teams.items():
        plt.step(*zip(*points), where='post', label=team)
    plt.gca().invert_xaxis()
    plt.legend()

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    Total_points_x_time = b64encode(img_buffer.getvalue()).decode('utf-8')
    plt.close()

    # ---------------- Value over time  ---------------- #
    plt.figure()
    plt.xlabel('Time')
    plt.ylabel('Points')

    for question, points in data_question.items():
        plt.step(*zip(*points), where='post', label=question)
    plt.gca().invert_xaxis()
    plt.legend()

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    Value_x_time = b64encode(img_buffer.getvalue()).decode('utf-8')
    plt.close()

    # ---------------- Histogram correct vs incorrect  ---------------- #
    width = 0.4
    plt.figure()
    plt.xlabel('Question')
    plt.ylabel('Number')
    plt.bar(N_Q_R, [question['ca'] for question in competition.questions_data.values()], width, label='Correct')
    plt.bar([x + width for x in N_Q_R], [sum(team[question]['err'] for team in competition.teams_data.values()) for question in N_Q_R], width, label='Incorrect')
    plt.legend()

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    ca_vs_inca = b64encode(img_buffer.getvalue()).decode('utf-8')
    plt.close()

    # ---------------- Jolly per question ---------------- #
    plt.figure()
    plt.xlabel('Question')
    plt.ylabel('Jolly')
    plt.bar(N_Q_R, [[team['jolly'] == question for team in competition.teams_data.values()].count(True) for question in N_Q_R])

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    jolly4question = b64encode(img_buffer.getvalue()).decode('utf-8')
    plt.close()

    # ---------------- Answers range  ---------------- #
    answers_graph = []

    for question, question_data in enumerate(data['Solutions'], 1):
        plt.figure()
        fig, ax = plt.subplots()
        plt.title(f"Question {question}")
        plt.ylabel('Answer')
        answers = tuple(answer[2] for answer in data['Actions']['answers'] if answer[1] == question)

        plt.scatter(range(1, len(answers) + 1), answers)
        avg_question = avg(answers)
        if avg_question:
            plt.axhline(y=avg_question, color='r', linestyle='--', label='Average')
        ax.axhspan(question_data[0] * (100 - question_data[1]) / 100, question_data[0] * (100 + question_data[1]) / 100, color='green', alpha=0.3)

        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        answers_graph.append(b64encode(img_buffer.getvalue()).decode('utf-8'))
        plt.close()

    lf = chr(10)

    html = f'''
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
            table, th, td {{
                border: 1px solid black;
            }}
            </style>
            <link rel="icon" href="data:image/png;base64,{b64encode(open(join(dirname(__file__), 'Physicscore.ico'), 'rb').read()).decode('utf-8')}" type="image/x-icon">
            <title>Report about {data['Name']}</title>
        </head>

        <body>
            <h1>Final screen</h1>
                <table style="width:100%">
    {lf.join([f"                <tr>{lf}{''.join([f'                    <td>{cell}</td>{lf}' for cell in row])}                </tr>" for row in [['']*3 + N_Q_R, ['']*3 + list(map(competition.value_question, N_Q_R)), *[[position, team, competition.total_points_team(team), *[competition.value_question_x_squad(team, question) for question in N_Q_R]] for position, team in enumerate(sorted(N_T, key=competition.total_points_team, reverse=True))]]])}
                </table>
            
            <h1>Teams</h1>
                <h2>Total points over time</h2>
                    <img src="data:image/png;base64,{Total_points_x_time}" alt="Total points over time">

            <h1>Questions</h1>
                <h2>Total points over time</h2>
                    <img src="data:image/png;base64,{Value_x_time}" alt="Total points over time">

                <h2>Correct vs Incorrect Answers</h2>
                    <img src="data:image/png;base64,{ca_vs_inca}" alt="Correct vs Incorrect Answers">

                <h2>Answers to each question</h2>
                    {f'{lf}                '.join(f'<img src="data:image/png;base64,{graph}" alt="Answers question {question}">' for question, graph in enumerate(answers_graph, 1))}

                <h2>Jolly per question</h2>
                    <img src="data:image/png;base64,{jolly4question}" alt="Jolly per question">
        </body>
    </html>
    '''

    open(asksaveasfilename(defaultextension='.html', filetypes=[('HyperText Markup Language', '*.html')]), 'w', encoding='utf-8').write(html)
