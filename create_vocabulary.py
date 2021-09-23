import json
import argparse
import pathlib
from collections import Counter

parser = argparse.ArgumentParser(description='Creates a list of lemmas used in a given (articles) JSON,\
                                              counting their frequency and filtering out those that are likely bad.')
parser.add_argument('-i', metavar='filepath', type=pathlib.Path, help='filepath pointing to a JSON file', required=True)
parser.add_argument('-o', metavar='filepath', type=pathlib.Path, help='filepath pointing to the output JSON file', required=True)

args = parser.parse_args()
in_filename = args.i
out_filename = args.o

articles = json.load(open(in_filename))

lemmas = []
for article in articles:
    lemmas += sum([x for x in article['sentence-lemmas']], [])

def bad_char_predicate(word):
    bad = ['<', '\n', '>', '\"', '’', '.', ':', ',', '-', '!', '?', *list('0123456789'), '\u00a0']
    for char in bad:
        if char in word:
            return False
    return True

counted = Counter(lemmas)
filtered = list(filter(lambda x:  bad_char_predicate(x), set(lemmas)))
glued = {k : v for k, v in dict(counted.most_common(None)).items() if k in filtered}
json.dump(glued, open(out_filename, 'w'), separators=(',', ': '), indent=4)
