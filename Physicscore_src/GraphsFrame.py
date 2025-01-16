from random import randrange
from math import log10, ceil
from typing import Dict, Tuple, List
from tkinter import Tk, Frame, Canvas, Label, BooleanVar, Checkbutton

from .Competition import Competition
from .ScrollableFrame import ScrollableFrame


class GraphsFrame(Frame):
    def __init__(self, master: Tk, data: dict):
        super().__init__(master)

        master.title(data['Name'])

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

        Graph_Frame(self, data_teams, TOTAL_TIME).pack()
        Graph_Frame(self, data_question, TOTAL_TIME).pack(padx=20)


class Graph_Frame(Frame):
    def __init__(
        self,
        master: Frame,
        data: Dict[int | str, List[Tuple[int, int, int, int]]],
        max_x: int,
    ):
        super().__init__(master)

        height = 400
        width_canvas = 700
        width_frame = 300

        keys = data.keys()

        # Create the canvas for the teams graph
        canvas = Canvas(self, width=width_canvas, height=height, bg='white')
        canvas.grid(column=0, row=0)

        scroll_frame = ScrollableFrame(self, width=width_frame, height=height)
        scroll_frame.grid(column=1, row=0)
        Label(scroll_frame.scrollable_frame, text='Show/Hide Teams').pack()

        # Create checkboxes for each team
        vars = {key: BooleanVar(self) for key in keys}
        colors_iterable = iter(
            [
                'red',
                'green',
                'blue',
                'orange',
                'purple',
                'pink',
                'brown',
                'black',
                'white',
                'gray',
                'cyan',
                'magenta',
                'lime',
                'indigo',
                'violet',
                'gold',
                'silver',
                'yellow',
                'maroon',
                'navy',
                'teal',
                'lavender',
                'olive',
                'coral',
                'turquoise',
                'salmon',
                'plum',
                'orchid',
                'chocolate',
                'ivory',
                'beige',
                'mint',
                'peach',
                'amber',
            ]
        )
        colors = {
            key: next(
                colors_iterable,
                f'#{randrange(256):02x}{randrange(256):02x}{randrange(256):02x}',
            )
            for key in keys
        }

        def update_graph():
            # Draw lines for each team if the checkbox is selected
            for key in keys:
                for element in canvas.find_withtag(f'tag_{key}'):
                    canvas.itemconfigure(
                        element, state='normal' if vars[key].get(
                        ) else 'hidden'
                    )

        for key in keys:
            Checkbutton(
                scroll_frame.scrollable_frame,
                text=key,
                variable=vars[key],
                fg=colors[key],
                command=update_graph,
            ).pack(anchor='w')

        def max_axis(max: int) -> int:
            fact = 10 ** int(log10(max))
            return int(ceil(max / fact) * fact)

        # cordinate O
        x_o = 70
        y_o = height - 50

        # axis lenght
        x_a_l = width_canvas - 100
        y_a_l = height - 80

        # number of indicator
        x_a_i_n = 10
        y_a_i_n = 10

        # max value of each axis
        max_a_x = max_axis(max_x)
        max_a_y = max_axis(
            max(line[-1] for data_set in data.values() for line in data_set)
        )

        # distance between indicator
        x_a_i_d = x_a_l / x_a_i_n
        y_a_i_d = y_a_l / y_a_i_n

        # interval betwen indicator
        x_a_d_i = max_a_x / x_a_i_n
        y_a_d_i = max_a_y / y_a_i_n

        # unit on the axis
        u_x_a = x_a_l / max_a_x
        u_y_a = y_a_l / max_a_y

        # Draw the x and y axes
        canvas.create_line(x_o, y_o, x_o + x_a_l, y_o,
                           arrow='last', tags='x-axis')
        canvas.create_line(x_o, y_o, x_o, y_o - y_a_l,
                           arrow='last', tags='y-axis')

        # Label the axes
        canvas.create_text(
            x_o + x_a_l / 2, canvas.winfo_reqheight() - 15, text='Time', tags='time'
        )
        canvas.create_text(15, y_o - y_a_l / 2, text='Value',
                           angle=90, tags='value')

        # Add grid lines and labels
        for i in range(1, x_a_i_n + 1):
            x = x_o + i * x_a_i_d
            canvas.create_line(x, y_o, x, y_o - y_a_i_d * y_a_i_n, dash=(2, 2))
            canvas.create_text(
                x, y_o + 10, text=str((max_x - i * x_a_d_i) / 60))
        canvas.create_text(x_o, y_o + 10, text=str(max_x / 60))

        for i in range(1, y_a_i_n + 1):
            y = y_o - i * y_a_i_d
            canvas.create_line(x_o, y, x_o + x_a_i_n * x_a_i_d, y, dash=(2, 2))
            canvas.create_text(x_o - 25, y, text=str(i * y_a_d_i))

        for tag, points in data.items():
            line_tag = f'tag_{tag}'
            color = colors[tag]
            for point_index in range(len(points) - 1):
                y1_2_coord = y_o - points[point_index][1] * u_y_a
                x2_3_coord = (max_x - points[point_index + 1][0]) * u_x_a + x_o
                canvas.create_line(
                    ((max_x - points[point_index][0])
                     * u_x_a + x_o, y1_2_coord),
                    (x2_3_coord, y1_2_coord),
                    tags=line_tag,
                    width=2,
                    fill=color,
                )
                canvas.create_line(
                    (x2_3_coord, y1_2_coord),
                    (x2_3_coord, y_o - points[point_index + 1][1] * u_y_a),
                    tags=line_tag,
                    width=2,
                    fill=color,
                )

        update_graph()
