"""Put the publisher's front covers on the nine Maxford Global books.

    python tools/set_maxford_covers.py "<folder with the cover pictures>"

The covers name the series: Simply Phonics, Simply Maths and Aasan Urdu, in Step A / B / C (Urdu: qadam 1 / 2 / 3),
which are Play Group (3+), Nursery (4+) and Prep (5+). Each cover is fitted to its book's page shape by trimming only
the bottom (the logos are at the top), saved as books/<id>/cover.jpg, and shown when the book opens (frontCover).
The book's title becomes the cover's, and its spine colours are taken from the cover.
"""
import json
import os
import sys

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'books')
# cover picture (WhatsApp file name, 23 Nov 2026) -> book and its title as printed on the cover
COVERS = {
    '5.46.23 PM': ('maxford-global-qaida-3-english', 'Simply Phonics Step A'),
    '5.46.21 PM': ('maxford-global-qaida-4-english', 'Simply Phonics Step B'),
    '5.46.19 PM': ('maxford-global-qaida-5-english', 'Simply Phonics Step C'),
    '5.46.22 PM (1)': ('maxford-global-qaida-3-maths', 'Simply Maths Step A'),
    '5.46.20 PM (1)': ('maxford-global-qaida-4-maths', 'Simply Maths Step B'),
    '5.46.18 PM (1)': ('maxford-global-qaida-5-maths', 'Simply Maths Step C'),
    '5.46.22 PM': ('maxford-global-qaida-3-urdu', 'آسان اردو قدم پہلا'),
    '5.46.20 PM': ('maxford-global-qaida-4-urdu', 'آسان اردو قدم دوسرا'),
    '5.46.18 PM': ('maxford-global-qaida-5-urdu', 'آسان اردو قدم تیسرا'),
}
WIDTH = 720


def spine(img):
    """The cover's background colour (its left and right edges), and a darker shade of it."""
    w, h = img.size
    px = [img.getpixel((x, y)) for x in (2, w - 3) for y in range(h // 5, h * 4 // 5, 7)]
    r, g, b = (sorted(c[i] for c in px)[len(px) // 2] for i in range(3))
    hexa = lambda c: '#%02x%02x%02x' % c
    return hexa((r, g, b)), hexa(tuple(int(v * .62) for v in (r, g, b)))


def main(folder):
    for stamp, (book, title) in COVERS.items():
        src = os.path.join(folder, f'WhatsApp Image 2026-11-23 at {stamp}.jpeg')
        d = os.path.join(ROOT, book)
        with open(os.path.join(d, 'meta.json'), encoding='utf-8-sig') as f:
            meta = json.load(f)
        img = Image.open(src).convert('RGB')
        w, h = img.size
        keep = min(h, round(w / meta['ratio']))          # the page's shape, from the top down
        img = img.crop((0, 0, w, keep)).resize((WIDTH, round(WIDTH / meta['ratio'])), Image.LANCZOS)
        img.save(os.path.join(d, 'cover.jpg'), quality=86, optimize=True, progressive=True)
        meta['title'], meta['author'], meta['frontCover'] = title, 'Maxford Global Learning', True
        meta['c1'], meta['c2'] = spine(img)
        with open(os.path.join(d, 'meta.json'), 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=4)
            f.write('\n')
        print(f'{book}: {title} (trimmed {h - keep}px of {h} from the bottom), spine {meta["c1"]}')


if __name__ == '__main__':
    main(sys.argv[1])
