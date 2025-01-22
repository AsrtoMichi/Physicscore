from tkinter import Tk, Variable

class IntVar(Variable):
    """Value holder for integer variables."""

    def __init__(self, master: Tk, n_question: int):
        """
        Constructs an integer variable.

        Parameters:
        master (Tk): The master tkinter window.
        n_question (int): The number of questions.
        """
        super().__init__(master)
        self.n_question = n_question

    def get(self) -> int:
        """
        Returns the value of the variable as an integer.
        
        Returns:
        int: The value of the variable if within the valid range, otherwise None.
        """
        try:
            value = int(self._tk.globalgetvar(self._name))
            return value if 0 < value <= self.n_question else None
        except ValueError:
            return None

class DoubleVar(Variable):
    """Value holder for float variables."""

    def __init__(self, master: Tk):
        """
        Constructs a float variable.

        Parameters:
        master (Tk): The master tkinter window.
        """
        super().__init__(master)

    def get(self) -> float:
        """
        Returns the value of the variable as a float.
        
        Returns:
        float: The value of the variable, or None if conversion fails.
        """
        try:
            return float(self._tk.globalgetvar(self._name))
        except ValueError:
            return None
