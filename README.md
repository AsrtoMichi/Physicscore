![324975101-5a9a03e5-f449-4fc1-b5a7-84d55af7ac5b](https://github.com/user-attachments/assets/e32c0c67-e8c9-4b9a-b0bd-f895b399e7a9)

### README

# Physicscore

Physicscore is an application designed to simulate physics team competitions. This tool is particularly useful for organizing and managing competitions in the style of the Physics Championships. You can find more information about the Physics Championships by visiting their [official website](https://olifis.org/).

## Configuration

Physicscore uses a JSON file to configure the competitions, teams, parameters, and generate graphs. Below is an example of a configuration JSON file:

```json
{
	"Name" : "Test",

	"Teams": ["Charlie", "David", "Eric", ["1", 0], "2", "3"],
	"Teams_ghost" : ["Ada"],
	"Teams_format": ["Name", ["Name", "Handicap as int value"]],

	"Timers" : {
		"time" : 1,
		"time_for_jolly" : 10,
		"time_format": "use min"
	},
	
	"Patameters": {
		"Bp" : 20,
		"Dp" : 80,
		"E" : 10,
		"A" : 20,
		"h": 3
	},

	"Solutions" : [
	
		[1.0, 1.0],
		[2.0, 1.0],
		[3.0, 1.0],
		[4.0, 1.0]
	],

	"Solution_format": ["answer", "relative error"],


	"Actions" : {
		"teams" : ["Ada", "Bob"],
		
		"jokers" : [
			["Ada", 1, 10],
			["Bob", 2, 30]
		],

		"jolly_format" : ["team", "question", "time in seconds"],

		"answers" : [
			["Ada", 1, 1.0, 20],
			["Bob", 3, 3.0, 15],
			["Ada", 2, 2.0, 40]
		],

		"answer_format" : ["team", "question", "answer", "time in seconds"]
	}
}
```

### JSON File Details

- **Name**: Specifies the name of the competition.
- **Teams**: List of participating teams with their handicap (can be omitted if equal to 0, es: [name_team, handicap])
- **Teams_ghost**: Ghost teams participating in the competition.
- **Timers**: Configure the competition time and the time for jokers.
- **Parameters**: Competition parameters using Python notation.
- **Solutions**: Expected solutions for the questions.
- **Actions**:
  - **teams**: List of teams that take actions.
  - **jokers**: Details of joker actions (team, question number, score).
  - **answers**: Answers provided by teams (team, question number, answer, score).

## Commands and Shortcuts

- **Enter**: To submit an answer.
- **Shift + Enter**: To use a joker.

## Graph Generation

Physicscore can also generate graphs based on the JSON configuration file. This helps visualize the data and performance of the teams during the competition.

## How to Use

1. Modify the JSON configuration file according to your needs.
2. Launch the Physicscore application.
3. Use the keyboard shortcuts to submit answers and joker actions.
4. Generate graphs to visualize the competition data and team performance.
