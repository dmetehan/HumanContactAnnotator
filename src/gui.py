import os.path
from tkinter import Frame, Label, LabelFrame, Button, N, LEFT, RIGHT, TOP, BOTTOM, BOTH, filedialog, messagebox


class InitWindow:
    def __init__(self, win):
        # TODO: read configuration including previously selected folder, annotator, output directory
        self.win = win

        self.leftframe = LabelFrame(win, padx=5, pady=5)
        self.leftframe.grid(row=0, column=0)
        self.midframe = LabelFrame(win, bg="yellow", padx=5, pady=5)
        self.midframe.grid(row=0, column=1)
        self.rightframe = LabelFrame(win, padx=5, pady=5)
        self.rightframe.grid(row=0, column=2)

        # folder selection
        self.frames_dir = ""
        self.label1 = Label(self.leftframe, text="Frames Folder")
        self.label1.pack(padx=3, pady=3)
        self.button1 = Button(self.leftframe, text="Select Folder", wraplength=80)
        self.button1.pack(padx=3, pady=3)
        self.button1.bind('<ButtonRelease-1>', self.selecting_folder)

        # Annotation dir
        self.annot_dir = ""
        self.label2 = Label(self.midframe, text="Annotations Folder")
        self.label2.pack(padx=3, pady=3)
        self.button2 = Button(self.midframe, text="Select Folder", wraplength=80)
        self.button2.pack(padx=3, pady=3)
        self.button2.bind('<ButtonRelease-1>', self.selecting_folder)

        # Start/Continue Annotating
        # TODO: Depending on the config and annotations folder change the text to "Continue"
        self.button3 = Button(self.rightframe, text="Start Annotating", wraplength=80)
        self.button3.pack(padx=3, pady=3)
        self.button3.bind('<ButtonRelease-1>', self.check_if_start)

        # TODO: Annotator selection drop down

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
        self.leftframe.destroy()
        self.midframe.destroy()
        self.rightframe.destroy()
        AnnotationWindow(self.win)


class AnnotationWindow:
    def __init__(self, win):
        self.leftframe = LabelFrame(win, padx=5, pady=5)
        self.leftframe.grid(row=0, column=0)
        self.midframe = LabelFrame(win, bg="yellow", padx=5, pady=5)
        self.midframe.grid(row=0, column=1)
        self.rightframe = LabelFrame(win, padx=5, pady=5)
        self.rightframe.grid(row=0, column=2)
