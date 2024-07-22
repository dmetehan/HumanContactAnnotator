import os.path
from tkinter import simpledialog, Frame, Label, StringVar, OptionMenu, LabelFrame, Button, N, LEFT, RIGHT, TOP, BOTTOM, BOTH, filedialog, messagebox

from .annotate import annotate_all


class InitWindow:
    def __init__(self, win):
        # TODO: read configuration including previously selected folder, annotator, output directory
        self.win = win

        self.leftframe = LabelFrame(win, text="Frames Folder", padx=5, pady=5)
        self.leftframe.grid(row=0, column=0, sticky="en")
        self.midframe = LabelFrame(win, text="Annotations Folder", bg="yellow", padx=5, pady=5)
        self.midframe.grid(row=0, column=1, sticky="en")
        self.rightframe = LabelFrame(win, text="Annotator Name", padx=5, pady=5)
        self.rightframe.grid(row=0, column=2, sticky="en")
        self.lastframe = LabelFrame(win, text="Annotating", padx=5, pady=5)
        self.lastframe.grid(row=0, column=3, sticky="en")

        # folder selection
        self.frames_dir = ""
        self.button_frames = Button(self.leftframe, text="Select Folder", wraplength=80)
        self.button_frames.pack(padx=3, pady=3)
        self.button_frames.bind('<ButtonRelease-1>', self.selecting_folder)

        # Annotation dir
        self.annot_dir = ""
        self.button_annot = Button(self.midframe, text="Select Folder", wraplength=80)
        self.button_annot.pack(padx=3, pady=3)
        self.button_annot.bind('<ButtonRelease-1>', self.selecting_folder)

        # Annotator selection drop down
        self.annotators = ["Metehan", "Ronald"]
        self.selected_annotator = StringVar()
        self.selected_annotator.set("Select")
        self.annotator_dropdown = OptionMenu(self.rightframe, self.selected_annotator, *self.annotators)
        self.annotator_dropdown.pack(padx=3, pady=3)
        self.button_add_new = Button(self.rightframe, text="Add New", wraplength=80)
        self.button_add_new.pack(padx=3, pady=3)
        self.button_add_new.bind('<ButtonRelease-1>', self.add_new_annotator)

        # Start/Continue Annotating
        # TODO: Depending on the config and annotations folder change the text to "Continue"
        self.button3 = Button(self.lastframe, text="Start", wraplength=80)
        self.button3.pack(padx=3, pady=3)
        self.button3.bind('<ButtonRelease-1>', self.check_if_start)

        # TODO: Add option to have folders per subject in the frames folder

    def add_new_annotator(self, event):
        max_len = 15
        new_annotator = simpledialog.askstring("New Annotator", "Enter the name/alias of the new annotator:")
        if new_annotator is None:
            return
        new_annotator = new_annotator.strip()
        while len(new_annotator) == 0 or len(new_annotator) > max_len:
            messagebox.showerror("Error", message="Annotator name cannot be empty!" if len(new_annotator) == 0 else
                                 f"Annotator name should be less than {max_len} characters")
            new_annotator = simpledialog.askstring("New Annotator", "Enter the name/alias of the new annotator:")
            if new_annotator is None:
                return
            new_annotator = new_annotator.strip()
        if new_annotator in self.annotators:
            messagebox.showerror("Error", message="Annotator already exists, select it from the dropdown menu!")
        self.annotators.append(new_annotator)
        self.selected_annotator.set(new_annotator)
        # destroy previously created ones:
        self.annotator_dropdown.destroy()
        self.button_add_new.destroy()
        # recreate new ones:
        self.annotator_dropdown = OptionMenu(self.rightframe, self.selected_annotator, *self.annotators)
        self.annotator_dropdown.pack(padx=3, pady=3)
        self.button_add_new = Button(self.rightframe, text="Add New", wraplength=80)
        self.button_add_new.pack(padx=3, pady=3)
        self.button_add_new.bind('<ButtonRelease-1>', self.add_new_annotator)

    def selecting_folder(self, event):
        selected_dir = filedialog.askdirectory()
        if event.widget.master == self.leftframe:
            self.check_frames_dir(selected_dir)
            selected_dir = self.frames_dir
        if event.widget.master == self.midframe:
            self.check_annot_dir(selected_dir)
            selected_dir = self.annot_dir
        if selected_dir != '':
            event.widget.config(text=selected_dir)
        else:
            event.widget.config(text="Select Folder")

    def check_frames_dir(self, frames_dir):
        # Check if folder exists
        if frames_dir != '' and not os.path.exists(frames_dir):
            self.frames_dir = ''
            messagebox.showerror("Path Error", message="Folder doesn't exist!")
            return False
        # TODO: Check if there are frames in the folder!
        self.frames_dir = frames_dir
        return True

    def check_annot_dir(self, annot_dir):
        if annot_dir != '' and not os.path.exists(annot_dir):
            self.annot_dir = ''
            messagebox.showerror("Path Error", message="Folder doesn't exist!")
            return False
        # TODO: Check if there are any annotations in the folder!
        # TODO: Check if annotations match with any of the frames in the frames folder!
        self.annot_dir = annot_dir
        return True

    def check_if_start(self, event):
        self.check_frames_dir(self.frames_dir)
        self.check_annot_dir(self.annot_dir)
        # TODO: if everything is all set write a config file for loading the same settings
        # TODO: Write config for each annotator separately
        self.write_config()
        self.leftframe.destroy()
        self.midframe.destroy()
        self.rightframe.destroy()
        self.lastframe.destroy()
        AnnotationWindow(self.win, self.frames_dir, self.annot_dir)

    def write_config(self):
        # TODO: check if different than current config
        pass


class AnnotationWindow:
    def __init__(self, win, frames_dir, annot_dir):
        self.win = win

        self.leftframe = LabelFrame(win, text="Frames Folder", padx=5, pady=5)
        self.leftframe.grid(row=0, column=0, sticky="en")
        self.midframe = LabelFrame(win, text="Annotations Folder", bg="yellow", padx=5, pady=5)
        self.midframe.grid(row=0, column=1, sticky="en")
        self.rightframe = LabelFrame(win, text="Annotating", padx=5, pady=5)
        self.rightframe.grid(row=0, column=2, sticky="en")

        annotate_all(frames_dir, annot_dir)
