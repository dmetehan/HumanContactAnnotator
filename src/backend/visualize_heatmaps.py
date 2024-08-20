import os
import cv2
import json
import numpy as np
import matplotlib.cm
import matplotlib.pyplot as plt

PERSON = ['adult', 'child']
N_COARSE = 21
MASK_COARSE_DIR = 'data/region_masks'
sketches = {pers: cv2.imread('data/region_masks/rid_base.png') for pers in PERSON}
# TODO: Customization for regions


def plot_color_gradients(cmap_list):
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))
    # Create figure and adjust figure height to number of colormaps
    nrows = len(cmap_list)
    figh = 0.35 + 0.15 + (nrows + (nrows - 1) * 0.1) * 0.22
    fig, axs = plt.subplots(nrows=nrows + 1, figsize=(6.4, figh))
    fig.subplots_adjust(top=1 - 0.35 / figh, bottom=0.15 / figh,
                        left=0.2, right=0.99)

    for ax, name in zip(axs, cmap_list):
        ax.imshow(gradient, aspect='auto', cmap=matplotlib.cm.get_cmap(name))
        ax.text(-0.01, 0.5, name, va='center', ha='right', fontsize=10,
                transform=ax.transAxes)

    # Turn off *all* ticks & spines, not just the ones with colormaps.
    for ax in axs:
        ax.set_axis_off()

    plt.show()


def create_mask_index():
    mask_ind = {pers: np.zeros_like(cv2.imread(f'data/region_masks/rid_base.png', 0)) for pers in PERSON}
    for pers in PERSON:
        for rid in range(N_COARSE):
            mask = cv2.imread(f'{MASK_COARSE_DIR}/rid_{rid}.png', 0)
            mask_ind[pers][mask < 100] = rid + 1
    return mask_ind


MASK_INDEX = create_mask_index()


def increase_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img


def light_up(person, reg_cnts, cmap='inferno'):
    base_cpy = increase_brightness(sketches[person].copy(), value=30)
    base_cpy_hsv = cv2.cvtColor(base_cpy, cv2.COLOR_BGR2HSV)
    img_cpy = sketches[person].copy()
    # for r in range(len(img_cpy)):
    #     for c in range(len(img_cpy[r, :])):
    #         img_cpy[r, c] = (200, 200, 200)
    # minimum, maximum = np.min(reg_cnts[person]), np.max(reg_cnts[person])
    minimum, maximum = min(np.min(reg_cnts[PERSON[0]]), np.min(reg_cnts[PERSON[1]])), \
        max(np.max(reg_cnts[PERSON[0]]), np.max(reg_cnts[PERSON[1]]))
    colormap = plt.get_cmap(cmap)
    for regions, count in enumerate(reg_cnts[person]):
        if count >= 0:
            x = (count - minimum) / (maximum - minimum)
            r, g, b = colormap(x)[:3]
            img_cpy[MASK_INDEX[person] == (regions + 1)] = (255*b, 255*g, 255*r)
    alpha = base_cpy_hsv[:, :, [2]] / 255
    img_cpy[:] = np.clip(alpha * img_cpy, 0, 255)
    return img_cpy


def read_json(path):
    with open(path, "r") as f:
        data = json.load(f)
        return data


def count_regions(annot, region_counts):
    for frame in annot:
        if annot[frame] == 'ambiguous':
            continue
        for pair in annot[frame]:
            region_counts['adult'][pair['adult']] += 1
            region_counts['child'][pair['child']] += 1


def vis_heatmaps(reg_cnts):
    cmap = 'YlOrRd'  # 'YlOrBr'  # 'inferno'
    for person in ['child', 'adult']:
        img = light_up(person, reg_cnts, cmap=cmap)
        cv2.imshow(person, img)
    plot_color_gradients([cmap])
    cv2.waitKey(0)


def heatmaps_for_gt(annot_file):
    reg_cnts = {'adult': np.zeros(21), 'child': np.zeros(21)}
    # TODO: SUBJECT BASED VISUALIZATION
    # for annot_file in os.listdir(annot_path):
    #     annot = read_json(os.path.join(annot_path, annot_file))
    #     count_regions(annot, reg_cnts)
    annot = read_json(annot_file)
    count_regions(annot, reg_cnts)
    return reg_cnts
