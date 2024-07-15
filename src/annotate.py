import os
from collections import defaultdict
from json import JSONDecodeError
from typing import List

import cv2
import json
import numpy as np
import pandas as pd


MASK_FINE_DIR = 'masks_finegrained'
N_FINE = 75
MASK_COARSE_DIR = 'masks_coarse_clear'
N_COARSE = 21
PERSON = ['adult', 'child']
annot_scale = {PERSON[0]: 1, PERSON[1]: 0.5, 'frame': 0.5}
frame = cv2.imread('rid_base.png')  # dummy frame for warnings!
sketches = {pers: cv2.imread('rid_base.png') for pers in PERSON}
selected_regions = []
regions_per_person = {PERSON[0]: [], PERSON[1]: []}
hlighted_regions = {PERSON[0]: [], PERSON[1]: []}
remove_pair = {PERSON[0]: -1, PERSON[1]: -1}
camera = 1


def create_mask_index():
    mask_ind = {pers: np.zeros_like(cv2.imread(f'rid_base.png', 0)) for pers in PERSON}
    for pers in PERSON:
        for rid in range(N_COARSE):
            mask = cv2.imread(f'{MASK_COARSE_DIR}/rid_{rid}.png', 0)
            mask_ind[pers][mask < 100] = rid + 1
    return mask_ind


MASK_INDEX = create_mask_index()


def light_up(img, person):
    global selected_regions, hlighted_regions, remove_pair
    other_person = PERSON[1 - PERSON.index(person)]
    img_cpy = img.copy()
    for regions in selected_regions:
        if regions[person] != -1:
            img_cpy[MASK_INDEX[person] == (regions[person] + 1)] = regions['color']
    if remove_pair[person] != -1:
        img_cpy[MASK_INDEX[person] == (remove_pair[person] + 1)] = (0, 0, 175)
    else:
        if len(hlighted_regions[person]) > 0:
            for region in hlighted_regions[person]:
                img_cpy[MASK_INDEX[person] == (region + 1)] = (0, 175, 0)
    if len(hlighted_regions[other_person]) > 0 or len(hlighted_regions[person]) > 0:
        for i in range(21):
            if i != remove_pair[person] and i not in hlighted_regions[person] and any([region[person] == i for region in selected_regions]):
                img_cpy[MASK_INDEX[person] == (i + 1)] = (0, 25, 0)
    return img_cpy


def imshow(window, img, scale, person=None):
    if person:
        img = light_up(img, person)
    width = int(img.shape[1] * scale)
    height = int(img.shape[0] * scale)
    dim = (width, height)
    cv2.imshow(window, cv2.resize(img, dim, interpolation=cv2.INTER_AREA))
    # cv2.moveWindow(window, 40, 30)


def highlight(x, y, param):
    global selected_regions
    person = param[0]
    other_person = PERSON[1 - PERSON.index(person)]
    scale = annot_scale[person]
    other_scale = annot_scale[other_person]
    try:
        m = MASK_INDEX[person][int(round(y / scale)), int(round(x / scale))]
    except IndexError:
        return
    if len(selected_regions) > 0 and selected_regions[-1][person] == -1 and selected_regions[-1][other_person] != -1:
        hlighted_regions[person] = [m - 1] if m > 0 else []
    elif len(selected_regions) > 0 and selected_regions[-1][other_person] == -1 and selected_regions[-1][person] != -1:
        hlighted_regions[person] = [selected_regions[-1][person]]
    else:
        if remove_pair[person] != -1:
            hlighted_regions[person] = [remove_pair[person]]
            hlighted_regions[other_person] = [region[other_person] for region in selected_regions
                                              if (region[person] == remove_pair[person])]
        elif remove_pair[other_person] != -1:
            hlighted_regions[other_person] = [remove_pair[other_person]]
            hlighted_regions[person] = [region[person] for region in selected_regions
                                        if (region[other_person] == remove_pair[other_person])]
        else:
            hlighted_regions[person] = [m - 1] if m > 0 else []
            hlighted_regions[other_person] = [region[other_person] for region in selected_regions
                                              if (region[person] == m - 1 and region[other_person] != -1)]
    imshow(person, sketches[person], scale, person)
    imshow(other_person, sketches[other_person], other_scale, other_person)


def already_selected(reg_pair_cand):
    global selected_regions
    person, other_person = reg_pair_cand.keys()
    for regions in selected_regions:
        if regions[person] == reg_pair_cand[person] and regions[other_person] == reg_pair_cand[other_person]:
            return True
    return False


def left_click(x, y, param):
    # add annotation
    global selected_regions, regions_per_person, remove_pair
    person = param[0]
    other_person = PERSON[1 - PERSON.index(person)]
    scale = annot_scale[person]
    m = int(MASK_INDEX[person][int(round(y / scale)), int(round(x / scale))])
    if m > 0:
        if len(selected_regions) > 0 and -1 in selected_regions[-1].values():
            if selected_regions[-1][person] == -1:
                if already_selected({other_person: selected_regions[-1][other_person], person: m - 1}):
                    print("This region combination is already annotated.")
                    regions_per_person[other_person].remove(selected_regions[-1][other_person])
                    selected_regions[-1][other_person] = -1
                else:
                    selected_regions[-1][person] = m - 1
                    regions_per_person[person].insert(0, m - 1)
            else:
                print(f"Already a region from '{person}' is selected. De-select it by right clicking on it or select "
                      f"a region from the other person to continue.")
        else:
            selected_regions.append({PERSON[0]: -1, PERSON[1]: -1, 'color': tuple(np.random.randint(0, 255)
                                                                                  for _ in range(3))})
            selected_regions[-1][person] = m - 1
            regions_per_person[person].insert(0, m - 1)
    imshow(person, sketches[person], annot_scale[person], person)
    remove_pair = {PERSON[0]: -1, PERSON[1]: -1}


def right_click(x, y, param):
    # remove annotation
    global selected_regions, regions_per_person, remove_pair
    person = param[0]
    other_person = PERSON[1 - PERSON.index(person)]
    scale = annot_scale[person]
    m = int(MASK_INDEX[person][int(round(y / scale)), int(round(x / scale))])
    if m > 0:
        if len(selected_regions) > 0:
            if selected_regions[-1][person] == m - 1 and selected_regions[-1][other_person] == -1:
                selected_regions[-1][person] = -1
                remove_pair = {PERSON[0]: -1, PERSON[1]: -1}
            else:
                if m - 1 not in regions_per_person[person]:
                    print('This region is not selected yet!')
                else:
                    if remove_pair[person] == -1:
                        if remove_pair[other_person] == -1:
                            print('Region added to remove pair! Right click on it to undo the selection!')
                            remove_pair[person] = m - 1
                            if selected_regions[-1][person] == -1 or selected_regions[-1][other_person] == -1:
                                # deselecting the previous selection
                                selected_regions[-1][person] = -1
                                selected_regions[-1][other_person] = -1
                        else:
                            matching_regions = []
                            for regions in selected_regions:
                                if regions[other_person] == remove_pair[other_person]:
                                    matching_regions.append(regions[person])
                            print(selected_regions)
                            print(matching_regions)
                            if m - 1 not in matching_regions:
                                print('The pair is not selected. Remove pair is reinitialized with the new selection.')
                                remove_pair = {person: m - 1, other_person: -1}
                            else:
                                remove_pair[person] = m - 1
                    else:
                        if remove_pair[person] == m - 1:
                            print("Remove selection is cleared!")
                            remove_pair[person] = -1
                        else:
                            print('Previous remove selection is replaced by the new region selection!')
                            remove_pair[person] = m - 1

                    if remove_pair[PERSON[0]] != -1 and remove_pair[PERSON[1]] != -1:
                        r = 0
                        for regions in selected_regions:
                            if regions[PERSON[0]] == remove_pair[PERSON[0]] and \
                                    regions[PERSON[1]] == remove_pair[PERSON[1]]:
                                break
                            else:
                                r += 1
                        selected_regions.pop(r)
                        regions_per_person[PERSON[0]].remove(remove_pair[PERSON[0]])
                        regions_per_person[PERSON[1]].remove(remove_pair[PERSON[1]])
                        remove_pair = {PERSON[0]: -1, PERSON[1]: -1}
                        print('Removed the region from the annotation!')
        else:
            print('No region is selected yet.')
    imshow(person, sketches[person], annot_scale[person], person)


def zoom(flags, param):
    global annot_scale, frame
    person = param[0]
    scale = annot_scale[person]
    if flags > 0:  # scroll wheel up
        scale += 0.1
        if scale > 2.5:  # zoom factor adjustment
            scale = 2.5
    else:  # scroll wheel down
        scale -= 0.1
        if scale < 0.3:  # zoom factor adjustment
            scale = 0.3
    annot_scale[person] = scale
    if person != 'frame':
        imshow(person, sketches[person], annot_scale[person], person)
    else:
        imshow(person, frame, annot_scale[person])


def annot_callbacks(event, x, y, flags, param):
    global camera
    if event == cv2.EVENT_RBUTTONUP:
        if param[0] != 'frame':
            right_click(x, y, param)
        else:
            camera = min(4, camera + 1)
    if event == cv2.EVENT_LBUTTONUP:
        if param[0] != 'frame':
            left_click(x, y, param)
        else:
            camera = max(1, camera - 1)
    if param[0] != 'frame' and event == cv2.EVENT_MOUSEMOVE:
        highlight(x, y, param)
    if event == cv2.EVENT_MOUSEWHEEL:  # scroll wheel
        zoom(flags, param)


def init_image(i_cf, img_dir, contact_frames):
    global selected_regions, regions_per_person, hlighted_regions, remove_pair, frame
    # starting a new annotation for the new frame
    selected_regions = []
    regions_per_person = {PERSON[0]: [], PERSON[1]: []}
    hlighted_regions = {PERSON[0]: [], PERSON[1]: []}
    remove_pair = {PERSON[0]: -1, PERSON[1]: -1}
    frame = cv2.imread(os.path.join(img_dir, contact_frames[i_cf]))
    imshow('frame', frame, annot_scale['frame'])
    imshow(PERSON[0], sketches[PERSON[0]], annot_scale[PERSON[0]])
    imshow(PERSON[1], sketches[PERSON[1]], annot_scale[PERSON[1]])


def get_prev_annot(annot_regions):
    global selected_regions, regions_per_person
    if annot_regions != "ambiguous":
        selected_regions = annot_regions.copy()
        for regions in selected_regions:
            for person in PERSON:
                regions_per_person[person].insert(0, regions[person])


def annotate(subject, root_dir, contact_frames, sig_annot_dir):
    # create_windows
    # create callbacks: 1) select 2) highlight 3) zoom 4) switch between views 5) next/previous
    global selected_regions, regions_per_person, hlighted_regions, remove_pair, frame, camera
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
            if frame_name == contact_frames[i_cf]:
                i_cf += 1
            else:
                raise ValueError(f"There is a problem with frame order in {sig_annot_file}")
    if i_cf >= len(contact_frames):
        return response, sig_annot
    img_dir = os.path.join(root_dir, subject, f'cam{camera}')
    frame = cv2.imread(os.path.join(img_dir, contact_frames[i_cf]))
    imshow('frame', frame, annot_scale['frame'])
    imshow(PERSON[0], sketches[PERSON[0]], annot_scale[PERSON[0]])
    imshow(PERSON[1], sketches[PERSON[1]], annot_scale[PERSON[1]])
    cv2.setMouseCallback('frame', annot_callbacks, ['frame'])
    cv2.setMouseCallback(PERSON[0], annot_callbacks, [PERSON[0]])
    cv2.setMouseCallback(PERSON[1], annot_callbacks, [PERSON[1]])
    init_image(i_cf, img_dir, contact_frames)
    while i_cf < len(contact_frames):
        response = 1
        key = cv2.waitKey(5)
        if key == ord('q') or key == ord('Q'):
            response = 0
            break
        elif key == ord('y') or key == ord('Y') or key == ord('a') or key == ord('A') or key == 13:  # enter
            if key == ord('a') or key == ord('A'):
                # ambiguous
                print("Annotated for ambiguous!")
                sig_annot[contact_frames[i_cf]] = 'ambiguous'
            else:
                if len(selected_regions) > 0 and -1 in selected_regions[-1].values():
                    print("WARNING! You left the last selected incomplete, saving without the last selection!")
                    selected_regions.pop()  # removing incomplete annotation
                print(f'Accepted annotation for {subject}/{contact_frames[i_cf]} ({i_cf+1}/{len(contact_frames)}): {selected_regions}')
                sig_annot[contact_frames[i_cf]] = selected_regions.copy()
            # Save annotation dictionary for subject
            with open(sig_annot_file, 'w') as f:
                json.dump(sig_annot, f)
            # to the next image
            i_cf += 1
            if i_cf >= len(contact_frames):
                break
            init_image(i_cf, img_dir, contact_frames)
            if contact_frames[i_cf] in sig_annot:
                get_prev_annot(sig_annot[contact_frames[i_cf]])
        elif key == ord('p') or key == ord('P'):
            # previous annotations
            i_cf -= 1
            if i_cf < 0:
                raise ValueError("index went lower than zero!")
            init_image(i_cf, img_dir, contact_frames)
            get_prev_annot(sig_annot[contact_frames[i_cf]])
            print(f'Previous annotation for {subject}/{contact_frames[i_cf]} ({i_cf}/{len(contact_frames)}): {selected_regions}')
        elif key == ord('1'):
            camera = 1
        elif key == ord('2'):
            camera = 2
        elif key == ord('3'):
            camera = 3
        elif key == ord('4'):
            camera = 4
        elif key == ord('r') or key == ord('R') or key == ord('-'):
            print("Copying last annotations!")
            init_image(i_cf, img_dir, contact_frames)
            get_prev_annot(sig_annot[contact_frames[i_cf - 1]])
        img_dir = os.path.join(root_dir, subject, f'cam{camera}')
        frame = cv2.imread(os.path.join(img_dir, contact_frames[i_cf]))
        imshow('frame', frame, annot_scale['frame'])
    cv2.destroyAllWindows()
    return response, sig_annot


def get_binary_annots(subj, annot_dir):
    annot_file = os.path.join(annot_dir, f'{subj}.csv')
    annot = pd.read_csv(annot_file, header=None)
    return annot


def get_contact_frames(binary_annot):
    contact_frames = binary_annot[binary_annot.iloc[:, 1] == 2].iloc[:, 0].tolist()  # 2 is touch
    return contact_frames


def annotate_all(subj_contact_count):
    root_dir = r"C:\Users\Doyra001\GithubRepos\contact-annotator\pci_frames\all"
    binary_annot_dir = r"C:\Users\Doyra001\GithubRepos\contact-annotator\annotations\contact\all\cam1"
    sig_annot_dir = r"C:\Users\Doyra001\GithubRepos\contact-signature-annotator\annotations\signature\all"
    # all_subjects = sorted(os.listdir(root_dir))
    all_subjects = [tup[0] for tup in sorted(subj_contact_count.items(), key=lambda x: x[1])]
    print(all_subjects)
    for subject in all_subjects:
        binary_annot = get_binary_annots(subject, binary_annot_dir)
        contact_frames = get_contact_frames(binary_annot)
        response, sig_annot = annotate(subject, root_dir, contact_frames, sig_annot_dir)
        # Save annotation dictionary for subject
        if response != 2 and len(sig_annot) > 0:
            print(f"Saving annotation for {subject}!")
            with open(os.path.join(sig_annot_dir, f'{subject}.json'), 'w') as f:
                json.dump(sig_annot, f)
        if response == 0:
            break


def order_subj_contact_count():
    root_dir = r"C:\Users\Doyra001\GithubRepos\contact-annotator\pci_frames\all"
    binary_annot_dir = r"C:\Users\Doyra001\GithubRepos\contact-annotator\annotations\contact\all\cam1"
    sig_annot_dir = r"C:\Users\Doyra001\GithubRepos\contact-signature-annotator\annotations\signature\all"
    all_subjects = sorted(os.listdir(root_dir))
    subj_contact = {}
    for subject in all_subjects:
        try:
            binary_annot = get_binary_annots(subject, binary_annot_dir)
            contact_frames = get_contact_frames(binary_annot)
            subj_contact[subject] = len(contact_frames)
        except FileNotFoundError:
            print("Annotation file not found for", subject)
    print(subj_contact)
    return subj_contact


def main():
    subj_contact = order_subj_contact_count()
    annotate_all(subj_contact)


if __name__ == '__main__':
    main()
