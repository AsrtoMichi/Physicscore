from tkinter.filedialog import askopenfilename
from json import load
from tkinter import Tk


class JsonLoader():
    @staticmethod
    def json_load(master: Tk):
        return load(
            open(
                askopenfilename(
                    master=master,
                    title='Select the .json file',
                    filetypes=[('JavaScript Object Notation', '*.json')],
                )
            )
        )
