from tkinter import Label, LabelFrame, messagebox


class InterannotatorWindow:
    def __init__(self, win):
        self.win = win
        self.win.geometry("570x180")

        self.leftframe = LabelFrame(win, text="Annotation Controls", padx=5, pady=5)
        self.leftframe.grid(row=0, column=0, sticky="en")

        # TODO: Ask annotation dir
        # TODO: Get annotator names
        # TODO: Make sure to implement subject based option as well

        win.update()

        # TODO: Call interannotator agreement

        win.destroy()