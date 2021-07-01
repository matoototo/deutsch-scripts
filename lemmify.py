import json
import argparse
import pathlib

# TODO: clean up tokens that are glued to HTML tags

parser = argparse.ArgumentParser(description='Lemmify a given JSON file.')
parser.add_argument('-i', metavar='filepath', type=pathlib.Path, help='filepath pointing to a JSON file', required=True)
parser.add_argument('-o', metavar='filepath', type=pathlib.Path, help='filepath pointing to the output JSON file', required=True)

args = parser.parse_args()
in_filename = args.i
out_filename = args.o

articles = json.load(open(in_filename))

# taken from https://stackoverflow.com/a/4665027
def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches

def remove_strong_tag(html):
    start = html.find('<strong>')
    end = html.find('</strong>')
    if start == -1:
        return html
    return html[:start] + html[start+8:end] + html[end+9:]

def extract_article_text(html):
    start = list(find_all(html, "<p class=\"kicker\">")) + list(find_all(html, "<p>"))
    end = []
    for index in start:
        end.append(html[index:].find("</p>") + index)
    text = ""
    for s, e in zip(start, end):
        closing_delta = html[s:].find(">")+1
        text += remove_strong_tag(html[s+closing_delta:e]) + '\n\n'
    return text

import spacy

nlp = spacy.load('de_core_news_sm')

for article in articles:
    article_text = extract_article_text(article['content'])
    sentences = article_text.split('.')
    lemmas = map(lambda sentence : list(set(map(lambda t: t.lemma_, nlp(sentence)))), sentences)
    article['sentence-lemmas'] = list(lemmas)
    lemmas = set(map(lambda t: t.lemma_, nlp(article_text)))
    article['lemmas'] = list(lemmas)

with open(out_filename, 'w') as outfile:
    outfile.write('[\n')
    first = True
    for article in articles:
        if first:
            first = not first
        else:
            outfile.write(',')
            outfile.write('\n')
        json.dump(article, outfile)
    outfile.write(']')
