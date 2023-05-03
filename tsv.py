"""Transform UN parallel txt corpus to multiple tsv files."""
import os


def gen_filename(idx):
    """Generate filenames from UN corpus per-line index.

    sample input: '2014/unw/2015/l_2 en:58:1 ru:58:1'
    sample output:'2014_unw_2015_l_2'
    """
    return '_'.join(idx.split()[0].split('/'))


def main(path_to_file, data_folder, tsv_folder):
    # put ['en \t ru',] into a dict, where keys are filenames
    contents_dict = dict()
    counter = 0
    with open(path_to_file, 'r', encoding='utf-8') as in_f:
        for line in in_f:
            counter += 1
            en, ru, idx = line.split('\t')
            filename = gen_filename(idx.strip())
            try:
                contents_dict[filename].append(f'{en.strip()}\t{ru.strip()}')
            except KeyError:
                contents_dict[filename] = []
                contents_dict[filename].append(f'{en.strip()}\t{ru.strip()}')

    ttl_lines = 0
    for k, v in contents_dict.items():
        lines_num = len(v)
        # comment out next line in final version
        # print(f'doc_idx: {k}; lines: {lines_num}')
        ttl_lines += lines_num
        with open(os.path.join(data_folder, tsv_folder, k+'.txt'), 'w', encoding='utf-8') as to_f:
            for line in v:
                en, ru = line.split('\t')
                to_f.write(en)
                to_f.write('\n')
                to_f.write(ru)
                to_f.write('\n\n')

    print(f'Dictionary length is {len(contents_dict)}')
    print(f'Total lines read from original files: {counter}')
    print(f'Total lines written to all files: {ttl_lines}')


if __name__ == '__main__':
    file_name = 'data/combined_file.txt'
    DATA = 'data'
    TSV = 'tsv'
    main(file_name, DATA, TSV)