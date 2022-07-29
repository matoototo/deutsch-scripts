import json
import pathlib
import argparse
from collections import Counter

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creates a JSON file categories ordered by number of articles.')
    parser.add_argument('-i', metavar='filepath', type=pathlib.Path, help='filepath pointing to an wikipedia JSON', required=True)
    parser.add_argument('-o', metavar='filepath', type=pathlib.Path, help='filepath pointing to the output JSON file', required=True)
    args = parser.parse_args()

    articles = json.load(open(args.i, 'r'))
    categories = Counter()
    for article in articles:
        for category in article['categories']:
            categories.update([category])
    categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    json.dump(categories, open(args.o, 'w', encoding='utf-8'), indent=4)
