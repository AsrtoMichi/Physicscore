from tkinter.filedialog import asksaveasfilename
import matplotlib.pyplot as plt
from io import BytesIO
from base64 import b64encode
from os.path import join, dirname
from collections import Counter
from tabulate import tabulate


from Physicscore_src.Competition import Competition
from Physicscore_src.JsonLoader import JsonLoader


def avg(data):
    return None if len(data) == 0 else sum(data) / len(data)


# ---------------- load data  ---------------- #

data = JsonLoader.json_load()

competition = Competition(data, data['Actions']['teams'])

TOTAL_TIME = data['Timers']['time'] * 60

data_teams = {team: [] for team in competition.NAMES_TEAMS}
data_question = {
    question: [] for question in competition.NUMBER_OF_QUESTIONS_RANGE_1
}


def register_data():
    for team in competition.NAMES_TEAMS:
        data_teams[team].append(
            (timer, competition.total_points_team(team)))

    for question in competition.NUMBER_OF_QUESTIONS_RANGE_1:
        data_question[question].append(
            (timer, competition.value_question(question))
        )


timer = TOTAL_TIME
register_data()

for action in sorted(
    data['Actions']['answers'] + data['Actions']['jokers'],
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


# ---------------- Total points in the time  ---------------- #


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


# ---------------- Value in the time  ---------------- #

plt.figure()
plt.xlabel('Time')
plt.ylabel('Points')

for team, points in data_question.items():
    plt.step(*zip(*points), where='post', label=team)
plt.gca().invert_xaxis()
plt.legend()


img_buffer = BytesIO()
plt.savefig(img_buffer, format='png')
Value_x_time = b64encode(img_buffer.getvalue()).decode('utf-8')


# ---------------- Istogram correct vs incorrect  ---------------- #

width = 0.4
plt.figure()
plt.xlabel('Number')
plt.ylabel('Question')
plt.bar(competition.NUMBER_OF_QUESTIONS_RANGE_1, [
        question['ca'] for question in competition.questions_data.values()], width, label='Correct')
plt.bar([x+width for x in competition.NUMBER_OF_QUESTIONS_RANGE_1], [sum(team[question]['err']
        for team in competition.teams_data.values()) for question in competition.NUMBER_OF_QUESTIONS_RANGE_1], width, label='Incorrect')
plt.legend()

img_buffer = BytesIO()
plt.savefig(img_buffer, format='png')
ca_vs_inca = b64encode(img_buffer.getvalue()).decode('utf-8')

# ---------------- Jolly for question ---------------- #

plt.figure()
plt.xlabel('Jolly')
plt.ylabel('Question')
plt.bar(competition.NUMBER_OF_QUESTIONS_RANGE_1,  [[team['jolly'] == queston for team in competition.teams_data.values(
)].count(True) for queston in competition.NUMBER_OF_QUESTIONS_RANGE_1],)

img_buffer = BytesIO()
plt.savefig(img_buffer, format='png')
jolly4question = b64encode(img_buffer.getvalue()).decode('utf-8')

# ---------------- Answerers range  ---------------- #

answers_graph = []

for question, question_data in enumerate(data['Solutions'], 1):
    plt.figure()
    fig, ax = plt.subplots()
    plt.title(f"Question {question}")
    plt.ylabel('Answer')
    answers = tuple(answer[2] for answer in data['Actions']
                    ['answers'] if answer[1] == question)

    plt.scatter(range(1, len(answers)+1), answers)
    avg_question = avg(answers)
    if avg_question:
        plt.axhline(y=avg_question, color='r', linestyle='--', label='Average')
    ax.axhspan(question_data[0] * (100 - question_data[1]) / 100, question_data[0]
               * (100 + question_data[1]) / 100, color='green', alpha=0.3)

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    answers_graph.append(b64encode(img_buffer.getvalue()).decode('utf-8'))




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
        <link rel="icon" href="data:image/png;base64,{b64encode(open(join(dirname(__file__), 'Resources', 'Physicscore.ico'), 'rb').read()).decode('utf-8')}" type="image/x-icon">
        <title>Report about {data['Name']}</title>
    </head>

    <body>

        <h1>Final screen</h1


            {tabulate([[None]*2+list(competition.NUMBER_OF_QUESTIONS_RANGE_1), [None]*2+[competition.value_question(question) for question in competition.NUMBER_OF_QUESTIONS_RANGE_1], *[[ team, competition.total_points_team(team), *[competition.value_question_x_squad(team, question) for question in competition.NUMBER_OF_QUESTIONS_RANGE_1]] for team in competition.NAMES_TEAMS]],  tablefmt='html')}

        <h1>Teams</h1>
            <h2>Total points in the time</h2>
                <img src="data:image/png;base64,{Total_points_x_time}" alt="Total points in the time">

        <h1>Questions</h1>

            <h2>Total points in the time</h2>
                <img src="data:image/png;base64,{Value_x_time}" alt="Total points in the time">

            <h2>Answers correct vs incorrect</h2>
                <img src="data:image/png;base64,{ca_vs_inca}" alt="Answers correct vs incorrect">

            <h2>Answers to each question</h2>
                {f'{chr(10)}                '.join(f'<img src="data:image/png;base64,{graph}" alt="Answers question {question}">' for question, graph in enumerate(answers_graph, 1))}

            <h2>Jolly for question</h2>
                <img src="data:image/png;base64,{jolly4question}" alt="Jolly for question">

    </body>
</html>
'''

open(f"{data['Name']}.html", 'w', encoding='utf-8').write(html)
