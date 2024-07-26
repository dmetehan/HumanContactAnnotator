import os
import json
import numpy as np
from itertools import combinations
from sklearn.metrics import cohen_kappa_score, jaccard_score


def read_annotations(path):
    annotations = {}
    # TODO: The following part is for subject based annotating
    # for filename in os.listdir(path):
    #     subject = filename.split('.')[0]
    #     with open(os.path.join(path, filename), 'r') as f:
    #         annotations[subject] = json.load(f)

    # non-subject based annotations
    with open(path, 'r') as f:
        annotations["default"] = json.load(f)
    return annotations


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


def calc_agreement(metehan_bin, ronald_bin, metehan_bin_seg, ronald_bin_seg, res=21):
    kappa = {k: cohen_kappa_score(metehan_bin[k], ronald_bin[k]) for k in range(res * res)
             if (np.sum(metehan_bin[k]) + np.sum(ronald_bin[k])) > 0}  # not nan values
    kappa_seg = {k: cohen_kappa_score(metehan_bin_seg[k], ronald_bin_seg[k]) for k in range(res + res)
                 if (np.sum(metehan_bin_seg[k]) + np.sum(ronald_bin_seg[k])) > 0}  # not nan values
    # reg_id_kappa = {(k // res, k % res): kappa[k] for k in kappa}
    # print(reg_id_kappa)
    return np.mean(list(kappa_seg.values())), np.mean(list(kappa.values()))
    # results[f'{res}+{res}'] = {'kappa': np.mean(list(kappa_seg.values()))}
    # results[f'{res}x{res}'] = {'kappa': np.mean(list(kappa.values()))}
    # print(f"Kappa for {res}+{res} regions: {results[f'{res}+{res}']['kappa']}")
    # print(f"Kappa for {res}x{res} regions: {results[f'{res}x{res}']['kappa']}")


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


def calc_pairwise_agreement(first_path, second_path):
    first_annot = read_annotations(first_path)
    second_annot = read_annotations(second_path)
    first_bin, first_bin_seg = convert_to_binary(first_annot)
    second_bin, second_bin_seg = convert_to_binary(second_annot)
    # TODO: Add option for jaccard score calculation as well
    return calc_agreement(first_bin, second_bin, first_bin_seg, second_bin_seg)


def agreement_for_all_annotator_pairs(annotators, annot_dir):
    all_possible_pairs = list(combinations(annotators, 2))
    seg_results = {cur_annotator: [] for cur_annotator in annotators}
    sig_results = {cur_annotator: [] for cur_annotator in annotators}
    for pair in all_possible_pairs:
        paths = [os.path.join(annot_dir, filename) for annotator in pair for filename in os.listdir(annot_dir)
                 if annotator in filename and filename.endswith(".json")]
        print(paths)
        cur_seg_result, cur_sig_result = calc_pairwise_agreement(*paths)
        for annotator in pair:
            seg_results[annotator].append(cur_seg_result)
            sig_results[annotator].append(cur_sig_result)
    for annotator in seg_results:
        seg_results[annotator] = (np.average(seg_results[annotator]), np.std(seg_results[annotator]))
        sig_results[annotator] = (np.average(sig_results[annotator]), np.std(sig_results[annotator]))
    return seg_results, sig_results
