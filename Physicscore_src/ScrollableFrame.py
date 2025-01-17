from tkinter import Frame, Canvas, Scrollbar

class ScrollableFrame(Frame):
    def __init__(self, container, **kwargs):
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