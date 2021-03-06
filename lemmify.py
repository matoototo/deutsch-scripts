import json
import argparse
import pathlib
import re
from os import listdir
from os.path import isfile, join


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
    res = nlp(sentence)
    res = [x for x in res if x.pos_ not in ['PROPN', 'SPACE', 'PUNCT', 'X', 'NUM']] # Filter names, punc, numbers and unknowns.
    res = [x.lemma_ for x in res]
    res = list(set(res)) # eliminate duplicates
    return res

def lemmatize_sentences(sentences):
    res = list(nlp.pipe(sentences))
    for i in range(len(res)):
        res[i] = [x for x in res[i] if x.pos_ not in ['PROPN', 'SPACE', 'PUNCT', 'X', 'NUM']] # Filter names, punc, numbers and unknowns.
        res[i] = [x.lemma_ for x in res[i]]
        res[i] = list(set(res[i])) # eliminate duplicates
    return [x for x in res if len(x) > 2]

def glue_if_number(sentences):
    # glues sentences that end in a number
    # (usually years or ordinals, which are not ends of sentences)
    glued_some = True
    res = [s for s in sentences if len(s) > 2]
    while glued_some:
        res_new = []
        glued_some = False
        last_was_glued = False
        for s1, s2 in zip(res[:-1], res[1:]):
            if s1[-1].isdigit():
                if last_was_glued:
                    res_new[-1] = f"{res_new[-1]}. {s2}"
                else:
                    res_new.append(f"{s1}. {s2}")
                glued_some = True
                last_was_glued = True
            else:
                res_new.append(s1)
                last_was_glued = False
        res = res_new
        if not glued_some:
            return res

import spacy

nlp = spacy.load('de_core_news_sm')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Lemmify a given JSON file.')
    parser.add_argument('-i', metavar='filepath', type=pathlib.Path, help='filepath pointing to a JSON file or a folder containing JSON files', required=True)
    parser.add_argument('-o', metavar='filepath', type=pathlib.Path, help='filepath pointing to the output JSON file or a folder', required=True)
    parser.add_argument('-s', metavar='source', type=str, help='source of the content in the JSON file, {nl | dw | yt | wiki}', required=True)
    parser.add_argument('--no-glue', help='boolean flag that disables glueing together - separated words', action='store_true')
    parser.add_argument('--split-comma', help='boolean flag that enables splitting sentences on commas', action='store_true')

    args = parser.parse_args()
    in_filename = args.i
    out_filename = args.o
    source = args.s
    glue = not args.no_glue
    split_comma = args.split_comma

    if in_filename.suffix == ".json":
        onlyfiles = [in_filename]
    elif out_filename.suffix == ".json":
        print("If used in folder-mode, both paths should be folders.")
        exit(1)
    else:
        onlyfiles = [in_filename / f for f in listdir(in_filename) if isfile(join(in_filename, f))]

    for file in onlyfiles:
        articles = json.load(open(file, encoding="utf-8"))

        for i, article in enumerate(articles):
            if i % 100 == 0:
                print(f"{i}/{len(articles)}")

            if (source in ['nl', 'dw']):
                if glue: article['content'] = glue_dash(article['content'])
                text = extract_article_text(article['content'])
            elif (source == 'yt'): text = article['transcript']
            elif source == 'wiki': text = article['text']
            else: exit(1)

            if split_comma:
                sentences = re.split(r"[,.!?]\s+", text)
            else:
                sentences = re.split(r"[.!?]\s+", text)

            sentences = glue_if_number(sentences)

            lemmas = lemmatize_sentences(sentences)

            article['sentences'] = sentences
            article['sentence-lemmas'] = lemmas
            article['lemmas'] = list(set(sum(lemmas, []))) # Join all lemmas together into one list.

        if len(onlyfiles) > 1:
            json.dump(articles, open(out_filename / f"{file.stem}-lemmified.json", 'w', encoding='utf-8'), separators=(',', ': '), indent=4)
        else:
            json.dump(articles, open(out_filename, 'w', encoding='utf-8'), separators=(',', ': '), indent=4)
