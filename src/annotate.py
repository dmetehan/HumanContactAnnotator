import os
from json import JSONDecodeError

import cv2
import json
import numpy as np


class Annotator:

    def __init__(self):
        self.MASK_COARSE_DIR = 'data/region_masks'
        self.N_COARSE = 21
        # TODO: Add option to rename people to the GUI
        self.PERSON = ['adult', 'child']
        self.annot_scale = {self.PERSON[0]: 1, self.PERSON[1]: 0.5, 'frame': 0.5}
        self.frame = cv2.imread('data/region_masks/rid_base.png')  # dummy frame for warnings!
        # TODO: Check if rid_base exists and show an error if not!
        self.sketches = {pers: cv2.imread('data/region_masks/rid_base.png') for pers in self.PERSON}
        self.selected_regions = []
        self.regions_per_person = {self.PERSON[0]: [], self.PERSON[1]: []}
        self.hlighted_regions = {self.PERSON[0]: [], self.PERSON[1]: []}
        self.remove_pair = {self.PERSON[0]: -1, self.PERSON[1]: -1}
        # TODO: Maybe add option for multiple views - needs some adjustments with folders
        self.camera = 1
        self.mask_index = self.create_mask_index()

    def create_mask_index(self):
        mask_ind = {pers: np.zeros_like(cv2.imread(f'data/region_masks/rid_base.png', 0)) for pers in self.PERSON}
        for pers in self.PERSON:
            for rid in range(self.N_COARSE):
                mask = cv2.imread(f'{self.MASK_COARSE_DIR}/rid_{rid}.png', 0)
                mask_ind[pers][mask < 100] = rid + 1
        return mask_ind

    def light_up(self, img, person):
        other_person = self.PERSON[1 - self.PERSON.index(person)]
        img_cpy = img.copy()
        for regions in self.selected_regions:
            if regions[person] != -1:
                img_cpy[self.mask_index[person] == (regions[person] + 1)] = regions['color']
        if self.remove_pair[person] != -1:
            img_cpy[self.mask_index[person] == (self.remove_pair[person] + 1)] = (0, 0, 175)
        else:
            if len(self.hlighted_regions[person]) > 0:
                for region in self.hlighted_regions[person]:
                    img_cpy[self.mask_index[person] == (region + 1)] = (0, 175, 0)
        if len(self.hlighted_regions[other_person]) > 0 or len(self.hlighted_regions[person]) > 0:
            for i in range(21):
                if i != self.remove_pair[person] and i not in self.hlighted_regions[person] and \
                        any([region[person] == i for region in self.selected_regions]):
                    img_cpy[self.mask_index[person] == (i + 1)] = (0, 25, 0)
        return img_cpy

    def imshow(self, window, img, scale, person=None):
        if person:
            img = self.light_up(img, person)
        width = int(img.shape[1] * scale)
        height = int(img.shape[0] * scale)
        dim = (width, height)
        cv2.imshow(window, cv2.resize(img, dim, interpolation=cv2.INTER_AREA))
        # cv2.moveWindow(window, 40, 30)

    def highlight(self, x, y, param):
        person = param[0]
        other_person = self.PERSON[1 - self.PERSON.index(person)]
        scale = self.annot_scale[person]
        other_scale = self.annot_scale[other_person]
        try:
            m = self.mask_index[person][int(round(y / scale)), int(round(x / scale))]
        except IndexError:
            return
        if len(self.selected_regions) > 0 and self.selected_regions[-1][person] == -1 and \
                self.selected_regions[-1][other_person] != -1:
            self.hlighted_regions[person] = [m - 1] if m > 0 else []
        elif len(self.selected_regions) > 0 and self.selected_regions[-1][other_person] == -1 and \
                self.selected_regions[-1][person] != -1:
            self.hlighted_regions[person] = [self.selected_regions[-1][person]]
        else:
            if self.remove_pair[person] != -1:
                self.hlighted_regions[person] = [self.remove_pair[person]]
                self.hlighted_regions[other_person] = [region[other_person] for region in self.selected_regions
                                                       if (region[person] == self.remove_pair[person])]
            elif self.remove_pair[other_person] != -1:
                self.hlighted_regions[other_person] = [self.remove_pair[other_person]]
                self.hlighted_regions[person] = [region[person] for region in self.selected_regions
                                                 if (region[other_person] == self.remove_pair[other_person])]
            else:
                self.hlighted_regions[person] = [m - 1] if m > 0 else []
                self.hlighted_regions[other_person] = [region[other_person] for region in self.selected_regions
                                                       if (region[person] == m - 1 and region[other_person] != -1)]
        self.imshow(person, self.sketches[person], scale, person)
        self.imshow(other_person, self.sketches[other_person], other_scale, other_person)

    def already_selected(self, reg_pair_cand):
        person, other_person = reg_pair_cand.keys()
        for regions in self.selected_regions:
            if regions[person] == reg_pair_cand[person] and regions[other_person] == reg_pair_cand[other_person]:
                return True
        return False

    def left_click(self, x, y, param):
        # add annotation
        person = param[0]
        other_person = self.PERSON[1 - self.PERSON.index(person)]
        scale = self.annot_scale[person]
        m = int(self.mask_index[person][int(round(y / scale)), int(round(x / scale))])
        if m > 0:
            if len(self.selected_regions) > 0 and -1 in self.selected_regions[-1].values():
                if self.selected_regions[-1][person] == -1:
                    if self.already_selected({other_person: self.selected_regions[-1][other_person], person: m - 1}):
                        print("This region combination is already annotated.")
                        self.regions_per_person[other_person].remove(self.selected_regions[-1][other_person])
                        self.selected_regions[-1][other_person] = -1
                    else:
                        self.selected_regions[-1][person] = m - 1
                        self.regions_per_person[person].insert(0, m - 1)
                else:
                    print(f"Already a region from '{person}' is selected. De-select it by right clicking on it or select "
                          f"a region from the other person to continue.")
            else:
                self.selected_regions.append({self.PERSON[0]: -1, self.PERSON[1]: -1,
                                              'color': tuple(np.random.randint(0, 255) for _ in range(3))})
                self.selected_regions[-1][person] = m - 1
                self.regions_per_person[person].insert(0, m - 1)
        self.imshow(person, self.sketches[person], self.annot_scale[person], person)
        self.remove_pair = {self.PERSON[0]: -1, self.PERSON[1]: -1}

    def right_click(self, x, y, param):
        # remove annotation
        person = param[0]
        other_person = self.PERSON[1 - self.PERSON.index(person)]
        scale = self.annot_scale[person]
        m = int(self.mask_index[person][int(round(y / scale)), int(round(x / scale))])
        if m > 0:
            if len(self.selected_regions) > 0:
                if self.selected_regions[-1][person] == m - 1 and self.selected_regions[-1][other_person] == -1:
                    self.selected_regions[-1][person] = -1
                    self.remove_pair = {self.PERSON[0]: -1, self.PERSON[1]: -1}
                else:
                    if m - 1 not in self.regions_per_person[person]:
                        print('This region is not selected yet!')
                    else:
                        if self.remove_pair[person] == -1:
                            if self.remove_pair[other_person] == -1:
                                print('Region added to remove pair! Right click on it to undo the selection!')
                                self.remove_pair[person] = m - 1
                                if self.selected_regions[-1][person] == -1 or self.selected_regions[-1][other_person] == -1:
                                    # deselecting the previous selection
                                    self.selected_regions[-1][person] = -1
                                    self.selected_regions[-1][other_person] = -1
                            else:
                                matching_regions = []
                                for regions in self.selected_regions:
                                    if regions[other_person] == self.remove_pair[other_person]:
                                        matching_regions.append(regions[person])
                                print(self.selected_regions)
                                print(matching_regions)
                                if m - 1 not in matching_regions:
                                    print('The pair is not selected. Remove pair is reinitialized with the new selection.')
                                    self.remove_pair = {person: m - 1, other_person: -1}
                                else:
                                    self.remove_pair[person] = m - 1
                        else:
                            if self.remove_pair[person] == m - 1:
                                print("Remove selection is cleared!")
                                self.remove_pair[person] = -1
                            else:
                                print('Previous remove selection is replaced by the new region selection!')
                                self.remove_pair[person] = m - 1

                        if self.remove_pair[self.PERSON[0]] != -1 and self.remove_pair[self.PERSON[1]] != -1:
                            r = 0
                            for regions in self.selected_regions:
                                if regions[self.PERSON[0]] == self.remove_pair[self.PERSON[0]] and \
                                        regions[self.PERSON[1]] == self.remove_pair[self.PERSON[1]]:
                                    break
                                else:
                                    r += 1
                            self.selected_regions.pop(r)
                            self.regions_per_person[self.PERSON[0]].remove(self.remove_pair[self.PERSON[0]])
                            self.regions_per_person[self.PERSON[1]].remove(self.remove_pair[self.PERSON[1]])
                            self.remove_pair = {self.PERSON[0]: -1, self.PERSON[1]: -1}
                            print('Removed the region from the annotation!')
            else:
                print('No region is selected yet.')
        self.imshow(person, self.sketches[person], self.annot_scale[person], person)

    def zoom(self, flags, param):
        person = param[0]
        scale = self.annot_scale[person]
        if flags > 0:  # scroll wheel up
            scale += 0.1
            if scale > 2.5:  # zoom factor adjustment
                scale = 2.5
        else:  # scroll wheel down
            scale -= 0.1
            if scale < 0.3:  # zoom factor adjustment
                scale = 0.3
        self.annot_scale[person] = scale
        if person != 'frame':
            self.imshow(person, self.sketches[person], self.annot_scale[person], person)
        else:
            self.imshow(person, self.frame, self.annot_scale[person])

    def annot_callbacks(self, event, x, y, flags, param):
        if event == cv2.EVENT_RBUTTONUP:
            if param[0] != 'frame':
                self.right_click(x, y, param)
            else:
                camera = min(4, self.camera + 1)
        if event == cv2.EVENT_LBUTTONUP:
            if param[0] != 'frame':
                self.left_click(x, y, param)
            else:
                camera = max(1, self.camera - 1)
        if param[0] != 'frame' and event == cv2.EVENT_MOUSEMOVE:
            self.highlight(x, y, param)
        if event == cv2.EVENT_MOUSEWHEEL:  # scroll wheel
            self.zoom(flags, param)

    def init_image(self, i_cf, img_dir, contact_frames):
        # starting a new annotation for the new frame
        self.selected_regions = []
        self.regions_per_person = {self.PERSON[0]: [], self.PERSON[1]: []}
        self.hlighted_regions = {self.PERSON[0]: [], self.PERSON[1]: []}
        self.remove_pair = {self.PERSON[0]: -1, self.PERSON[1]: -1}
        self.frame = cv2.imread(os.path.join(img_dir, contact_frames[i_cf]))
        self.imshow('frame', self.frame, self.annot_scale['frame'])
        self.imshow(self.PERSON[0], self.sketches[self.PERSON[0]], self.annot_scale[self.PERSON[0]])
        self.imshow(self.PERSON[1], self.sketches[self.PERSON[1]], self.annot_scale[self.PERSON[1]])

    def get_prev_annot(self, annot_regions):
        if annot_regions != "ambiguous":
            selected_regions = annot_regions.copy()
            for regions in selected_regions:
                for person in self.PERSON:
                    self.regions_per_person[person].insert(0, regions[person])

    def annotate(self, subject, root_dir, all_frames, sig_annot_dir):
        # create_windows
        # create callbacks: 1) select 2) highlight 3) zoom 4) switch between views 5) next/previous
        # 0: quit annotating,
        # 1: continue annotating and save the json file,
        # 2: continue annotating and no save is needed.
        response = 2
        sig_annot = {}
        sig_annot_file = os.path.join(sig_annot_dir, f'{subject}.json')
        i_cf = 0
        if os.path.exists(sig_annot_file):
            # Read previously saved annotation file to continue from it.
            print(f"The file {sig_annot_file} exists, loading the previous annotations.")
            with open(sig_annot_file, 'r') as f:
                try:
                    sig_annot = json.load(f)
                except JSONDecodeError:
                    sig_annot = {}
            for frame_name in sig_annot:
                if frame_name == all_frames[i_cf]:
                    i_cf += 1
                else:
                    raise ValueError(f"There is a problem with frame order in {sig_annot_file}")
        if i_cf >= len(all_frames):
            return response, sig_annot
        # TODO: Option for subject based foldering and cameras
        # img_dir = os.path.join(root_dir, subject, f'cam{self.camera}')
        img_dir = root_dir
        frame = cv2.imread(os.path.join(img_dir, all_frames[i_cf]))
        self.imshow('frame', frame, self.annot_scale['frame'])
        self.imshow(self.PERSON[0], self.sketches[self.PERSON[0]], self.annot_scale[self.PERSON[0]])
        self.imshow(self.PERSON[1], self.sketches[self.PERSON[1]], self.annot_scale[self.PERSON[1]])
        cv2.setMouseCallback('frame', self.annot_callbacks, ['frame'])
        cv2.setMouseCallback(self.PERSON[0], self.annot_callbacks, [self.PERSON[0]])
        cv2.setMouseCallback(self.PERSON[1], self.annot_callbacks, [self.PERSON[1]])
        self.init_image(i_cf, img_dir, all_frames)
        while i_cf < len(all_frames):
            response = 1
            key = cv2.waitKey(5)
            if key == ord('q') or key == ord('Q'):
                response = 0
                break
            elif key == ord('y') or key == ord('Y') or key == ord('a') or key == ord('A') or key == 13:  # enter
                if key == ord('a') or key == ord('A'):
                    # ambiguous
                    print("Annotated for ambiguous!")
                    sig_annot[all_frames[i_cf]] = 'ambiguous'
                else:
                    if len(self.selected_regions) > 0 and -1 in self.selected_regions[-1].values():
                        print("WARNING! You left the last selected incomplete, saving without the last selection!")
                        self.selected_regions.pop()  # removing incomplete annotation
                    print(f'Accepted annotation for {subject}/{all_frames[i_cf]} ({i_cf+1}/{len(all_frames)}): '
                          f'{self.selected_regions}')
                    # TODO: Get rid of writing the color into the annotation json
                    sig_annot[all_frames[i_cf]] = self.selected_regions.copy()
                # Save annotation dictionary for subject
                with open(sig_annot_file, 'w') as f:
                    json.dump(sig_annot, f)
                # to the next image
                i_cf += 1
                if i_cf >= len(all_frames):
                    break
                self.init_image(i_cf, img_dir, all_frames)
                if all_frames[i_cf] in sig_annot:
                    self.get_prev_annot(sig_annot[all_frames[i_cf]])
            elif key == ord('p') or key == ord('P'):
                # previous annotations
                i_cf -= 1
                if i_cf < 0:
                    raise ValueError("index went lower than zero!")
                self.init_image(i_cf, img_dir, all_frames)
                self.get_prev_annot(sig_annot[all_frames[i_cf]])
                print(f'Previous annotation for {subject}/{all_frames[i_cf]} ({i_cf}/{len(all_frames)}): '
                      f'{self.selected_regions}')
            elif key == ord('1'):
                self.camera = 1
            elif key == ord('2'):
                self.camera = 2
            elif key == ord('3'):
                self.camera = 3
            elif key == ord('4'):
                self.camera = 4
            elif key == ord('r') or key == ord('R') or key == ord('-'):
                print("Copying last annotations!")
                self.init_image(i_cf, img_dir, all_frames)
                self.get_prev_annot(sig_annot[all_frames[i_cf - 1]])
            # TODO: Option for subject and camera
            # img_dir = os.path.join(root_dir, subject, f'cam{self.camera}')
            img_dir = root_dir
            self.frame = cv2.imread(os.path.join(img_dir, all_frames[i_cf]))
            self.imshow('frame', frame, self.annot_scale['frame'])
        cv2.destroyAllWindows()
        return response, sig_annot


def annotate_all(root_dir, sig_annot_dir):
    subject = os.path.dirname(root_dir)  # folder name is the subject name
    # Supports files with .jpg, .jpeg, and .png format
    all_frames = [filename for filename in os.listdir(root_dir) if filename.endswith((".jpg", ".jpeg", ".png"))]
    annotator_obj = Annotator()
    response, sig_annot = annotator_obj.annotate(subject, root_dir, all_frames, sig_annot_dir)
    # Save annotation dictionary for subject
    if response != 2 and len(sig_annot) > 0:
        print(f"Saving annotation for {subject}!")
        with open(os.path.join(sig_annot_dir, f'{subject}.json'), 'w') as f:
            json.dump(sig_annot, f)
    if response == 0:
        print("response 0")  # maybe useful for subject based annotation


def main():
    root_dir = r"C:\Users\Doyra001\GithubRepos\contact-annotator\pci_frames\all"
    sig_annot_dir = r"C:\Users\Doyra001\GithubRepos\contact-signature-annotator\annotations\signature\all"
    annotate_all(root_dir, sig_annot_dir)


if __name__ == '__main__':
    main()
