"""The publisher's videos as buttons on their pages, laid out as in Stemford English 3+.

    python tools/make_maxford_video_buttons.py          # writes books/activities-maxford-videos.js
    python tools/make_maxford_video_buttons.py --show   # and an overlay of each page in tools/_video_buttons/

Only the books whose video lists the publisher gave (Qaida 3+ English, Maths and Urdu), and only the pages whose
printed QR code has those videos. As in Stemford English 3+ (D:/javed publishers, books/activities-english3.js):
the videos are one column of buttons on the page's big picture, in its top corner, in the order Story, Phonic
Poem, Vocabulary (then the others), 4.5% of the page apart; and the letter's Formation video is not a page button
but "How to write a" in its writing page's Write/Colour, beside Show me how (the fill activity's `video`). The
Maths and Urdu writing pages have no Write/Colour activity, so their Formation video stays in the column. The QR's
"Watch this" stays as it is.
"""
import json
import os
import re
import sys

from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
# what the video is, from its title: (pattern, kind, English label, Urdu label, icon); the first that matches
KINDS = [
    (r"teacher", 'teachers', "Teachers", 'اساتذہ', '👩‍🏫'),
    (r"parent", 'parents', "Parents", 'والدین', '👪'),
    (r"story", 'story', 'Story', 'کہانی', '📖'),
    (r"poem|rhyme", 'poem', 'Phonic Poem', 'نظم', '🎵'),
    (r"words? .*writing", 'words', 'Words & Writing', 'الفاظ اور لکھائی', '✏️'),
    (r"formation|writing", 'formation', 'Formation', 'لکھائی', '✏️'),
    (r"vocabulary|words", 'words', 'Vocabulary', 'الفاظ', '🔤'),
    (r"objects", 'objects', 'Objects', 'چیزیں', '🍎'),
    (r"comparison|compare", 'compare', 'Compare', 'موازنہ', '⚖️'),
    (r"lesson", 'lesson', 'Lesson', 'سبق', '📚'),
]
ORDER = ['story', 'poem', 'words', 'objects', 'compare', 'lesson', 'formation', 'teachers', 'parents']
STEP = 4.5          # between buttons, % of the page height (as in Stemford English 3+)
# the column's top corner on each page's big picture: (x, y, side); 'left' = x is the column's left edge,
# 'right' = x is its right edge (the Urdu book reads from the right, its picture is on the left of the letter)
COLUMN = {
    'maxford-global-qaida-3-english': {None: (68, 20.5, 'left')},           # the letter's story picture, under "Watch this"
    'maxford-global-qaida-3-maths': {None: (68, 21.5, 'left'),              # the number's picture, under "Watch this"
                                     '7': (2.5, 13, 'left'), '8': (2.5, 15.5, 'left')},   # the sky over the lion / the stalls
    'maxford-global-qaida-3-urdu': {None: (55.5, 19.5, 'right')},           # the letter's picture, its right corner
}
# books whose writing page has a Write/Colour activity: the Formation video goes there as "How to write ..."
FILL_FORMATION = {'maxford-global-qaida-3-english'}


def library():
    text = open(os.path.join(ROOT, 'books', 'library.js'), encoding='utf-8').read()
    return json.loads(text.split('window.PDF_BOOKS = ', 1)[1].strip().rstrip(';'))


def kind_of(title):
    for pattern, kind, en, ur, icon in KINDS:
        if re.search(pattern, title, re.I):
            return kind, en, ur, icon
    return 'story', 'Video', 'ویڈیو', '▶️'


def width(label):
    """A button's width (the app's .story-btn), % of the page width: the icon, the padding and the words."""
    return round(9 + 1.75 * len(label), 1)


LETTERS = 'abcdefghijklmnopqrstuvwxyz'
ENGLISH_PAGES = [11, 15, 19, 23, 31, 35, 39, 43, 49, 53, 57, 61, 69, 73, 77, 81, 87, 91, 95, 99, 107, 111, 115, 119, 125, 129]


def main(show):
    books = {b['id']: b for b in library()}
    out, fills, notes = {}, {}, []
    for book, columns in COLUMN.items():
        b = books[book]
        urdu = bool(b.get('rtl'))
        for page, item in sorted(b.get('qr', {}).items(), key=lambda kv: int(kv[0])):
            vids = item.get('videos', [])
            if not vids:
                continue
            found = []
            for v in vids:
                title = v.get('label') or v['title']
                kind, en, ur, icon = kind_of(title)
                found.append((ORDER.index(kind), kind, ur if urdu else en, icon, title, v['id']))
            found.sort(key=lambda f: f[0])
            x0, y, side = columns.get(page, columns[None])
            acts, seen = [], {}
            for _, kind, name, icon, title, vid in found:
                src = 'https://youtu.be/' + vid
                if kind == 'formation' and book in FILL_FORMATION:
                    letter = LETTERS[ENGLISH_PAGES.index(int(page))] if int(page) in ENGLISH_PAGES else ''
                    fills.setdefault(book, {})[str(int(page) + 1)] = {'title': f'How to write {letter}'.strip(), 'src': src}
                    continue
                seen[name] = seen.get(name, 0) + 1
                label = f'{name} {seen[name]}' if seen[name] > 1 else name
                w = width(label)
                x = x0 if side == 'left' else x0 - w
                acts.append({'type': 'videos', 'label': label, 'icon': icon, 'title': title, 'button': {'x': round(x, 1), 'y': round(y, 1)},
                             'videos': [{'title': label, 'src': src}], '_w': w})
                y += STEP
            out.setdefault(book, {})[page] = acts
            notes.append(f'{book} p{page}: {len(acts)} buttons' + (f' + How to write on p{int(page) + 1}' if book in fills and str(int(page) + 1) in fills[book] else ''))
    if show:
        folder = os.path.join(ROOT, 'tools', '_video_buttons')
        os.makedirs(folder, exist_ok=True)
        for f in os.listdir(folder):
            os.remove(os.path.join(folder, f))
        for book, pages in out.items():
            for page, acts in pages.items():
                im = Image.open(os.path.join(ROOT, books[book]['dir'], 'p%03d.jpg' % int(page))).convert('RGB')
                d, (W, H) = ImageDraw.Draw(im), im.size
                for a in acts:
                    x, y, w = a['button']['x'], a['button']['y'], a['_w']
                    d.rounded_rectangle([x / 100 * W, y / 100 * H, (x + w) / 100 * W, (y + 3.7) / 100 * H], radius=14, outline=(255, 0, 140), width=5)
                im.thumbnail((560, 760))
                im.save(os.path.join(folder, f'{book[-5:]}-{int(page):03}.jpg'), quality=82)
    for pages in out.values():
        for acts in pages.values():
            for a in acts:
                a.pop('_w')
    with open(os.path.join(ROOT, 'books', 'activities-maxford-videos.js'), 'w', encoding='utf-8') as f:
        f.write("// Generated by tools/make_maxford_video_buttons.py: the publisher's videos on their pages, as in Stemford English 3+.\n")
        f.write("// Loaded after the books' own activity files: adds the video buttons to their pages, and puts each letter's\n")
        f.write("// Formation video in its writing page's Write/Colour (\"How to write a\").\n")
        f.write('((acts, fillVideos) => {\n')
        f.write('  for (const [book, pages] of Object.entries(acts)) {\n')
        f.write('    const into = window.BOOK_ACTIVITIES[book] = window.BOOK_ACTIVITIES[book] || {};\n')
        f.write('    for (const [page, list] of Object.entries(pages)) into[page] = [].concat(into[page] || [], list);\n  }\n')
        f.write('  for (const [book, pages] of Object.entries(fillVideos)) for (const [page, video] of Object.entries(pages)) {\n')
        f.write("    const fill = [].concat(window.BOOK_ACTIVITIES[book]?.[page] || []).find(activity => activity.type === 'fill');\n")
        f.write('    if (fill) fill.video = video;\n  }\n})(')
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write(', ')
        json.dump(fills, f, ensure_ascii=False, indent=1)
        f.write(');\n')
    print('\n'.join(notes))
    print(sum(len(a) for p in out.values() for a in p.values()), 'buttons;', sum(len(p) for p in fills.values()), 'How to write videos')


if __name__ == '__main__':
    main('--show' in sys.argv)
