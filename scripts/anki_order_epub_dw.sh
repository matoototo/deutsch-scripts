#!/bin/bash

# Given an anki .apkg and a limit L, this script extracts that file into an anki2 collection,
# calls anki_lemmas.py on it, then calls order_articles.py and finally, creates an epub with the top L articles.

if (( $# != 2 && $# != 3))
then
  echo "The script requires 2 arguments, a path to an anki .apkg file and the article limit."
  exit 1
fi

file=$(basename -- "$1")
renamed="${file%%.*}.zip"

cp $1 $renamed
rm "decks/collection.anki2"
unzip -j ./$renamed "collection.anki2" -d "decks/" >/dev/null
rm ./$renamed

python3 anki_lemmas.py -i "decks/collection.anki2" -o "data/extracted-anki.json" -f Word Sentence
python3 order_articles.py -k "data/extracted-anki.json" -a "data/dw-lemmified.json" -v "data/dw-vocab.json" -o "data/dw-processed.json" >/dev/null
python3 create_epub.py -i "data/dw-processed.json" -o "books/dw.epub" -l $2 -m --src dw >/dev/null
