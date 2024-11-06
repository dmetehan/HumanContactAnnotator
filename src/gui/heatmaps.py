import os
from tkinter import Button, LabelFrame, messagebox, filedialog

from src.backend.visualize_heatmaps import heatmaps_for_gt, vis_heatmaps


class HeatmapsWindow:
    def __init__(self, win):
        self.win = win
        self.win.geometry("300x200+50+50")

        self.leftframe = LabelFrame(win, text="Annotation File", padx=5, pady=5)
        self.leftframe.grid(row=0, column=0, sticky="en")
        self.midframe = LabelFrame(self.win, text="Heatmaps", padx=5, pady=5)
        self.midframe.grid(row=0, column=1, sticky="en")

        self.button_visualize = Button(self.midframe, text="Visualize", wraplength=80)
        self.button_visualize.pack(padx=3, pady=3)
        self.button_visualize.bind('<ButtonRelease-1>', self.visualize)

        # Annotation file
        # TODO: Make sure to implement option for subject based foldering
        self.annot_file = ""
        self.button_annot = Button(self.leftframe, text="Select Annotation File", wraplength=180)
        self.button_annot.pack(padx=3, pady=3)
        self.button_annot.bind('<ButtonRelease-1>', self.selecting_folder)

        win.update()

        # TODO: Call heatmap visualization function

    def selecting_folder(self, event):
        filename = filedialog.askopenfilename()
        self.set_annot_file(filename)
        if self.annot_file != '':
            event.widget.config(text=self.annot_file)
        else:
            event.widget.config(text="Select Folder")

    def set_annot_file(self, annot_file):
        if annot_file != '' and not os.path.exists(annot_file):
            self.annot_file = ''
            messagebox.showerror("Path Error", message="Annotations folder doesn't exist!")
        else:
            self.annot_file = annot_file

    def visualize(self, _):
        # TODO: Make the visualization nicer with combining the heatmaps and color legend
        reg_cnts = heatmaps_for_gt(self.annot_file)
        self.win.destroy()
        vis_heatmaps(reg_cnts)

