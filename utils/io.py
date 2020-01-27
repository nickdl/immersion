from pathlib import Path
import hashlib
import os
import re
import unicodedata


def slugify(value):
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^/.\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '_', value)
    return value


def get_files(directory, string=True, recursive=True, file_type=''):
    pattern = '**/*' if recursive else '*/*'
    files = sorted(f for f in Path(directory).glob(pattern + file_type) if f.is_file())
    if string:
        files = [str(file) for file in files]
    return files


def get_hash(file):
    with open(file, 'rb') as f:
        h = hashlib.new('sha1', f.read())
        return file, h.hexdigest()


def hash_diff(directory1, directory2):
    files1 = get_files(directory1, string=False)
    files2 = get_files(directory2, string=False)
    files1_set = set(str(f.relative_to(directory1)) for f in files1)
    files2_set = set(str(f.relative_to(directory2)) for f in files2)
    print('dir1', len(files1_set), 'dir2', len(files2_set))
    intersection = files1_set.intersection(files2_set)
    print('filename intersection', len(intersection))
    difference1 = files1_set.difference(files2_set)
    print('filename difference dir1', len(difference1))
    difference2 = files2_set.difference(files1_set)
    print('filename difference dir2', len(difference2))
    for different1 in difference1:
        print('filename diff1', different1)
    for different2 in difference2:
        print('filename diff2', different2)
    intersection_files1 = [os.path.join(directory1, f) for f in intersection]
    intersection_files2 = [os.path.join(directory2, f) for f in intersection]
    hashes1 = list(map(get_hash, intersection_files1))
    hashes2 = list(map(get_hash, intersection_files2))
    for hash1, hash2 in zip(hashes1, hashes2):
        if hash1[1] != hash2[1]:
            print('hash different @ intersection', hash1[0], hash2[0])
