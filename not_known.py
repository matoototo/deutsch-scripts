from genericpath import isfile
import json
import argparse
from os import listdir
import pathlib
from posixpath import join

parser = argparse.ArgumentParser(description='Creates a vocabulary of unknown words from the target vocabulary.')
parser.add_argument('--known', metavar='filepath', type=pathlib.Path, help='filepath pointing to a JSON file containing known words', required=True)
parser.add_argument('--vocab', metavar='filepath', type=pathlib.Path, help='filepath pointing to a JSON file containing target vocab or a folder', required=True)
parser.add_argument('-o', metavar='filepath', type=pathlib.Path, help='filepath pointing to the output JSON file or a folder', required=True)

def calc_unknown(vocab, known):
    return {x: y for x, y in vocab.items() if x not in known and x.lower() not in known}

if __name__ == '__main__':
    args = parser.parse_args()

    known = json.load(open(args.known, encoding="utf-8"))

    if args.vocab.suffix == ".json":
        vocab = json.load(open(args.vocab, encoding="utf-8"))
        unknown = calc_unknown(vocab, known)
        json.dump(unknown, open(args.o, 'w', encoding="utf-8"), separators=(',', ': '), indent=4, ensure_ascii=False)
    elif args.o.suffix == ".json":
        print("If used in folder-mode, both paths should be folders.")
        exit(1)
    else:
        onlyfiles = [f for f in listdir(args.vocab) if isfile(join(args.vocab, f))]
        for file in onlyfiles:
            vocab = json.load(open(args.vocab / file, encoding="utf-8"))
            name, extension = file.split('.')
            glued = calc_unknown(vocab, known)

            if args.o.suffix == ".json":
                json.dump(glued, open(args.o, 'w'), separators=(',', ': '), indent=4)
            else:
                json.dump(glued, open(args.o / f"{name}-unknown.json", 'w'), separators=(',', ': '), indent=4)
