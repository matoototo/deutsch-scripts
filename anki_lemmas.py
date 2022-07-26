import sqlite3
import json
import argparse
import pathlib
import re
from lemmify import lemmatize_sentences


def lemmify_deck(in_filename, target_fields):
    con = sqlite3.connect(in_filename)
    cur = con.cursor()

    cur.execute('SELECT * FROM col;')
    note_types = json.loads(cur.fetchone()[9])

    cur.execute('SELECT * FROM notes;')
    rows = cur.fetchall()
    rows = list(map(lambda row : {'mid': row[2], 'data': row[6].split('\x1f')}, rows))

    def clean(row):
        row = re.sub(r"</?\w+>", " ", row)
        row = row.replace("&nbsp;", " ")
        return row

    extracted = []
    singles = []
    for row in rows:
        for field in note_types[str(row['mid'])]['flds']:
            if field['name'] in target_fields:
                output = clean(row['data'][field['ord']]).strip()
                if len(output.split(" ")) == 1: singles.append(output)
                else: extracted.append(output)
    return list(set(sum(lemmatize_sentences(extracted), singles)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Lemmify words from the specified fields in a given Anki deck.')
    parser.add_argument('-i', metavar='filepath', type=pathlib.Path, help='filepath pointing to an anki2 file', required=True)
    parser.add_argument('-o', metavar='filepath', type=pathlib.Path, help='filepath pointing to the output JSON file', required=True)
    parser.add_argument('-f', metavar='fields', type=str, help='fields from which the lemmas will be extracted', nargs='+', required=True)
    args = parser.parse_args()
    in_filename = args.i
    out_filename = args.o
    target_fields = args.f

    lemmas = lemmify_deck(in_filename, target_fields)

    with open(out_filename, 'w+') as outfile:
        outfile.writelines(json.dumps(lemmas))
