from genericpath import isfile
import math
from os import listdir
from posixpath import join

def process_percentage_known(known, articles, vocab = None):
    known = frozenset(known)
    vocab_keys = frozenset(vocab.keys())
    remove = []
    for i, article in enumerate(articles):
        if vocab: article_lemmas = set(article['lemmas']).intersection(vocab_keys)
        else: article_lemmas = frozenset(article['lemmas'])
        try:
            percentage = len(known.intersection(article_lemmas))/len(article_lemmas)
            article['percentage known'] = percentage
            article['unknown'] = list(article_lemmas.difference(known))
        except:
            print('Empty article:', article['url'])
            remove.append(i)
    articles = [article for i, article in enumerate(articles) if i not in remove]
    return articles

def count_n_plus_x(known, article, vocab_keys = None, x = 1):
    known = frozenset(known)
    count = 0
    mined_words = []
    for lemmas in article['sentence-lemmas']:
        if vocab_keys: filtered_lemmas = set(lemmas).intersection(vocab_keys)
        else: filtered_lemmas = lemmas
        diff = set(filtered_lemmas).difference(known)
        if len(diff) == x:
            count += 1
            mined_words += list(diff)
    return count, list(set(mined_words))

def process_count_n_plus_x(known, articles, vocab = None, x = 1):
    vocab_keys = frozenset(vocab.keys())
    for article in articles:
        count, mined_words = count_n_plus_x(known, article, vocab_keys, x)
        article['percentage n+1'] = count/len(article['sentence-lemmas'])
        article['mined'] = mined_words
    return articles

def process_importance_of_mined(articles, vocab, scale = lambda x : math.log(x)):
    vocab_keys = frozenset(vocab.keys())
    nl_w = 6247/max(vocab.values()) # to get log inputs roughly in line with NL
    for article in articles:
        relevant_words = set(article['mined']).intersection(vocab_keys)
        importance = sum([scale(nl_w*vocab[k]) for k in relevant_words])
        if len(relevant_words) != 0: importance /= len(relevant_words)
        article['importance'] = importance
    return articles

def process_avg_length(articles):
    for article in articles:
        lengths = list(map(lambda x : len(x), article['sentence-lemmas']))
        avglen = 0 if lengths == [] else sum(lengths)/len(lengths)
        article['avglen'] = avglen
    return articles

def process_score(articles):
    imp_w = 1.0
    npx_w = 20.0
    kwn_w = 0.0
    len_w = 0.0
    for x in articles:
        score = imp_w*x['importance']*npx_w*x['percentage n+1'] + kwn_w*x['percentage known'] + len_w*x['avglen']
        x['score'] = score
    return articles

def percentage_known_order(articles):
    articles.sort(key=(lambda x : x['percentage known']), reverse=True)
    return articles

def percentage_n_plus_x_order(articles):
    articles.sort(key=(lambda x : x['percentage n+1']), reverse=True)
    return articles

def importance_order(articles):
    articles.sort(key=(lambda x : x['importance']), reverse=True)
    return articles

def score_order(articles):
    articles.sort(key=(lambda x : x['score']), reverse=True)
    return articles

if __name__ == '__main__':

    import json, argparse, pathlib

    parser = argparse.ArgumentParser(description='Order articles.')
    parser.add_argument('-k', metavar='filepath', type=pathlib.Path, help='filepath pointing to the JSON file with known lemmas', required=True)
    parser.add_argument('-a', metavar='filepath', type=pathlib.Path, help='filepath pointing to the JSON file with the articles or to a folder', required=True)
    parser.add_argument('-v', metavar='filepath', type=pathlib.Path, help='filepath pointing to the JSON file with allowed vocab', required=True)
    parser.add_argument('-o', metavar='filepath', type=pathlib.Path, help='filepath pointing to the output JSON file or to a folder', required=True)

    args = parser.parse_args()
    known_path = args.k
    articles_path = args.a
    vocab_path = args.v
    out_path = args.o

    known_lemmas = json.load(open(known_path))
    vocab = json.load(open(vocab_path))
    filtered_vocab = frozenset(json.load(open("filtered.json")))
    vocab = {k:v for k, v in vocab.items() if k not in filtered_vocab}

    if articles_path.suffix == ".json":
        onlyfiles = [articles_path]
    elif out_path.suffix == ".json":
        print("If used in folder-mode, both input and output paths should be folders.")
        exit(1)
    else:
        onlyfiles = [articles_path / f for f in listdir(articles_path) if isfile(join(articles_path, f))]

    for file in onlyfiles:
        articles = json.load(open(file))
        articles = process_count_n_plus_x(known_lemmas, articles, vocab)
        articles = process_percentage_known(known_lemmas, articles, vocab)
        articles = process_importance_of_mined(articles, vocab)
        articles = process_avg_length(articles)
        articles = process_score(articles)
        articles = score_order(articles)

        json.dump(articles, open(out_path / f"{file.stem}-processed.json", 'w'), indent=4)
