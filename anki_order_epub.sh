#!/bin/bash

# Given an anki .apkg and a limit L, this script extracts that file into an anki2 collection,
# calls anki_lemmas.py on it, then calls order_articles.py and finally, creates an epub with the top L articles.

if (( $# != 2 && $# != 3))
then
  echo "The script requires 2 or 3 arguments, a path to an anki .apkg file, the article limit,
and an optional 'split', which creates a different epub for every category instead of them together."
  exit 1
fi

file=$(basename -- "$1")
renamed="${file%%.*}.zip"

cp $1 $renamed
rm "decks/collection.anki2"
unzip -j ./$renamed "collection.anki2" -d "decks/" >/dev/null
rm ./$renamed

python3 anki_lemmas.py -i "decks/collection.anki2" -o "data/extracted-anki.json" -f Word Sentence >/dev/null 2>&1
python3 order_articles.py -k "data/extracted-anki.json" -a "data/articles-lemmified.json" -v "data/vocab.json" -o "data/articles-processed.json" >/dev/null

if [[ $# == 3 && $3 == "split" ]]
then
  python3 create_epub.py -i "data/articles-processed.json" -o "data/book_vermischtes.epub" -l $2 -m -nsk >/dev/null
  python3 create_epub.py -i "data/articles-processed.json" -o "data/book_kultur.epub" -l $2 -m -nsv >/dev/null
  python3 create_epub.py -i "data/articles-processed.json" -o "data/book_sport.epub" -l $2 -m -nvk >/dev/null
  python3 create_epub.py -i "data/articles-processed.json" -o "data/book_nachrichten.epub" -l $2 -m -vsk >/dev/null
else
  python3 create_epub.py -i "data/articles-processed.json" -o "data/book.epub" -l $2 -m >/dev/null
fi
