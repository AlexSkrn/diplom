#!/usr/bin/env python3

import os
import numpy as np
import json
import time
from itertools import islice
import multiprocessing
import configparser

from nltk.metrics.distance import jaro_similarity


def count_bytearray_sums(list1):
    """Return bytearray sums of concatendated sentences from two list."""
    s_arr = np.empty([1, len(list1)]).astype('int64')

    counter_sums = 0
    for line in list1:
        en, ru, _ = line.split('\t')
        en_ru = en + ru
        s = sum(bytearray(en_ru, encoding='utf-8'))
        s_arr[0][counter_sums] = s
        counter_sums += 1
    print(f'Sums counter: {counter_sums}')
    return s_arr

def abs_differences_matrix(s_arr):
    """Return a matrix of absolute differences.

    Example: given an array with "1 5 10", it returns
       0 4 9
       4 0 5
       9 5 0
    """
    return np.abs(np.tile(s_arr.T, s_arr.shape[1]) - np.tile(s_arr, (s_arr.shape[1], 1)))

def similarities_dict(abs_diff_matrix, diff_threshold):
    """Return dict of similarities from square numpy array of similarities."""
    sim_dict = dict()
    for i in range(abs_diff_matrix.shape[0]):
        mask = (abs_diff_matrix[i][i+1:] < diff_threshold)
        res = np.where(mask == True)[0]
        res += i+1
        if np.any(res):
            sim_dict[i] = res

    return sim_dict

def sorted_sent_line_number(d: dict)  -> list:
    """Return a sorted list of sentence line numbers from sim dictionary."""
    sents_list = []
    for key, val in d.items():
        sents_list.append(key)
        sents_list.extend(val)
    return sorted(list(set(sents_list)))

def get_sent_dict(list1, sent_n_list, global_counter) -> dict:
    """Return a dict of sentences key:line_num; val: string sentence."""
    sent_dict = dict()
    counter = 0
    for line in list1:
        en, ru, _ = line.split('\t')
        if counter in sent_n_list:
            sent_dict[counter + global_counter] = en + ru
        counter += 1
    return sent_dict

def jaro_sim_wrapper(data):
    return jaro_similarity(data[0], data[1])

def get_batch(sent_dict, sim_dict, global_counter):
    """Return lists of sentence pairs and their numbers for computing Jaro scores."""
    c = global_counter
    sentence_string_pairs = []
    sentence_line_num_pairs = []
    for key_sent_num, val_sent_nums in sim_dict.items():
        for sent_num in val_sent_nums:
            sentence_string_pairs.append((sent_dict[key_sent_num + c], sent_dict[sent_num + c]))
            sentence_line_num_pairs.append((key_sent_num + c, sent_num + c))
    return sentence_string_pairs, sentence_line_num_pairs

def process_jaro_scores(jaro_scores: list, sent_line_num_pairs, threshold: float)  -> dict:
    """Match scores and sentences and return sent_del_dict."""
    sent_del_dict = dict()
    for id, jaro in enumerate(jaro_scores):
        del_sents = []
        if jaro > threshold:
            try:
                s1_id, s2_id = sent_line_num_pairs[id]
                sent_del_dict[s1_id].append(s2_id)
            except KeyError:
                sent_del_dict[s1_id] = [s2_id]
    return sent_del_dict

def save_potential_duplicates(path: str, sent_del_dict, sent_dict):
    with open(path, 'a', encoding='utf-8') as to_f:
        for key, values in sent_del_dict.items():
            for val in values:
              to_f.write(f'{sent_dict[key]}\t{sent_dict[val]}\n')
    return None

def flatten_dict(d: dict) -> list:
    """Return a sorted list of values in dict."""
    return (sorted({x for v in d.values() for x in v}))

def main(source_path, path_for_near_duplicates, path_for_del_numbers, path_for_del_dict, test):
    en_f = open(os.path.join(source_path), 'r', encoding='utf-8')

    try:
        os.remove(path_for_near_duplicates)
    except OSError:
        pass

    final_dict_with_sents_nums_to_del = dict()
    global_counter = 0
    iteration = 0

    try:
        while True:
            print(f'------ Iteration {iteration} ---------')
            batch_size = 5000
            DIFF_THRESHOLD = 10
            next_n_lines = list(islice(en_f, batch_size))
            # next_n_ru = list(islice(ru_f, batch_size))
            if not next_n_lines:
                break
            # STEP 1 - count sums of bytearrays
            bytearry_sums = count_bytearray_sums(next_n_lines)

            # STEP 2 - build similarities dictionary where
            # key: sentence line number; value: list of numbers of "similar" sents
            abs_diff = abs_differences_matrix(bytearry_sums)
            print(f'Shape of abs diff array: {abs_diff.shape}')

            sim_dict = similarities_dict(abs_diff, DIFF_THRESHOLD)
            print(f'Number of keys in sim dict: {len(sim_dict)}')

            # STEP 3 - get a sorted list of all sentence line numbers
            sents_num_list = sorted_sent_line_number(sim_dict)
            print(f'# of sent line numbers in sim dict (keys+vals): {len(sents_num_list)}')

            # STEP 4 - get a list of concatenated real sentences mentioned in sent_num_list
            # This list contains candidate duplicate sentences - but also False Positves
            # What if the list is too large? Below 1 mln is probably okey
            # Need to move filereading from this function and pass only file objects to it
            sent_dict = get_sent_dict(next_n_lines, sents_num_list, global_counter)
            print(f'Dict of string sentences contains {len(sent_dict)} concatenated sents')

            # STEP 5A - get a jaro sim dictionary of sentences above certain threshold
            batch, sents_line_nums = get_batch(sent_dict, sim_dict, global_counter)
            with multiprocessing.Pool() as pool:
                jaros = pool.map(jaro_sim_wrapper, batch)
            # jaros = map(jaro_sim_wrapper, batch)
            threshold = 0.8
            sent_del_dict = process_jaro_scores(jaros, sents_line_nums, threshold)
            

            # STEP 6 -- посмотреть кандидатов на удаление
            # если увеличивать sumbytearray diff, то будет больше результатов
            # но медленнее программа
            if test:
                save_potential_duplicates(path_for_near_duplicates, sent_del_dict, sent_dict)

            # STEP 7 - список предложений для удаления - то есть это все значения из sent_del_dict
            # Return a sorted list of sentence line numbers from sent del dict."""

            final_dict_with_sents_nums_to_del.update(sent_del_dict)

            global_counter += len(next_n_lines)
            iteration += 1

    except Exception as e:
        print(e)
    finally:
        for file in (
            en_f,
        ):
            file.close()
    

    sents_to_del = flatten_dict(final_dict_with_sents_nums_to_del)
    print(f'Number of sentences to delete: {len(sents_to_del)}')
    # STEP 7 - сохранить список в файл
    with open(path_for_del_numbers, 'w', encoding='utf-8') as to_f:
        for num in sents_to_del:
            to_f.write(f'{num}\n')
    
    print(f'Wrote {len(sents_to_del)} numbers of lines to be deleted to {path_for_del_numbers}')
    print(f'Use filter_by_linenumber.py')

    if test:
        # - сохранить в виде словаря
        with open(path_for_del_dict, 'w', encoding='utf-8') as to_f:
            for key, val in final_dict_with_sents_nums_to_del.items():
                to_f.write(f'{str(key)}\t{str(val)}\n')


if __name__ == '__main__':
    start_time = time.time()
    print(f'Start time: {time.strftime("%b %d %Y %H:%M:%S", time.gmtime(start_time))}')

    config = configparser.ConfigParser()
    config.read('config.ini')

    test = False
    if test:
        source_path = config['JARO-LINES-TEST']['source_path']
        path_for_near_duplicates = config['JARO-LINES-TEST']['found_near_duplicates_path']
        path_for_del_numbers = config['JARO-LINES-TEST']['del_numbers']
        path_for_del_dict = config['JARO-LINES-TEST']['del_dict']
    else:
        source_path = config['JARO-LINES']['source_path']
        path_for_near_duplicates = config['JARO-LINES']['found_near_duplicates_path']
        path_for_del_numbers = config['JARO-LINES']['del_numbers']
        path_for_del_dict = config['JARO-LINES']['del_dict']

    main(source_path, path_for_near_duplicates, path_for_del_numbers, path_for_del_dict, test)
    
 
    print('-' * 20)
    print(f'Time: {(time.time() - start_time)/60:.2f} minutes')
    print('-' * 20)
