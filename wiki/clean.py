import re
import json
import pathlib
import argparse


def remove_tables(text):
    # remove everything between {| and |}
    return re.sub(r'\{\|.*?\|\}', '', text)

def remove_modifiers(text):
    # remove prefixes such as mini|
    return re.sub(r'[a-z]+\|', '', text)

def add_dot_after_headings(text):
    # add dot after headings such as ==Heading==
    return re.sub(r'(==.*?==)', r'\1.', text)

def remove_categories(text):
    # remove words containing :
    new = ""
    for word in text.split():
        if ':' not in word:
            new += word + ' '
    return new

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cleans a given wiki JSON file by removing tables and other junk.')
    parser.add_argument('-i', metavar='filepath', type=pathlib.Path, help='filepath pointing to an wikipedia JSON', required=True)
    parser.add_argument('-o', metavar='filepath', type=pathlib.Path, help='filepath pointing to the output JSON file', required=True)
    args = parser.parse_args()

    articles = json.load(open(args.i, 'r'))
    for article in articles:
        article['text'] = remove_tables(article['text'])
        article['text'] = remove_modifiers(article['text'])
        article['text'] = add_dot_after_headings(article['text'])
        article['text'] = remove_categories(article['text'])
    json.dump(articles, open(args.o, 'w'), indent=4)
