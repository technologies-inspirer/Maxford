"""A button for each of the publisher's videos, next to the part of the book it is about, like the Stemford books.

    python tools/make_maxford_video_buttons.py          # writes books/activities-maxford-videos.js
    python tools/make_maxford_video_buttons.py --show   # and an overlay of each page in tools/_video_buttons/

Only the books whose video lists the publisher gave (Qaida 3+ English, Maths and Urdu), and only the pages whose
printed QR code has those videos. Each video gets its own button, named by what it is ("Story", "Poem", "Formation";
in Urdu for the Urdu book), and put by what it is about: the story on the big picture, the poem by the printed poem,
the words by the word pictures, the formation by the "Formation Rhyme" of the next page (where the letter or number
is traced), the teachers' and parents' guides by the Teacher's Note. The pages of each kind share one design, so
each place is measured once per kind (SLOTS) and checked on every page with --show. The QR's "Watch this" stays.
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
    (r"poem|rhyme", 'poem', 'Poem', 'نظم', '🎵'),
    (r"words? .*writing", 'words', 'Words & Writing', 'الفاظ اور لکھائی', '✏️'),
    (r"formation|writing", 'formation', 'Formation', 'لکھائی', '✏️'),
    (r"vocabulary|words", 'words', 'Vocabulary', 'الفاظ', '🔤'),
    (r"objects", 'objects', 'Objects', 'چیزیں', '🍎'),
    (r"comparison|compare", 'compare', 'Compare', 'موازنہ', '⚖️'),
    (r"lesson", 'lesson', 'Lesson', 'سبق', '📚'),
]
# Where each kind of video goes, per book: kind -> (page offset, x, y) in % of the page (the button's top-left);
# a second button of the same place goes beside the first (to its left in the Urdu book). Page numbers as keys
# are pages with their own design.
TEACHER_NOTE = {'teachers': (0, 58, 94.6), 'parents': (0, 74.5, 94.6)}     # under the Teacher's Note, beside the page number
SLOTS = {
    'maxford-global-qaida-3-english': {None: {
        'story': (0, 44.5, 19.5),        # on the picture of the letter's story
        'poem': (0, 2.5, 40.3),          # before the "Phonic Poem" heading (the poem box is wider on some pages)
        'words': (0, 46, 62.4),          # beside "/a/ as in..." and its Play
        'formation': (1, 47, 7.8),       # over the next page's "Formation Rhyme", where the letter is traced
    }, '15': {'story': (0, 44.5, 19.5), 'poem': (0, 2.5, 36.3), 'words': (0, 46, 62.4), 'formation': (1, 47, 7.8)}},   # b: a taller poem box
    'maxford-global-qaida-3-maths': {
        None: {'story': (0, 45, 19.5),   # the number's picture
               'poem': (0, 29.5, 40.3),  # after the "Poem" heading
               'objects': (0, 35, 61.6),  # after "1 horse" ("4 elephants"), the things counted
               'formation': (1, 62, 8.3),  # over the next page's "Formation Rhyme", after its Write button
               **TEACHER_NOTE},
        '7': {'story': (0, 30, 13), 'poem': (0, 83, 17.8), 'compare': (0, 76, 44.3), **TEACHER_NOTE},   # big and small: over "small"
        '8': {'story': (0, 30, 13), 'lesson': (0, 14, 44.8), **TEACHER_NOTE},                          # more and less
    },
    'maxford-global-qaida-3-urdu': {None: {
        'story': (0, 44, 19.5),          # on the picture, its right corner
        'poem': (0, 63.5, 40.2),         # before the "صوتی نظم" heading
        'words': (0, 44, 62.2),          # under the picture, over the word pictures
        'formation': (1, 47, 7.8),       # over the next page's model letter, where it is written
        'teachers': (0, 2, 94.4), 'parents': (0, 16.5, 94.4),   # by the teachers' note
    }},
}
H = 3.3   # a button's height, % of the page height (the CSS .video-btn: about 4.1% of the page's width)


def library():
    text = open(os.path.join(ROOT, 'books', 'library.js'), encoding='utf-8').read()
    return json.loads(text.split('window.PDF_BOOKS = ', 1)[1].strip().rstrip(';'))


def other_buttons(book):
    """Where the pages' own buttons already are (games, exercise questions), as {page: [(x, y, w, h)]}."""
    out = {}
    for f in os.listdir(os.path.join(ROOT, 'books')):
        if not re.match(r'(activities|questions)-maxford', f) or 'videos' in f:
            continue
        text = open(os.path.join(ROOT, 'books', f), encoding='utf-8').read()
        m = re.search(r"\['%s'\] = (\{.*\});" % re.escape(book), text, re.S)
        if not m:
            continue
        for page, items in json.loads(m.group(1)).items():
            for it in items if isinstance(items, list) else [items]:
                b = it.get('button')
                if b:
                    out.setdefault(int(page), []).append((b['x'], b['y'], 15, H))
    return out


def kind_of(title):
    for pattern, kind, en, ur, icon in KINDS:
        if re.search(pattern, title, re.I):
            return kind, en, ur, icon
    return 'story', 'Video', 'ویڈیو', '▶️'


def width(label):
    """A button's width, % of the page width: the icon, the padding and the words."""
    return round(5.8 + 1.12 * len(label), 1)


def main(show):
    books = {b['id']: b for b in library()}
    out, notes, problems = {}, [], []
    for book, slots_of in SLOTS.items():
        b = books[book]
        urdu = bool(b.get('rtl'))
        taken = other_buttons(book)
        for page, item in sorted(b.get('qr', {}).items(), key=lambda kv: int(kv[0])):
            vids = item.get('videos', [])
            if not vids:
                continue
            slots = slots_of.get(page, slots_of[None])
            used = {}
            for v in vids:
                title = v.get('label') or v['title']
                kind, en, ur, icon = kind_of(title)
                if kind not in slots:
                    problems.append(f'{book} p{page}: no place for a {kind} video ({title})')
                    continue
                off, x, y = slots[kind]
                name = ur if urdu else en
                n = used.get((off, x, y), [])
                if any(o[0] == name for o in n):
                    name = f'{name} {len(n) + 1}'
                w = width(name)
                if n:   # beside the one already there
                    x = n[-1][1] - w - 1.2 if urdu else n[-1][1] + n[-1][2] + 1.2
                used.setdefault((off, slots[kind][1], y), []).append((name, x, w))
                target = str(int(page) + off)
                hit = [o for o in taken.get(int(target), []) if x < o[0] + o[2] and o[0] < x + w and y < o[1] + o[3] and o[1] < y + H]
                if hit:
                    problems.append(f'{book} p{target}: {name} overlaps a button at {hit}')
                out.setdefault(book, {}).setdefault(target, []).append({
                    'type': 'videos', 'label': name, 'icon': icon, 'title': title, 'button': {'x': round(x, 1), 'y': y},
                    'videos': [{'title': title, 'src': 'https://youtu.be/' + v['id']}], '_w': w})
            notes.append(f'{book} p{page}: {len(vids)} videos')
    if show:
        folder = os.path.join(ROOT, 'tools', '_video_buttons')
        os.makedirs(folder, exist_ok=True)
        for f in os.listdir(folder):
            os.remove(os.path.join(folder, f))
        for book, pages in out.items():
            for page, acts in pages.items():
                im = Image.open(os.path.join(ROOT, books[book]['dir'], 'p%03d.jpg' % int(page))).convert('RGB')
                d, (W, Hp) = ImageDraw.Draw(im), im.size
                for a in acts:
                    x, y, w = a['button']['x'], a['button']['y'], a['_w']
                    d.rounded_rectangle([x / 100 * W, y / 100 * Hp, (x + w) / 100 * W, (y + H) / 100 * Hp], radius=12, outline=(255, 0, 140), width=5)
                im.thumbnail((560, 760))
                im.save(os.path.join(folder, f'{book[-5:]}-{int(page):03}.jpg'), quality=82)
    for pages in out.values():
        for acts in pages.values():
            for a in acts:
                a.pop('_w')
    with open(os.path.join(ROOT, 'books', 'activities-maxford-videos.js'), 'w', encoding='utf-8') as f:
        f.write("// Generated by tools/make_maxford_video_buttons.py: a button for each of the publisher's videos, by what it is about.\n")
        f.write("// Loaded after the books' own activity files, so it adds to their pages.\n")
        f.write('(acts => {\n  for (const [book, pages] of Object.entries(acts)) {\n')
        f.write('    const into = window.BOOK_ACTIVITIES[book] = window.BOOK_ACTIVITIES[book] || {};\n')
        f.write('    for (const [page, list] of Object.entries(pages)) into[page] = [].concat(into[page] || [], list);\n  }\n})(')
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write(');\n')
    print('\n'.join(problems) or 'no problems')
    print(len(notes), 'pages with videos,', sum(len(a) for p in out.values() for a in p.values()), 'buttons on', sum(len(p) for p in out.values()), 'pages')


if __name__ == '__main__':
    main('--show' in sys.argv)
