from tkinter import Frame, Label, LabelFrame, Button, LEFT, RIGHT, TOP, BOTTOM, BOTH, filedialog


class InitWindow:
    def __init__(self, win):
        self.leftframe = LabelFrame(win, bg="green", padx=15, pady=15)
        self.leftframe.grid(row=0, column=0)
        self.rightframe = LabelFrame(win, bg="yellow", padx=15, pady=15)
        self.rightframe.grid(row=0, column=1)

        self.label1 = Label(self.leftframe, text="Frames Folder")
        self.label1.pack(padx=3, pady=3)
        self.button2 = Button(self.rightframe, text="Select Folder")
        self.button2.pack(padx=3, pady=3)
        self.folder_path = ""
        self.button2.bind('<Button-1>', self.selecting_folder)

        self.button3 = Button(self.leftframe, text="Button1")
        self.button3.pack(padx=3, pady=3)
        self.button4 = Button(self.rightframe, text="Button2")
        self.button4.pack(padx=3, pady=3)

    def selecting_folder(self, event):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path != '':
            self.button2.config(text=self.folder_path)
        else:
            self.button2.config(text="Select Folder")

