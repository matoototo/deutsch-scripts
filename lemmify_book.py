from ebooklib import epub
from lemmify import lemmatize_sentences
import ebooklib
import json
import re
import argparse
import pathlib

def lemmify_book(path):
    book = epub.read_epub(path)
    sentences = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        content = item.get_body_content().decode('utf-8')
        sentences += [x.strip() for x in re.split('\.|«|»', re.sub('<.*?>', '', content).strip()) if x.strip()]

    lemmas = []
    book_obj = {}
    lemmas = lemmatize_sentences(sentences)
    book_obj['sentences'] = sentences
    book_obj['sentence-lemmas'] = lemmas
    book_obj['lemmas'] = list(set(sum(lemmas, [])))
    return book_obj

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Lemmifies a given EPUB file and stores the results in JSON format.')
    parser.add_argument('-i', metavar='filepath', type=pathlib.Path, help='filepath pointing to an EPUB', required=True)
    parser.add_argument('-o', metavar='filepath', type=pathlib.Path, help='filepath pointing to the output JSON file', required=True)
    args = parser.parse_args()

    book_obj = lemmify_book(args.i)
    json.dump([book_obj], open(args.o, 'w'), indent=4)
