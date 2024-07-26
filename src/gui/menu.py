from tkinter import Button

from .annotation import InitAnnotationWindow
from .interannotator import InterannotatorWindow
from .heatmaps import HeatmapsWindow


class InitWindow:
    def __init__(self, win):
        self.win = win

        self.button_annotate = Button(win, text="Annotate", wraplength=80)
        self.button_annotate.pack(padx=3, pady=3)
        self.button_annotate.bind('<ButtonRelease-1>', self.init_annotation_window)

        self.button_interannotator_agreement = Button(win, text="Interannotator Agreement", wraplength=80)
        self.button_interannotator_agreement.pack(padx=3, pady=3)
        self.button_interannotator_agreement.bind('<ButtonRelease-1>', self.init_interannotator_window)

        self.button_visualize_annotations = Button(win, text="Visualize Annotations", wraplength=80)
        self.button_visualize_annotations.pack(padx=3, pady=3)
        self.button_visualize_annotations.bind('<ButtonRelease-1>', self.init_visualization_window)

    def remove_buttons(self):
        self.button_annotate.destroy()
        self.button_interannotator_agreement.destroy()
        self.button_visualize_annotations.destroy()

    def init_annotation_window(self, event):
        self.remove_buttons()
        InitAnnotationWindow(self.win)

    def init_interannotator_window(self, event):
        self.remove_buttons()
        InterannotatorWindow(self.win)

    def init_visualization_window(self, event):
        self.remove_buttons()
        HeatmapsWindow(self.win)
