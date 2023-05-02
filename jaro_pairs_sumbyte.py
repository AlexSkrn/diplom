#!/usr/bin/env python3

"""Write to file Jaro scores between sentences in 2-language sentence pairs."""

# import os
import time
import multiprocessing
from math import floor, ceil
from itertools import islice
import configparser


# Function to calculate the
# Jaro Similarity of two strings
def jaro_distance(s1, s2):
    # s1, s2, _ = data.split('\t')
    # s1, s2 = data[0], data[1]
    # If the s are equal
    # if (s1 == s2):
    #     return 1.0
 
    # Length of two s
    len1 = len(s1)
    len2 = len(s2)
 
    # Maximum distance upto which matching
    # is allowed
    max_dist = floor(max(len1, len2) / 2) - 1
 
    # Count of matches
    match = 0
 
    # Hash for matches
    hash_s1 = [0] * len(s1)
    hash_s2 = [0] * len(s2)
 
    # Traverse through the first
    for i in range(len1):
 
        # Check if there is any matches
        for j in range(max(0, i - max_dist),
                       min(len2, i + max_dist + 1)):
             
            # If there is a match
            if (s1[i] == s2[j] and hash_s2[j] == 0):
                hash_s1[i] = 1
                hash_s2[j] = 1
                match += 1
                break
 
    # If there is no match
    if (match == 0):
        return 0.0
 
    # Number of transpositions
    t = 0
    point = 0
 
    # Count number of occurrences
    # where two characters match but
    # there is a third matched character
    # in between the indices
    for i in range(len1):
        if (hash_s1[i]):
 
            # Find the next matched character
            # in second
            while (hash_s2[point] == 0):
                point += 1
 
            if (s1[i] != s2[point]):
                t += 1
            point += 1
    t = t//2
 
    # Return the Jaro Similarity
    return (match/ len1 + match / len2 +
            (match - t) / match)/ 3.0

def process(data):
    """Return Jaro score if diff of sums of bytearrays is below cutoff val."""
    cutoff_val = 24100
    s1, s2, _ = data.split('\t')
    s1_sum = sum(bytearray(s1, encoding='utf-8'))
    s2_sum = sum(bytearray(s2, encoding='utf-8'))
    diff = abs(s1_sum - s2_sum)
    if diff < cutoff_val:
        return jaro_distance(s1, s2)
    return 0  # low score indicates large differnce between 2 strings


def main(source_path, path_for_jaro, path_good_numbers, path_bad_numbers):
    threshold = 0.8
    glob_counter = 0
    jaro_similarities = []
    with open(source_path, 'r', encoding='utf-8') as in_f:
        while True:
            n = 1000
            next_n_lines = list(islice(in_f, n))
            if not next_n_lines:
                break
            with multiprocessing.Pool() as pool:
                temp_results = pool.map(process, next_n_lines)
            jaro_similarities.extend(temp_results)
            glob_counter += n
            if glob_counter % 1000000 == 0:
                print(f'counter: {glob_counter}')

    print(f'Read {source_path}')
    
    with open(path_for_jaro, 'w', encoding='utf-8') as to_f:
        for i in jaro_similarities:
            to_f.write(f'{i}\n')
    print(f'Wrote {len(jaro_similarities)} jaro scores to {path_for_jaro}')

    # if Jaro score is low, then sentences are very different
    # and I want to keep them
    candidates = [0 if i < threshold else 1 for i in jaro_similarities]
    print(f'Found {sum(candidates)} sentence pairs to be removed.')

    good_indices = [idx for idx, value in enumerate(candidates) if value == 0]
    with open(path_good_numbers, 'w', encoding='utf-8') as to_f:
        for num in good_indices:
            to_f.write(f'{num+1}\n')  # incremented by 1 for use with AWK
    print(f'Indices (starting with 1) of lines to be kept are written to {path_good_numbers}')
    print("""Use: awk 'NR == FNR {pos[$1]; next} FNR in pos' linenumbers sourcefile > targetfile.""")

    bad_indices = [idx for idx, value in enumerate(candidates) if value == 1]
    with open(path_bad_numbers, 'w', encoding='utf-8') as to_f:
        for num in bad_indices:
            to_f.write(f'{num+1}\n')  # incremented by 1 for use with AWK
    print(f'Indices (starting with 1) of lines to be removed are written to {path_bad_numbers}')
    print("""Use: awk 'NR == FNR {pos[$1]; next} FNR in pos' linenumbers sourcefile > targetfile.""")



if __name__ == "__main__":
    start_time = time.time()
    print(f'Start time: {time.strftime("%b %d %Y %H:%M:%S", time.gmtime(start_time))}')

    config = configparser.ConfigParser()
    config.read('config.ini')

    test = False
    if test:
        source_path = config['JARO-PAIRS-TEST']['source_path']
        path_for_jaro = config['JARO-PAIRS-TEST']['path_for_jaro']
        path_good_numbers = config['JARO-PAIRS-TEST']['path_good_numbers']
        path_bad_numbers = config['JARO-PAIRS-TEST']['path_bad_numbers']
    else:
        source_path = config['JARO-PAIRS']['source_path']
        path_for_jaro = config['JARO-PAIRS']['path_for_jaro']
        path_good_numbers = config['JARO-PAIRS']['path_good_numbers']
        path_bad_numbers = config['JARO-PAIRS']['path_bad_numbers']

    main(source_path, path_for_jaro, path_good_numbers, path_bad_numbers)
    

    print('-' * 20)
    print(f'Total time: {(time.time() - start_time)/60:.2f} minutes')
    print('-' * 20)