from tkinter import Frame, Canvas, Scrollbar

class ScrollableFrame(Frame):
    """
    A frame that contains a scrollable area using a canvas and scrollbar.
    
    Attributes:
    container (Frame): The parent frame for this scrollable frame.
    **kwargs: Additional keyword arguments to be passed to the Frame.
    """

    def __init__(self, container, **kwargs):
        """
        Initializes the ScrollableFrame with a container and additional options.
        
        Parameters:
        container (Frame): The parent frame for this scrollable frame.
        **kwargs: Additional keyword arguments to be passed to the Frame.
        """
        super().__init__(container, **kwargs)
        canvas = Canvas(self, **kwargs)
        scrollbar = Scrollbar(self, orient='vertical', command=canvas.yview)
        self.scrollable_frame = Frame(canvas, **kwargs)

        self.scrollable_frame.bind(
            '<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
