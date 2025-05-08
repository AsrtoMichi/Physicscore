from os.path import join, dirname, isfile
from sys import exit as sys_exit, platform
from tkinter import Tk, Button
from tkinter.messagebox import askokcancel, showinfo
from traceback import format_exc
from .GraphsFrame import GraphsFrame
from .CompetitionFrame import CompetitionFrame
from .JsonLoader import json_load

class Physicscore(Tk):
    """
    A class to manage and run the Physicscore application.
    """

    def __init__(self):
        """
        Initializes the Physicscore application.
        """
        super().__init__()

        Button(
            self,
            text="About",
            command=lambda: showinfo(
                "License",
                """Physicscore, an app for physique competition in teams.
Copyright (C) 2024  AsrtoMichi

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact me by email at a asrtomichi@gmail.com.""",
                master=self
            )
        ).pack(side='bottom', anchor='e', padx=8, pady=8)

        if platform.startswith('win'):
            self.iconbitmap(default=join(dirname(__file__), 'Physicscore.ico'))

        self.protocol(
            'WM_DELETE_WINDOW',
            lambda: sys_exit()
            if askokcancel("Confirm exit", "Data can be lost.", master=self)
            else None,
        )

        self.button1 = Button(self)
        self.button2 = Button(self)

        self.show_menu()

    def show_menu(self):
        """
        Displays the main menu of the application.
        """
        self.button1.config(text="Start competition", command=self.new_competition)
        self.button2.config(text="Draw graphs", command=self.show_graph)

        self.button1.pack_forget()
        self.button2.pack_forget()
        self.button1.pack()
        self.button2.pack()

    def destroy_frame(self):
        """
        Destroys the current frame and returns to the main menu.
        """
        self.frame.destroy()
        self.show_menu()

    def new_competition(self):
        """
        Loads the competition data and sets up the competition frame.
        """
        try:
            self.data = json_load(self)
            self.button1.config(text="Start", command=self.start_competition)
            self.button2.pack_forget()
        except RuntimeWarning:
            self.show_menu()

    def start_competition(self):
        """
        Starts the competition with the loaded data.
        """
        self.button1.pack_forget()
        try:
            self.frame = CompetitionFrame(self, self.data)
            self.frame.pack(fill='both', expand=True)
        except RuntimeWarning:
            self.show_menu()
        del self.data

    def show_graph(self):
        """
        Loads the graph data and sets up the graph frame.
        """
        try:
            self.button1.config(text="Menu", command=self.destroy_frame)
            self.button2.pack_forget()
            self.frame = GraphsFrame(self, json_load(self))
            self.frame.pack()
        except RuntimeWarning:
            self.show_menu()


def run_physicscore():
    try:
        Physicscore().mainloop()
    except Exception as e:  # Using Exception instead of Error
        showerror("Unexpected", f"An error occurred, please report at https://github.com/AsrtoMichi/Physicscore/issues", 
                  detail=f"Error code: 1\n{format_exc()}") 