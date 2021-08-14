from ebooklib import epub
import json
import argparse
import pathlib

parser = argparse.ArgumentParser(description='Create an ebook from a given JSON containing articles.')
parser.add_argument('-i', metavar='filepath', type=pathlib.Path, help='filepath pointing to a JSON file', required=True)
parser.add_argument('-o', metavar='filepath', type=pathlib.Path, help='filepath pointing to the output EPUB file', required=True)
parser.add_argument('-l', metavar='N', type=int, help='create EPUB from only the first N articles', default=1e9)
parser.add_argument('--cover', metavar='filepath', type=pathlib.Path, help='path to a custom cover image')
parser.add_argument('-m', action='store_true', help='if present, adds a <p> tag containing mined words below the title')
parser.add_argument('-n', action='store_true', help='if present, filters out articles with the nachrichten tag.')
parser.add_argument('-s', action='store_true', help='if present, filters out articles with the sport tag.')
parser.add_argument('-k', action='store_true', help='if present, filters out articles with the kultur tag.')
parser.add_argument('-v', action='store_true', help='if present, filters out articles with the vermischtes tag.')

args = parser.parse_args()
out_filename = args.o
in_filename = args.i
limit = args.l
add_mined = args.m

filters = [args.n, args.s, args.k, args.v]
tags = ["2042", "2039", "2045", "2046"]
f_tags = [t for t, f in zip(tags, filters) if f]

book = epub.EpubBook()

# set metadata
book.set_identifier('id123456')
book.set_title('Nachrichtenleicht')
book.set_language('de')

book.set_cover(str(args.cover), open(args.cover, 'rb').read()) if args.cover else None
book.add_author('Deutschlandfunk')

articles = json.load(open(in_filename))

articles = filter(lambda article : not any(tag in article['url'] for tag in f_tags), articles)

book.toc = []
book.spine = []

def remove_img_tag(html):
    start = html.find('<div class=\"image\"')
    end = html.find('</div>')
    return html[:start] + html[end+6:]

def insert_mined_words(html, mined):
    mined_tag = "<p style=\"font-size: 0.8em\"> " + ', '.join(mined) + "</p> <hr/>"
    end = html.find("</h2>") + len("</h2>")
    html = html[:end] + mined_tag + html[end:]
    return html

for article in articles:
    article['content'] = article['content'].replace('2em', '1em')
    start = article['content'].find('<h2>')
    end = article['content'].find('</h2>')
    title = article['content'][start+4:end]
    id = article['url'][article['url'].find('article_id=')+11:]
    article['content'] = remove_img_tag(article['content'])
    if (add_mined): article['content'] = insert_mined_words(article['content'], article['mined'])
    c = epub.EpubHtml(title=title, file_name=f'${id}.xhtml', lang='de')
    c.content = article['content']
    book.add_item(c)
    book.toc.append(epub.Link(f'${id}.xhtml', title, title))
    book.spine.append(c)
    limit -= 1
    if (limit <= 0):  break

# add default NCX and Nav file
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

# define CSS style
style = 'BODY {color: white;}'
nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

# add CSS file
book.add_item(nav_css)

# basic spine
book.spine.append('nav')

# write to the file
epub.write_epub(out_filename, book, {})
