from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
from json import load, JSONDecodeError
from tkinter import Tk

def json_load(master: Tk = None) -> dict:
    """
    Opens a file dialog to select a JSON file and loads its contents.
    
    Parameters:
    master (Tk, optional): The master tkinter window. Can be omitted.
    
    Returns:
    dict: The contents of the selected JSON file.
    """
    try:
        with open(
            askopenfilename(
                master=master,
                title='Select the .json file',
                filetypes=[('JavaScript Object Notation', '*.json')],
            ), 
            'r', 
            encoding='utf-8'
        ) as file:
            return load(file)

    except FileNotFoundError:
        showerror("File Not Found", "Please select an existing file.", detail="Error code: 211", master=master)
        raise RuntimeWarning("File not found.")

    except PermissionError:
        showerror("Permission Error", "You don't have permission to access this file.", detail="Error code: 212", master=master)
        raise RuntimeWarning("Permission error.")

    except TypeError:
        showerror("Type Error", "Invalid file type or content.", detail="Error code: 213", master=master)
        raise RuntimeWarning("Type error.")

    except JSONDecodeError as e:
        showerror("JSON Decode Error", "The selected file contains invalid JSON format.", detail=f'{e}{chr(10)}Error code: 214', master=master)
        raise RuntimeWarning("JSON parsing error.")

