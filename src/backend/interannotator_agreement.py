import os
import json
import numpy as np
from sklearn.metrics import cohen_kappa_score, jaccard_score


def read_annotations(path):
    annotations = {}
    for filename in os.listdir(path):
        subject = filename.split('.')[0]
        with open(os.path.join(path, filename), 'r') as f:
            annotations[subject] = json.load(f)
    return annotations


def subset_select(ronald, all_set):
    subset = {}
    for subj in ronald:
        frame = list(ronald[subj].keys())[0]
        subset[subj] = {frame: all_set[subj][frame]}
    return subset


def convert_to_binary(subset, res=21):
    assert res in [6, 21]
    binary = {k: [] for k in range(res * res)}
    binary_segment = {k: [] for k in range(res + res)}
    count = 0
    for subj in sorted(subset):
        for frame in sorted(subset[subj]):
            for item in subset[subj][frame]:
                binary[item['adult'] * res + item['child']].append(1)
                if len(binary_segment[item['adult']]) < count + 1:
                    binary_segment[item['adult']].append(1)
                if len(binary_segment[res + item['child']]) < count + 1:
                    binary_segment[res + item['child']].append(1)
            count += 1
            for k in binary:
                if len(binary[k]) < count:
                    binary[k].append(0)
            for k in binary_segment:
                if len(binary_segment[k]) < count:
                    binary_segment[k].append(0)
    return binary, binary_segment


def calc_agreement(metehan_bin, ronald_bin, metehan_bin_seg, ronald_bin_seg, results, res=21):
    kappa = {k: cohen_kappa_score(metehan_bin[k], ronald_bin[k]) for k in range(res * res)
             if (np.sum(metehan_bin[k]) + np.sum(ronald_bin[k])) > 0}  # not nan values
    kappa_seg = {k: cohen_kappa_score(metehan_bin_seg[k], ronald_bin_seg[k]) for k in range(res + res)
                 if (np.sum(metehan_bin_seg[k]) + np.sum(ronald_bin_seg[k])) > 0}  # not nan values
    # reg_id_kappa = {(k // res, k % res): kappa[k] for k in kappa}
    # print(reg_id_kappa)
    results[f'{res}+{res}'] = {'kappa': np.mean(list(kappa_seg.values()))}
    results[f'{res}x{res}'] = {'kappa': np.mean(list(kappa.values()))}
    print(f"Kappa for {res}+{res} regions: {results[f'{res}+{res}']['kappa']}")
    print(f"Kappa for {res}x{res} regions: {results[f'{res}x{res}']['kappa']}")


def comb_regs(subset, res=21):
    assert res in [6, 21]
    if res == 21:
        return subset
    else:
        mapping = {}
        with open("combined_regions_6.txt", 'r') as f:
            for i, line in enumerate(f):
                for reg in list(map(int, map(str.strip, line.strip().split(',')))):
                    mapping[reg] = i
        newset = {}
        for subj in subset:
            newset[subj] = {}
            for frame in subset[subj]:
                newset[subj][frame] = []
                for item in subset[subj][frame]:
                    newset[subj][frame].append({'adult': mapping[item['adult']], 'child': mapping[item['child']]})
        return newset


def onehot_encoding(annot1, annot2, res, segmentation=False):
    onehot1, onehot2 = [], []
    for subj in annot1:
        for frame in annot1[subj]:
            if segmentation:
                onehot1.append(np.zeros((res + res)))
                onehot2.append(np.zeros((res + res)))
                for item in annot1[subj][frame]:
                    onehot1[-1][item['adult']] = 1
                    onehot1[-1][res + item['child']] = 1
                for item in annot2[subj][frame]:
                    onehot2[-1][item['adult']] = 1
                    onehot2[-1][res + item['child']] = 1
            else:
                onehot1.append(np.zeros((res * res)))
                onehot2.append(np.zeros((res * res)))
                for item in annot1[subj][frame]:
                    onehot1[-1][item['adult'] * res + item['child']] = 1
                for item in annot2[subj][frame]:
                    onehot2[-1][item['adult'] * res + item['child']] = 1
    return onehot1, onehot2


def calc_jaccard(metehan_comb, ronald_comb, results, res):
    metehan_onehot, ronald_onehot = onehot_encoding(metehan_comb, ronald_comb, res, segmentation=True)
    results[f'{res}+{res}'] = {'jaccard': jaccard_score(metehan_onehot, ronald_onehot, average='micro')}
    print(f"Jaccard for {res}+{res} regions: {results[f'{res}+{res}']['jaccard']}")
    metehan_onehot, ronald_onehot = onehot_encoding(metehan_comb, ronald_comb, res)
    results[f'{res}x{res}'] = {'jaccard': jaccard_score(metehan_onehot, ronald_onehot, average='micro')}
    print(f"Jaccard for {res}x{res} regions: {results[f'{res}x{res}']['jaccard']}")


def main():
    all_set = read_annotations('annotations/signature/all')
    ronald = read_annotations('annotations/signature/signature_ronald')
    metehan = subset_select(ronald, all_set)
    results = {}
    for res in [21, 6]:
        metehan_comb = comb_regs(metehan, res=res)
        ronald_comb = comb_regs(ronald, res=res)
        metehan_bin, metehan_bin_seg = convert_to_binary(metehan_comb, res=res)
        ronald_bin, ronald_bin_seg = convert_to_binary(ronald_comb, res=res)
        calc_agreement(metehan_bin, ronald_bin, metehan_bin_seg, ronald_bin_seg, results, res=res)
        calc_jaccard(metehan_comb, ronald_comb, results, res=res)


if __name__ == '__main__':
    main()
