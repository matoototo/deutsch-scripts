import json
import argparse
import pathlib

parser = argparse.ArgumentParser(description='Creates a vocabulary of unknown words from the target vocabulary.')
parser.add_argument('--known', metavar='filepath', type=pathlib.Path, help='filepath pointing to a JSON file containing known words', required=True)
parser.add_argument('--vocab', metavar='filepath', type=pathlib.Path, help='filepath pointing to a JSON file containing target vocab', required=True)
parser.add_argument('-o', metavar='filepath', type=pathlib.Path, help='filepath pointing to the output JSON file', required=True)

def calc_unknown(vocab, known):
    return {x: y for x, y in vocab.items() if x not in known}

if __name__ == '__main__':
    args = parser.parse_args()
    known = json.load(open(args.known))
    vocab = json.load(open(args.vocab))
    unknown = calc_unknown(vocab, known)
    json.dump(unknown, open(args.o, 'w'), separators=(',', ': '), indent=4)
