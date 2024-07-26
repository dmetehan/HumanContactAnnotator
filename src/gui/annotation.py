import os.path
import configparser
from tkinter import simpledialog, Label, IntVar, StringVar, OptionMenu, LabelFrame, Button, Checkbutton, filedialog, messagebox

from src.backend.annotate import annotate_all


class InitAnnotationWindow:
    def __init__(self, win):
        self.win = win
        self.config_dir = "configs"

        self.leftframe = LabelFrame(win, text="Annotator Name", padx=5, pady=5)
        self.leftframe.grid(row=0, column=0, sticky="en")
        self.midframe = LabelFrame(win, text="Frames Folder", padx=5, pady=5)
        self.midframe.grid(row=0, column=1, sticky="en")
        self.rightframe = LabelFrame(win, text="Annotations Folder", padx=5, pady=5)
        self.rightframe.grid(row=0, column=2, sticky="en")
        self.lastframe = LabelFrame(win, text="Annotating", padx=5, pady=5)
        self.lastframe.grid(row=0, column=3, sticky="en")

        # Annotator selection drop down
        self.button_add_new = Button(self.leftframe, text="Add New", wraplength=80)
        self.button_add_new.pack(padx=3, pady=3)
        self.button_add_new.bind('<ButtonRelease-1>', self.add_new_annotator)
        self.annotators = self.get_annotators()
        self.selected_annotator = StringVar()
        self.selected_annotator.set("Select")
        self.annotator_dropdown = OptionMenu(self.leftframe, self.selected_annotator, *self.annotators, command=self.load_config)
        self.annotator_dropdown.pack(padx=3, pady=3)

        # folder selection
        self.frames_dir = ""
        self.button_frames = Button(self.midframe, text="Select Folder", wraplength=80)
        self.button_frames.pack(padx=3, pady=3)
        self.button_frames.bind('<ButtonRelease-1>', self.selecting_folder)

        # option to have folders per subject in the frames folder
        self.subject_based = IntVar()
        self.subject_based_check = Checkbutton(self.midframe, text='Subject Folders', variable=self.subject_based, onvalue=1, offvalue=0)
        self.subject_based_check.pack()

        # Annotation dir
        self.annot_dir = ""
        self.button_annot = Button(self.rightframe, text="Select Folder", wraplength=80)
        self.button_annot.pack(padx=3, pady=3)
        self.button_annot.bind('<ButtonRelease-1>', self.selecting_folder)

        # Start Annotating
        self.button3 = Button(self.lastframe, text="Start", wraplength=80)
        self.button3.pack(padx=3, pady=3)
        self.button3.bind('<ButtonRelease-1>', self.check_if_start)

    def get_annotators(self):
        annotators = []
        for filename in os.listdir(self.config_dir):
            if filename.endswith(".ini"):
                annotators.append(filename[:-4])
        return annotators

    def add_new_annotator(self, event):
        # TODO: Add a check for only alphabetic characters! No digits, no spaces, no symbols!
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
        self.button_add_new = Button(self.leftframe, text="Add New", wraplength=80)
        self.button_add_new.pack(padx=3, pady=3)
        self.button_add_new.bind('<ButtonRelease-1>', self.add_new_annotator)
        self.annotator_dropdown = OptionMenu(self.leftframe, self.selected_annotator, *self.annotators)
        self.annotator_dropdown.pack(padx=3, pady=3)

    def selecting_folder(self, event):
        selected_dir = filedialog.askdirectory()
        if event.widget.master == self.midframe:
            self.set_frames_dir(selected_dir)
            selected_dir = self.frames_dir
        if event.widget.master == self.rightframe:
            self.set_annot_dir(selected_dir)
            selected_dir = self.annot_dir
        if selected_dir != '':
            event.widget.config(text=selected_dir)
        else:
            event.widget.config(text="Select Folder")

    def set_frames_dir(self, frames_dir):
        # Check if folder exists
        if frames_dir != '' and not os.path.exists(frames_dir):
            self.frames_dir = ''
            messagebox.showerror("Path Error", message="Frames folder doesn't exist!")
        else:
            self.frames_dir = frames_dir

    def check_frames_dir(self):
        # Check if folder exists
        if self.frames_dir != '' and not os.path.exists(self.frames_dir):
            self.frames_dir = ''
            messagebox.showerror("Path Error", message="Frames folder doesn't exist!")
            return False
        elif self.frames_dir == '':
            messagebox.showerror("Path Error", message="Frames folder not selected!")
            return False
        if self.subject_based.get():
            check_subject_folders = False
            # Check if there are folders for subjects in the folder if the subject based option is selected!
            for subject in os.listdir(self.frames_dir):
                if os.path.isdir(os.path.join(self.frames_dir,subject)):
                    check_subject_folders = True
                    # Check if there are frames in one of the subject folders!
                    for filename in os.listdir(os.path.join(self.frames_dir, subject)):
                        if filename.endswith((".jpg", ".jpeg", ".png")):
                            return True
            if check_subject_folders:
                messagebox.showerror("Path Error", message="Subject folders inside the frames folder don't have any frames in them!")
            else:
                messagebox.showerror("Path Error", message="Frames folder doesn't have any folders for subjects!\n"
                                                           "Select a folder with subfolders for subject based annotating\n"
                                                           "or uncheck the Subject Folders checkbox for no subfolders")
        else:
            # Check if there are frames in the folder!
            for filename in os.listdir(self.frames_dir):
                if filename.endswith((".jpg", ".jpeg", ".png")):
                    return True
            messagebox.showerror("Path Error", message="Frames folder doesn't have any frames in it!\n"
                                                       "Select a folder with frames in it or\n"
                                                       "check the Subject Folders checkbox for subfolders.")
        return False

    def set_annot_dir(self, annot_dir):
        if annot_dir != '' and not os.path.exists(annot_dir):
            self.annot_dir = ''
            messagebox.showerror("Path Error", message="Annotations folder doesn't exist!")
        else:
            self.annot_dir = annot_dir

    def check_annot_dir(self):
        if self.annot_dir != '' and not os.path.exists(self.annot_dir):
            self.annot_dir = ''
            messagebox.showerror("Path Error", message="Annotations folder doesn't exist!")
            return False
        elif self.annot_dir == '':
            messagebox.showerror("Path Error", message="Annotations folder not selected!")
            return False
        return True

    def check_annotator(self):
        if self.selected_annotator.get() == "Select":
            messagebox.showerror("Selection Error", message="Annotator not selected!")
            return False
        else:
            return True

    def check_if_start(self, event):
        if not self.check_frames_dir():
            return
        if not self.check_annot_dir():
            return
        if not self.check_annotator():
            return
        # if everything is all set write a config file for loading the same settings in the future
        self.write_config()
        # remove current GUI elements
        self.leftframe.destroy()
        self.midframe.destroy()
        self.rightframe.destroy()
        self.lastframe.destroy()
        # Create the annotation GUI
        AnnotationWindow(self.win, self.frames_dir, self.annot_dir, self.selected_annotator.get())

    def write_config(self):
        os.makedirs(self.config_dir, exist_ok=True)
        # Write config for each annotator separately
        config_path = os.path.join(self.config_dir, f"{self.selected_annotator.get()}.ini")
        config = configparser.ConfigParser()
        # Add sections and key-value pairs
        config['Frames'] = {'folder': self.frames_dir, 'subject_based': self.subject_based.get()}
        config['Annotations'] = {'folder': self.annot_dir, 'annotator': self.selected_annotator.get()}
        # Write the configuration to a file
        with open(config_path, 'w') as configfile:
            config.write(configfile)

    def load_config(self, annotator):
        config_path = os.path.join(self.config_dir, f"{annotator}.ini")
        if os.path.exists(config_path):
            print("Loading previous config file!")
            config = configparser.ConfigParser()
            config.read_file(open(config_path))
            self.frames_dir = config['Frames']['folder']
            self.button_frames.config(text=self.frames_dir)
            if int(config['Frames']['subject_based']):
                self.subject_based_check.select()
            self.annot_dir = config['Annotations']['folder']
            self.button_annot.config(text=self.annot_dir)


class AnnotationWindow:
    def __init__(self, win, frames_dir, annot_dir, annotator):
        self.win = win
        self.win.geometry("570x180")

        self.leftframe = LabelFrame(win, text="Annotation Controls", padx=5, pady=5)
        self.leftframe.grid(row=0, column=0, sticky="en")

        annotation_controls = "<Mouse-Left>: Select region pair\n" \
                              "<Mouse-Right>: Remove region pair\n" \
                              "<Mouse-Mid>: Zoom In/Out on each window\n" \
                              "Y / <Enter>: Accept annotation for the current frame and move to the next frame\n" \
                              "P: Go to the previous frame and annotations to make changes\n" \
                              "R: Copy the previous frame annotations to the current frame. Can be further edited\n" \
                              "Q: Quit the program (doesn't save the annotations for the current frame)"
        label = Label(self.leftframe, text=annotation_controls, font='Calibri 12')
        label.pack()

        win.update()

        completed = annotate_all(frames_dir, annot_dir, annotator)
        if completed:
            messagebox.showinfo(title="Completed!", message="Annotation completed!")
        win.destroy()
