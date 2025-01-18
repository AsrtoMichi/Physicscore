from tkinter.filedialog import askopenfilename
from json import load
from tkinter import Tk



def json_load(master: Tk = None):
    return load(
        open(
            askopenfilename(
                master=master,
                title='Select the .json file',
                filetypes=[('JavaScript Object Notation', '*.json')],
            )
        )
    )
