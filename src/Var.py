
from tkinter import Variable

from .Physicscore import Main

class IntVar(Variable):
    '''Value holder for integer variables.'''

    def __init__(self, master: Main, n_question: int):
        '''Construct an integer variable.

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to 0)
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        '''
        super().__init__(self, master)
        self.n_question = n_question

    def get(self) -> int:
        '''Return the value of the variable as an integer.'''
        try:
            value = int(self._tk.globalgetvar(self._name))
            return value if 0 < value <= self.n_question else None
        except ValueError:
            return None


class DoubleVar(Variable):
    '''Value holder for float variables.'''

    def __init__(self, master: Main):
        '''Construct a float variable.

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to 0.0)
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        '''
        super().__init__(self, master)

    def get(self) -> float:
        '''Return the value of the variable as an integer.'''
        try:
            return float(self._tk.globalgetvar(self._name))
        except ValueError:
            return None
