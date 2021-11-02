import json
import argparse
import pathlib

# TODO: clean up tokens that are glued to HTML tags

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

def glue_dash(text):
    indices = [i for i in find_all(text, "-") if i+1 < len(text) and text[i+1].isupper()]
    text = list(text)
    for i in indices:
        text[i] = ''
        text[i+1] = text[i+1].lower()
    return ''.join(text)

def lemmatize_sentence(sentence):
    pos_dict = {'NOUN': 'N', 'VERB': 'V', 'ADJ': 'ADJ', 'ADV': 'ADV', 'AUX': 'V'}
    res = nlp(sentence)
    res = [x for x in res if x.pos_ not in ['PROPN', 'SPACE', 'PUNCT', 'X', 'NUM']] # Filter names, punc, numbers and unknowns.
    res = [lemmatizer.find_lemma(x.text, pos_dict[x.pos_]) if x.pos_ in pos_dict.keys() else x.lemma_ for x in res]
    res = list(set(res)) # eliminate duplicates
    return res

import spacy
from germalemma import GermaLemma

nlp = spacy.load('de_core_news_sm')
lemmatizer = GermaLemma()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Lemmify a given JSON file.')
    parser.add_argument('-i', metavar='filepath', type=pathlib.Path, help='filepath pointing to a JSON file', required=True)
    parser.add_argument('-o', metavar='filepath', type=pathlib.Path, help='filepath pointing to the output JSON file', required=True)
    parser.add_argument('-s', metavar='source', type=str, help='source of the content in the JSON file, {nl | dw | yt}', required=True)
    parser.add_argument('--no-glue', help='boolean flag that disables glueing together - separated words', action='store_true')

    args = parser.parse_args()
    in_filename = args.i
    out_filename = args.o
    source = args.s
    glue = not args.no_glue

    articles = json.load(open(in_filename))

    for i, article in enumerate(articles):

        if i % 100 == 0:
            print(f"{i}/{len(articles)}")

        if (source in ['nl', 'dw']):
            if glue: article['content'] = glue_dash(article['content'])
            text = extract_article_text(article['content'])
        elif (source == 'yt'): text = article['transcript']
        else: exit(1)
        sentences = text.split('.')
        lemmas = []
        for sentence in sentences:
            lemmas.append(lemmatize_sentence(sentence))

        article['sentence-lemmas'] = lemmas
        article['lemmas'] = list(set(sum(lemmas, []))) # Join all lemmas together into one list.


    json.dump(articles, open(out_filename, 'w'), separators=(',', ': '), indent=4)
