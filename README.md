### README

# Installation

To install the app:
1. Clone the source code using git: ```git clone AsrtoMichi/Physicscore```
2. Navigate to the directory: ```cd Physicscore```
3. Install the package using: ```pip install .```

# Physicscore

Physicscore is an application designed to simulate physics team competitions. This tool is particularly useful for organizing and managing competitions in the style of the Physics Championships. You can find more information about the Physics Championships by visiting their [official website](https://olifis.org/).

## How to Use

1. Modify the JSON configuration file according to your needs.
2. Launch the Physicscore application with the command ```physicscore``` and select the .json file.
3. Submit answers and joker actions using the Receiver window.
4. Save data in a .json file.
5. Generate graphs to visualize the competition data and team performance.

## Commands and Shortcuts

- **Enter**: To submit an answer.
- **Shift + Enter**: To use a joker.

# Graph Generation

ReportGenerator is a script useful for generating a detailed report about the competition.

## How to Use

1. Modify the JSON configuration file according to your needs.
2. Launch the application with the command ```reportgen```.
3. Select the .json file and save the report in a .html file.
4. Open the .html file using a browser or another tool.

# Configure the .json file

Physicscore uses a JSON file to configure the competitions, teams, parameters, and generate graphs. Below is an example of a configuration JSON file:

```json
{
    "Name": "Test",

    "Teams": [["Charlie", 100], "David", "Eric"],
    "Teams_ghost": ["Ada"],

    "Teams_format": ["Name", ["Name", "Handicap as int value"]],

    "Timers": {
        "time": 1,
        "time_for_jolly": 10,
        "time_format": "use min"
    },
    
    "Parameters": {
        "Bp": 20,
        "Dp": 80,
        "E": 10,
        "A": 20,
        "h": 3
    },

    "Solutions": [
        [1.0, 1.0],
        [2.0, 1.0],
        [3.0, 1.0],
        [4.0, 1.0]
    ],

    "Solution_format": ["answer", "relative error"],

    "Actions": {
        "teams": ["Ada", "Bob"],
        
        "jokers": [
            ["Ada", 1, 10],
            ["Bob", 2, 30]
        ],

        "jolly_format": ["team", "question", "time in seconds"],

        "answers": [
            ["Ada", 1, 1.0, 20],
            ["Bob", 3, 3.0, 15],
            ["Ada", 2, 2.0, 40]
        ],

        "answer_format": ["team", "question", "answer", "time in seconds"]
    }
}
```

## JSON File Explanation

- **Name**: Specifies the name of the competition.
- **Teams**: List of participating teams with their handicap (can be omitted if equal to 0, e.g., [name_team, handicap]).
- **Teams_ghost**: Ghost teams participating in the competition.
- **Timers**: Configure the competition time and the time for jokers.
- **Parameters**: Competition parameters using Python notation.
- **Solutions**: Expected solutions for the questions.
- **Actions**:
  - **teams**: List of teams that take actions.
  - **jokers**: Details of joker actions (team, question number, time in seconds).
  - **answers**: Answers provided by teams (team, question number, answer, time in seconds).

## Acknowledgments 

I would like to thank the following people for their contributions:
- Alessandro Chiozza: for help with data structures.
- Federico Micelli: for their specific contribution.
- Giorgio Sorgente: for help with tkinter library.
- Gabriele Trisolino: for all the ideas on how to improve the program.

## License
This project is licensed under the GPL3 License.
