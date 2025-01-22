from tkinter.filedialog import askopenfilename
from json import load
from tkinter import Tk

def json_load(master: Tk = None) -> dict:
    """
    Opens a file dialog to select a JSON file and loads its contents.
    
    Parameters:
    master (Tk, optional): The master tkinter window. Can be omitted.
    
    Returns:
    dict: The contents of the selected JSON file.
    """
    return load(
        open(
            askopenfilename(
                master=master,
                title='Select the .json file',
                filetypes=[('JavaScript Object Notation', '*.json')],
            )
        )
    )
