#!/usr/bin/env python3

"""This script rstrips numbers and spaces."""

import time
import time
from itertools import islice
import configparser
import re


def main(source_file, target_file):
    regex_en_pare = r'\d+(?:\.\d+)?(?:\s+\d+(?:\.\d+)?)*\s*$'
    regex_ru_pare = r'\d+(?:\,\d+)?(?:\s+\d+(?:\,\d+)?)*\s*$'

    regex_en = r'\d+(?:\.\d+)?(?:\s+\(\d+(?:\.\d+)?\))*\s*$'
    regex_ru = r'\d+(?:\,\d+)?(?:\s+\(\d+(?:\,\d+)?\))*\s*$'

    with open(source_file, 'r', encoding='utf-8') as in_f, \
        open(target_file, 'w', encoding='utf-8') as to_f:
        counter = 0
        for line in in_f:
            en, ru, idx = line.split('\t')
            # cond1 = ru.endswith('года')
            # cond2 = ru.endswith('год')
            # cond3 = ru.endswith('ГОДА')
            # cond4 = ru.endswith('годы')
            # cond5 = ru.endswith('годов')
            # cond6 = ru.endswith('евро')
            # if cond1 or cond2 or cond3 or cond4 or cond5 or cond6:
            if ru[-1].isalpha():
                pass
            else:
                en = re.split(regex_en, en)[0].strip()
                en = re.split(regex_en_pare, en)[0].strip()
                ru = re.split(regex_ru, ru)[0].strip()
                ru = re.split(regex_ru_pare, ru)[0].strip()
            to_f.write(f'{en}\t{ru}\t{idx}')  # idx keeps its \n
            counter += 1
        
    print(f'Read {counter} lines in {source_file}')
    print(f'Wrote processed lines to {target_file}')
    

if __name__ == '__main__':
    start_time = time.time()
    print(f'Start time: {time.strftime("%b %d %Y %H:%M:%S", time.gmtime(start_time))}')

    config = configparser.ConfigParser()
    config.read('config.ini')
    
    test = False
    if test:
        source_file = config['RSTRIP-TEST']['source_file']
        target_file = config['RSTRIP-TEST']['target_file']
    else:
        source_file = config['RSTRIP']['source_file']
        target_file = config['RSTRIP']['target_file']

    main(source_file, target_file)


    print('-' * 20)
    print(f'Total time: {(time.time() - start_time)/60:.2f} minutes')
    print('-' * 20)


