#!/usr/bin/env python3
"""Filter out lines from text file by line numbers."""

import configparser
import time


def filter_by_linenumber(filter_p, data_p, target_p):
    """Read line numbers and sentences, skip sentences, write new file."""
    exclude_line_numbers = set()
    with open(filter_p, 'r', encoding='utf=8') as in_f:
        for line in in_f:
            exclude_line_numbers.add(int(line.strip()))
    with open(data_p, 'r', encoding='utf-8') as data_f, \
       open(target_p, 'w', encoding='utf-8') as target_f:
        line_counter = 0
        for line in data_f:
            if line_counter not in exclude_line_numbers:
                target_f.write(line)
            line_counter += 1


def main():
    """Run the script."""
    config = configparser.ConfigParser()
    config.read('config.ini')
    test = False
    if test:
        filter_p = config['FILTER-BY-NUMBERS-TEST']['exclude_numbers_file']
        source_path = config['FILTER-BY-NUMBERS-TEST']['source_file']
        target_path = config['FILTER-BY-NUMBERS-TEST']['target_file']
    else:
        filter_p = config['FILTER-BY-NUMBERS']['exclude_numbers_file']
        source_path = config['FILTER-BY-NUMBERS']['source_file']
        target_path = config['FILTER-BY-NUMBERS']['target_file']
    
    filter_by_linenumber(filter_p, source_path, target_path)
    print(f'Read {source_path}')
    print(f'Read lines numbers to remove from {source_path}')
    print(f'Wrote results to {target_path}')
    print(f'Done at {time.strftime("%b %d %Y %H:%M:%S", time.gmtime(time.time()))}')

if __name__ == '__main__':
    start_time = time.time()
    print(f'Start time: {time.strftime("%b %d %Y %H:%M:%S", time.gmtime(start_time))}')
    main()
    print('-' * 20)
    print(f'Total time: {(time.time() - start_time)/60:.2f} minutes')
    print('-' * 20)