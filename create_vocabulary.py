import json
import argparse
import pathlib
from os import listdir
from os.path import isfile, join
from collections import Counter


def bad_char_predicate(word):
    bad = ['<', '\n', '>', '\"', '’', '.', ':', ',', '-', '!', '?', *list('0123456789'), '\u00a0']
    for char in bad:
        if char in word:
            return False
    return True


def create_vocab(in_filename):
    articles = json.load(open(in_filename))
    lemmas = []

    for article in articles:
        lemmas += sum([x for x in article['sentence-lemmas']], [])

    counted = Counter(lemmas)
    filtered = list(filter(lambda x:  bad_char_predicate(x), set(lemmas)))
    glued = {k : v for k, v in dict(counted.most_common(None)).items() if k in filtered}

    return glued


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creates a list of lemmas used in a given (articles) JSON,\
                                                counting their frequency and filtering out those that are likely bad.')
    parser.add_argument('-i', metavar='filepath', type=pathlib.Path, help='filepath pointing to a JSON file or a folder containing JSON files', required=True)
    parser.add_argument('-o', metavar='filepath', type=pathlib.Path, help='filepath pointing to the output JSON file or a folder', required=True)

    args = parser.parse_args()
    in_filename = args.i
    out_filename = args.o

    if in_filename.suffix == ".json":
        glued = create_vocab(in_filename)
        json.dump(glued, open(out_filename, 'w'), separators=(',', ': '), indent=4)
    elif out_filename.suffix == ".json":
        print("If used in folder-mode, both paths should be folders.")
        exit(1)
    else:
        onlyfiles = [f for f in listdir(in_filename) if isfile(join(in_filename, f))]
        for file in onlyfiles:
            name, extension = file.split('.')
            glued = create_vocab(in_filename / file)
            json.dump(glued, open(out_filename / f"{name}-vocab.json", 'w'), separators=(',', ': '), indent=4)
