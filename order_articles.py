def percentage_known_order(known, articles):
    known = frozenset(known)
    ordered = []
    for article in articles:
        article_lemmas = frozenset(article['lemmas'])
        percentage = len(known.intersection(article_lemmas))/len(article['lemmas'])
        ordered.append({**article, 'percentage': percentage, 'unknown': list(article_lemmas.difference(known))})
    ordered.sort(key=(lambda x : x['percentage']), reverse=True)
    return ordered

def count_n_plus_x(known, article, x = 1):
    known = frozenset(known)
    count = 0
    for lemmas in article['sentence-lemmas']:
        if len(set(lemmas).difference(known)) == x:
            count += 1
    return count

def percentage_n_plus_x_order(known, articles, x = 1):
    ordered = []
    for article in articles:
        ordered.append({**article, 'percentage n+1': count_n_plus_x(known, article, x)/len(article['sentence-lemmas'])})
    ordered.sort(key=(lambda x : x['percentage n+1']), reverse=True)
    return ordered

# import json

# known_lemmas = json.load(open('data/extracted-anki.json'))
# articles = json.load(open('data/articles-lemmified-sentencewise.json'))

# print(percentage_known_order(known_lemmas, articles)[0:1])

# for art in percentage_n_plus_x_order(known_lemmas, articles)[0:5]:
#     print(art['percentage n+1'], art['url'])
