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
    imp_w = 0.75
    npx_w = 10.0
    kwn_w = 1.0
    articles.sort(key=(lambda x : imp_w*x['importance'] + npx_w*x['percentage n+1'] + kwn_w*x['percentage known']), reverse=True)
    return articles

# import json

# known_lemmas = json.load(open('data/extracted-anki.json'))
# articles = json.load(open('data/articles-lemmified-sentencewise.json'))
# vocab = json.load(open('data/vocab.json'))

# articles = process_count_n_plus_x(known_lemmas, articles, vocab)
# articles = process_percentage_known(known_lemmas, articles, vocab)
# articles = process_importance_of_mined(articles, vocab)

# articles = combined_order(articles)

# json.dump(articles, open('./data/articles-processed.json', 'w'), indent=4)
