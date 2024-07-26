from tkinter import Label, LabelFrame, messagebox


class HeatmapsWindow:
    def __init__(self, win):
        self.win = win
        self.win.geometry("570x180")

        self.leftframe = LabelFrame(win, text="Annotation Controls", padx=5, pady=5)
        self.leftframe.grid(row=0, column=0, sticky="en")

        # TODO: Get annotation file to visualize
        # TODO: Make sure to implement option for subject based foldering

        win.update()

        # TODO: Call heatmap visualization function

        win.destroy()