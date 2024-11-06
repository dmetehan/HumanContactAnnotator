import os
from tkinter import Button, Label, LabelFrame, messagebox, filedialog, IntVar, Checkbutton

from src.backend.interannotator_agreement import agreement_for_all_annotator_pairs, read_annotations


class InterannotatorWindow:
    def __init__(self, win):
        self.win = win
        self.win.geometry("300x200+50+50")

        self.leftframe = LabelFrame(win, text="Annotations Folder", padx=5, pady=5)
        self.leftframe.grid(row=0, column=0, sticky="en")
        self.midframe = LabelFrame(self.win, text="Annotators", padx=5, pady=5)
        self.midframe.grid(row=0, column=1, sticky="en")
        self.rightframe = LabelFrame(self.win, text="Agreement", padx=5, pady=5)
        self.rightframe.grid(row=0, column=2, sticky="en")

        # Annotation dir
        self.annot_dir = ""
        self.button_annot = Button(self.leftframe, text="Select Folder", wraplength=80)
        self.button_annot.pack(padx=3, pady=3)
        self.button_annot.bind('<ButtonRelease-1>', self.selecting_folder)
        # TODO: Make sure to implement subject based option as well

        win.update()

    def create_checkboxes_for_annotators(self):
        print("create checkboxes")
        self.midframe.destroy()
        self.rightframe.destroy()
        self.midframe = LabelFrame(self.win, text="Annotators", padx=5, pady=5)
        self.midframe.grid(row=0, column=1, sticky="en")
        max_annotated_frames = 0
        annotators = {}
        for filename in os.listdir(self.annot_dir):
            # TODO: Fix the bug that can be caused by having annotations for
            #  different folders in the same annotations directory!
            if filename.endswith(".json"):
                cur_annots = read_annotations(os.path.join(self.annot_dir, filename))
                if len(cur_annots['default']) > max_annotated_frames:
                    max_annotated_frames = len(cur_annots['default'])
                elif len(cur_annots['default']) < max_annotated_frames:
                    continue  # do not take into account unfinished annotations
                cur_annotator = filename.split("_")[0]
                if cur_annotator not in annotators:
                    annotators[cur_annotator] = len(cur_annots['default'])
        valid_annotators = []
        for cur_annotator in annotators:
            if annotators[cur_annotator] == max_annotated_frames:
                valid_annotators.append(cur_annotator)
        self.annotator_selection = {cur_annotator: IntVar() for cur_annotator in valid_annotators}
        self.annotator_checkboxes = {cur_annotator: Checkbutton(self.midframe, text=cur_annotator,
                                                                variable=self.annotator_selection[cur_annotator],
                                                                onvalue=1, offvalue=0)
                                     for cur_annotator in valid_annotators}
        for _, checkbox in self.annotator_checkboxes.items():
            checkbox.pack()
            checkbox.select()
        self.button_check_all = Button(self.midframe, text="Check all", wraplength=80)
        self.button_check_all.pack(padx=3, pady=3)
        self.button_check_all.bind('<ButtonRelease-1>', self.check_all)
        self.button_uncheck_all = Button(self.midframe, text="Uncheck all", wraplength=80)
        self.button_uncheck_all.pack(padx=3, pady=3)
        self.button_uncheck_all.bind('<ButtonRelease-1>', self.uncheck_all)

        # Right frame
        self.rightframe = LabelFrame(self.win, text="Agreement", padx=5, pady=5)
        self.rightframe.grid(row=0, column=2, sticky="en")
        self.button_calculate = Button(self.rightframe, text="Calculate", wraplength=80)
        self.button_calculate.pack(padx=3, pady=3)
        self.button_calculate.bind('<ButtonRelease-1>', self.calc_agreement)

        self.win.update()

    def calc_agreement(self, _):
        # check if at least two annotators are selected
        if sum([selected.get() for selected in self.annotator_selection.values()]) < 2:
            messagebox.showerror("Selection Error", message="You must select at least two annotators!")
            return
        # TODO: Check if all the selected annotators have annotated all the frames!

        # TODO: Check if multiple annotations exist for the annotators (different subject names etc.)

        self.leftframe.destroy()
        self.midframe.destroy()
        self.rightframe.destroy()
        selected_annotators = [annotator for annotator, selected in self.annotator_selection.items() if selected.get()]
        seg_results, sig_results = agreement_for_all_annotator_pairs(selected_annotators, self.annot_dir)
        AgreementRankingWindow(self.win, seg_results, sig_results)

    def check_all(self, _):
        for _, checkbox in self.annotator_checkboxes.items():
            checkbox.select()

    def uncheck_all(self, _):
        for _, checkbox in self.annotator_checkboxes.items():
            checkbox.deselect()

    def selecting_folder(self, event):
        selected_dir = filedialog.askdirectory()
        self.set_annot_dir(selected_dir)
        if self.annot_dir != '':
            event.widget.config(text=self.annot_dir)
            self.create_checkboxes_for_annotators()
        else:
            event.widget.config(text="Select Folder")

    def set_annot_dir(self, annot_dir):
        if annot_dir != '' and not os.path.exists(annot_dir):
            self.annot_dir = ''
            messagebox.showerror("Path Error", message="Annotations folder doesn't exist!")
        else:
            self.annot_dir = annot_dir


class AgreementRankingWindow:
    def __init__(self, win, segmentation_results, signature_results):
        self.win = win
        self.win.geometry("300x200+50+50")

        self.leftframe = LabelFrame(win, text="Results", padx=5, pady=5)
        self.leftframe.grid(row=0, column=0, sticky="en")

        output = self.convert_results_to_text(segmentation_results, signature_results)
        label = Label(self.leftframe, text=output, font='Calibri 12')
        label.pack()

        # Annotation dir
        # self.annot_dir = ""
        # self.button_annot = Button(self.leftframe, text="New Calculation", wraplength=80)
        # self.button_annot.pack(padx=3, pady=3)
        # self.button_annot.bind('<ButtonRelease-1>', self.go_back)

        win.update()

    def convert_results_to_text(self, seg_results, sig_results):
        output = '\tSegmentation\tSignature\n'
        sorted_seg = dict(sorted(seg_results.items(), key=lambda item: item[1][0], reverse=True))
        for annotator in sorted_seg:
            output += f'{annotator}\t{seg_results[annotator][0]:.3f} ({seg_results[annotator][1]:.3f})' \
                      f'\t{sig_results[annotator][0]:.3f} ({sig_results[annotator][1]:.3f})\n'
        return output
