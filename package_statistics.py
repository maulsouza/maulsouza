#!/usr/bin/python
import os.path
import sys
from typing import TextIO

import operator
import requests
import tempfile
import shutil
import gzip
import re

MIRROR_DOWNLOAD = 'http://ftp.uk.debian.org/debian/dists/stable/main/'

dir_path = tempfile.mkdtemp()


def download_file(arch):
    print('Downloading file')
    try:
        url = f'{MIRROR_DOWNLOAD}Contents-{arch}.gz'
        r = requests.get(url, allow_redirects=True)
        if r.status_code != 200:
            raise
        file_name = os.path.join(dir_path, 'Contents.gz')
        open(file_name, 'wb').write(r.content)
    except:
        print('Error downloading file')
        quit()
    return file_name


def extract_file(file_name):
    print('Extracting downloaded file')
    try:
        with gzip.open(file_name, 'rb') as f_in:
            ret_file_name = os.path.join(dir_path, 'file.txt')
            with open(ret_file_name, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    except:
        print("File type not supported to extraction")
        quit()
    return ret_file_name


def process_file(file_name):
    print('Processing file', end='')
    max_col = 0
    hash_packages = {}
    temp = set()
    with open(file_name, 'r') as fp:
        ii = 0
        for line in fp.readlines():
            values = re.split(r'\s+', line)[1].split(',')
            for hashing in values:
                if ii % 100000 == 0:
                    print('.', end='')
                ii += 1
                if hashing in temp:
                    hash_packages[hashing] += 1
                else:
                    max_col = max(max_col, len(hashing))
                    hash_packages[hashing] = 1
                    temp.add(hashing)
    print('')
    return sorted(hash_packages.items(), key=operator.itemgetter(1), reverse=True), max_col


def main(argv):
    architecture = ''
    try:
        if len(argv) != 1:
            raise Exception('Expected syntax: package_statistics.py <architecture>')
    except Exception as e:
        print(e)
        quit()
    file_downloaded = download_file(argv[0])
    text_file = extract_file(file_downloaded)
    sorted_packages, max_col = process_file(text_file)
    for ii in range(10):
        print(f'{ii+1:3}. {sorted_packages[ii][0]:{max_col}}   {sorted_packages[ii][1]}')

    shutil.rmtree(dir_path)


if __name__ == "__main__":
    main(sys.argv[1:])
