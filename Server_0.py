import subprocess
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from flask_login import LoginManager, UserMixin as User, login_user, logout_user, login_required, current_user

from flask_socketio import SocketIO, emit
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

from Physicscore.src.JsonLoader import json_load
from Physicscore.src.Competition import Competition
from Physicscore.src.HtmlTable import html_table

from secrets import token_urlsafe, token_hex
from tkinter.filedialog import askdirectory
from os.path import join
from json import dump
from platform import system as plt_system

from simple_websocket import Server as WebSocketServer


def get_ip_address():
    try:
        system = plt_system()
        if system in ["Linux", "Darwin"]:  # Mac OS is recognized as "Darwin"
            return subprocess.run(
                "ip addr show eth0 | grep 'inet ' | awk '{ print $2 }' | cut -f1 -d'/'",
                shell=True,
                check=True,
                stdout=-1,
                stderr=-1
            ).stdout.decode('utf-8').strip(). split('\n')[0]

        elif system == "Windows":
            for line in subprocess.run(
                "ipconfig",
                shell=True,
                check=True,
                stdout=-1,
                stderr=-1
                ).stdout.decode('utf-8').split('\n'):

                if 'IPv4 Address' in line:
                    return line.split(':')[-1].strip()
        else:
            raise Exception(f"Unsupported operating system: {system}")


    except subprocess.CalledProcessError as e:
        print(f"Error during the execution of command: {e}")
        return None


def start_gunicorn():
    try:
        command = [
            "gunicorn",
            "--bind", "0.0.0.0:5000",
            "--workers", "4",
            "appserver:App"
        ]
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'avvio di Gunicorn: {e}")


data = json_load()
users = {user : {'password': token_urlsafe(12), 'teams': data['Teams'][user]} for user in data['Teams'].keys()}
print(users)
for user in users.keys():
    pass
competition = Competition(data, [element for sublist in data['Teams'].values() for element in sublist])




app = Flask("Physicscore")
app.secret_key = token_hex(32)

login_manager = LoginManager()
login_manager.init_app(app)

socketio = SocketIO(app, async_mode='threading', websocket=WebSocketServer)
limiter = Limiter(get_remote_address, app=app, storage_uri="redis://localhost:6379")
Talisman(app)



@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return '''
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
</head>
<body>



    <form action='login' method='POST'>
        <input type='text' name='username' id='username' placeholder='username'/>
        <input type='password' name='password' id='password' placeholder='password'/>
        <input type='submit' name='submit'/>
    </form>


</body>
</html>
'''

    username = request.form['username']
    if username in users and request.form['password'] == users[username]['password']:
        user = User()
        user.id = username
        login_user(user)
        return redirect(url_for('submit'))

    return 'Bad login'

@app.route('/logout')
def logout():
    logout_user()
    return 'Logged out'

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(join(app.root_path, 'Physicscore', 'src'),
                               'Physicscore.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/submit', methods=['GET', 'POST'])
@login_required
#@limiter.limit("10 per minute")
def submit():
    if request.method == 'POST':
  
        try:
            team = request.form.get('menu')
            question = int(request.form.get('question_number'))
            answer = float(request.form.get('answer'))
            
            match request.form.get('submit'): 
                case 'jolly':
                    competition.submit_jolly(team, question)
                case 'answer':
                    competition.submit_answer(team, question, answer)

            
        except TypeError as e:
            print

    return f'''

    <form action="/submit" method="POST">
        <label for="menu">Scegli un'opzione:</label>
        <select id="menu" name="menu" reqired="true">
            { ''.join([f'           <option value="{ team }">{ team }</option>{chr(10)}'   for team in [''] + users[current_user.id]['teams']])}

        </select>

        <br><br>

        <label for="question_number">Question number:</label>
        <input type="number" name="question_number" step="1">

        <br><br>

        <label for="answer">Answer:</label>
        <input type="text" id="answer" name="answer" step="any">

        <br><br>

        <button type="submit" name="submit" value="jolly">Submit jolly</button>
        <button type="submit" name="submit" value="answer">Submit answer</button>
        
    </form>
'''


@app.route('/')
def home():
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="{url_for('favicon')}">
    <title>Physicscore</title>
    <style nonce="{token_urlsafe(16)}">
        .green-background {{
            background-color: green;
        }}
        .white-background {{
            background-color: white;
        }}
        .red-background {{
            background-color: white;
        }}
        table.custom-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        table.custom-table th, table.custom-table td {{
            border: 1px solid black;
            padding: 8px;
            text-align: left;
        }}
    </style>
    
</head>
<body>

    <h1>Data Updates</h1>
    {html_table(competition)}

</body>
</html>
'''

@app.route('/license')
def license():
    return f'''
<h1>License</h1>
<pre>
An app for physique competition in teams.
Copyright (C) 2024 AsrtoMichi

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.


This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <a href="https://www.gnu.org/licenses/">https://www.gnu.org/licenses/</a>.

Contact me by email at <a href="mailto:asrtomichi@gmail.com">asrtomichi@gmail.com</a>.
</pre>
'''


if __name__ == '__main__':
    print(f'Il tuo IP pubblico è: {get_ip_address()}')
    app.run(debug=True)
