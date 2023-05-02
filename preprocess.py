#!/usr/bin/env python3

"""Find short sentences and numerical and punctuation only texts.

awk 'NR == FNR {pos[$1]; next} FNR in pos' linenumbers sourcefile > targetfile
"""

import time
import configparser
import multiprocessing
from itertools import islice
from string import punctuation
import configparser
# import cProfile


punctuation += '1234567890' + ' '
# import numpy as np

def preprocess(data):
    """Return 0 if sentence pair is good, 1 otherwise."""
    en, ru, _ = data.split('\t')
    cond1 = (en == ru)
    cond2 = (len(en) <= 2 and len(ru) <= 2)  # too short
    cond3 = (set(en).difference(set(punctuation)) == set())  # all punctuation
    cond4 = (set(ru).difference(set(punctuation)) == set())
    if not cond1 and not cond2 and not cond3 and not cond4:
        return 0
    return 1


def main(source_file, file_to_write_name):
    glob_counter = 0
    # candidates = np.array([])
    candidates = []
    with open(source_file, 'r', encoding='utf-8') as in_f:
        while True:
            n = 1000
            next_n_lines = list(islice(in_f, n))
            if not next_n_lines:
                break
            with multiprocessing.Pool() as pool:
                results = pool.map(preprocess, next_n_lines)
            # candidates = np.append(candidates, results, 0)
            candidates.extend(results)
            glob_counter += n
            if glob_counter % 1000000 == 0:
                print(f'counter: {glob_counter}')
    # get all 0's for awk
    candidates_indices = [idx for idx, value in enumerate(candidates) if value == 0]
    print(f'Read {len(candidates)} lines in file {source_file}')
    print(f'Found {sum(candidates)} to be removed.')
    with open(file_to_write_name, 'w', encoding='utf-8') as to_f:
        for num in candidates_indices:
            to_f.write(f'{num+1}\n')  # incremented by 1 for use with AWK
            # to_f.write(f'{num}\n')
    print(f'Indices (starting with 1) of lines to be kept are written to {file_to_write_name}')


if __name__ == '__main__':
    start_time = time.time()
    print(f'Start time: {time.strftime("%b %d %Y %H:%M:%S", time.gmtime(start_time))}')

    config = configparser.ConfigParser()
    config.read('config.ini')
    # source_file = config['PREPROCESS_TEST']['source_file']
    # file_to_write_name = config['PREPROCESS_TEST']['write_to_file']
    source_file = config['PREPROCESS']['source_file']
    file_to_write_name = config['PREPROCESS']['write_to_file']
    main(source_file, file_to_write_name)
    # cProfile.run('main(source_file, file_to_write_name)')

    print('-' * 20)
    print(f'Total time: {(time.time() - start_time)/60:.2f} minutes')
    print('-' * 20)