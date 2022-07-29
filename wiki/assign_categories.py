import json
import pathlib
import argparse

def get_categories(text):
    # parse categories of the form Kategorie:Name of category Kategorie:Other category
    categories = []
    i = text.find('Kategorie:')
    while i != len(text):
        j = text.find('Kategorie:', i+10)
        if j == -1:
            j = len(text)
        categories.append(text[i+10:j].strip())
        i = j
    return categories

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extracts categories from a wiki JSON.')
    parser.add_argument('-i', metavar='filepath', type=pathlib.Path, help='filepath pointing to an wikipedia JSON', required=True)
    parser.add_argument('-o', metavar='filepath', type=pathlib.Path, help='filepath pointing to the output JSON file', required=True)
    args = parser.parse_args()

    articles = json.load(open(args.i, 'r'))
    for article in articles:
        article['categories'] = get_categories(article['text'])
    json.dump(articles, open(args.o, 'w'), indent=4)
