def percentage_known_order(known, articles):
    known = frozenset(known)
    ordered = []
    for article in articles:
        article_lemmas = frozenset(article['lemmas'])
        percentage = len(known.intersection(article_lemmas))/len(article['lemmas'])
        ordered.append({'url': article['url'], 'percentage': percentage, 'unknown': list(article_lemmas.difference(known))})
    ordered.sort(key=(lambda x : x['percentage']), reverse=True)
    return ordered

# import json

# known_lemmas = json.load(open('data/extracted-anki.json'))
# articles = json.load(open('data/articles-lemmified.json'))

# print(percentage_known_order(known_lemmas, articles)[0:1])
