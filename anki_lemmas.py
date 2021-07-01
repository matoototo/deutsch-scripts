import sqlite3
import json
import argparse
import pathlib

parser = argparse.ArgumentParser(description='Lemmify words from the specified fields in a given Anki deck.')
parser.add_argument('-i', metavar='filepath', type=pathlib.Path, help='filepath pointing to an anki2 file', required=True)
parser.add_argument('-o', metavar='filepath', type=pathlib.Path, help='filepath pointing to the output JSON file', required=True)
parser.add_argument('-f', metavar='fields', type=str, help='fields from which the lemmas will be extracted', nargs='+', required=True)
args = parser.parse_args()
in_filename = args.i
out_filename = args.o
target_fields = args.f

con = sqlite3.connect(in_filename)
cur = con.cursor()

cur.execute('SELECT * FROM col;')
note_types = json.loads(cur.fetchone()[9])

cur.execute('SELECT * FROM notes;')
rows = cur.fetchall()
rows = list(map(lambda row : {'mid': row[2], 'data': row[6].split('\x1f')}, rows))

extracted = []
for row in rows:
    for field in note_types[str(row['mid'])]['flds']:
        if field['name'] in target_fields:
            extracted.append(row['data'][field['ord']])

import spacy

nlp = spacy.load('de_core_news_sm')
lemmas = list(set(list(map(lambda x : x.lemma_, nlp(" ".join(extracted))))))

with open(out_filename, 'w') as outfile:
    json.dump(lemmas, outfile)
