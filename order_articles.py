import math

def process_percentage_known(known, articles, vocab = None):
    known = frozenset(known)
    vocab_keys = frozenset(vocab.keys())
    processed = []
    for article in articles:
        if vocab: article_lemmas = set(article['lemmas']).intersection(vocab_keys)
        else: article_lemmas = frozenset(article['lemmas'])
        percentage = len(known.intersection(article_lemmas))/len(article_lemmas)
        processed.append({**article, 'percentage known': percentage, 'unknown': list(article_lemmas.difference(known))})
    return processed

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
    processed = []
    for article in articles:
        count, mined_words = count_n_plus_x(known, article, vocab_keys, x)
        processed.append({**article, 'percentage n+1': count/len(article['sentence-lemmas']), 'mined': mined_words})
    return processed

def process_importance_of_mined(articles, vocab, scale = lambda x : math.log(x)):
    vocab_keys = frozenset(vocab.keys())
    processed = []
    for article in articles:
        relevant_words = set(article['mined']).intersection(vocab_keys)
        importance = sum([scale(vocab[k]) for k in relevant_words])
        if len(relevant_words) != 0: importance /= len(relevant_words)
        processed.append({**article, 'importance': importance})
    return processed

def process_avg_length(articles):
    processed = []
    for article in articles:
        lengths = list(map(lambda x : len(x), article['sentence-lemmas']))
        avglen = 0 if lengths == [] else sum(lengths)/len(lengths)
        processed.append({**article, 'avglen': avglen})
    return processed

def percentage_known_order(articles):
    articles.sort(key=(lambda x : x['percentage known']), reverse=True)
    return articles

def percentage_n_plus_x_order(articles):
    articles.sort(key=(lambda x : x['percentage n+1']), reverse=True)
    return articles

def importance_order(articles):
    articles.sort(key=(lambda x : x['importance']), reverse=True)
    return articles

def combined_order(articles):
    imp_w = 1.0
    npx_w = 10.0
    kwn_w = 1.0
    len_w = 0.0
    articles.sort(key=(lambda x : imp_w*x['importance'] + npx_w*x['percentage n+1'] + kwn_w*x['percentage known'] + len_w*x['avglen']), reverse=True)
    return articles

if __name__ == '__main__':

    import json, argparse, pathlib

    parser = argparse.ArgumentParser(description='Order articles.')
    parser.add_argument('-k', metavar='filepath', type=pathlib.Path, help='filepath pointing to the JSON file with known lemmas', required=True)
    parser.add_argument('-a', metavar='filepath', type=pathlib.Path, help='filepath pointing to the JSON file with the articles', required=True)
    parser.add_argument('-v', metavar='filepath', type=pathlib.Path, help='filepath pointing to the JSON file with allowed vocab', required=True)
    parser.add_argument('-o', metavar='filepath', type=pathlib.Path, help='filepath pointing to the output JSON file', required=True)

    args = parser.parse_args()
    known_path = args.k
    articles_path = args.a
    vocab_path = args.v
    out_path = args.o


    known_lemmas = json.load(open(known_path))
    articles = json.load(open(articles_path))
    vocab = json.load(open(vocab_path))

    articles = process_count_n_plus_x(known_lemmas, articles, vocab)
    articles = process_percentage_known(known_lemmas, articles, vocab)
    articles = process_importance_of_mined(articles, vocab)
    articles = process_avg_length(articles)
    articles = combined_order(articles)

    json.dump(articles, open(out_path, 'w'), indent=4)
