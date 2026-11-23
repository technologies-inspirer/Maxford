"""The printed exercises of Maxford Global Qaida 3+ Maths as questions (app.js openQuestion).

Positions come from the PDF itself: every picture is its own image and every box, grid cell, outline and
heading is its own vector shape, so the generator finds them on each page instead of measuring by hand.
Writes books/questions-maxford-maths.js.

    python tools/make_maxford_maths.py
"""
import json
import os
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from import_pdf import blank
from make_maxford_questions import C, MANY, Q, box, choose, colour, match, place_buttons, tap, write

BOOK = 'maxford-global-qaida-3-maths'
PDF = r'D:\pdf\Maxford Global QAIDA 3+ MATHS (112 Pgs) (8.87 X 11.25) (2026-27) Final Curve.pdf'
TEXT = '#221e1f'        # the book's dark text colour: headings are shapes of this colour

doc = pymupdf.open(PDF)
pdf_pages = [page for page in doc if not blank(page)]      # book page n is pdf_pages[n - 1]


class Page:
    """Pictures (k='img') and drawn shapes (k='shape') of one book page, each with a box [x, y, w, h] in % of the page."""

    def __init__(self, n):
        self.n = n
        pg = pdf_pages[n - 1]
        W, H = pg.rect.width, pg.rect.height
        pct = lambda r: [round(r.x0 / W * 100, 2), round(r.y0 / H * 100, 2), round(r.width / W * 100, 2), round(r.height / H * 100, 2)]
        self.parts, seen = [], set()
        for info in pg.get_image_info():
            r = pymupdf.Rect(info['bbox']) & pg.rect
            b = pct(r)
            if b[2] < 90 and b[3] < 90 and ('img', tuple(b)) not in seen:
                seen.add(('img', tuple(b)))
                self.parts.append({'k': 'img', 'b': b})
        for dr in pg.get_drawings():
            b = pct(dr['rect'])
            col = dr.get('fill') or dr.get('color')
            c = '#%02x%02x%02x' % tuple(int(v * 255) for v in col) if col else None
            if b[2] < 90 and b[3] < 60 and ('shape', tuple(b), c) not in seen:
                seen.add(('shape', tuple(b), c))
                self.parts.append({'k': 'shape', 'b': b, 'c': c, 'fill': bool(dr.get('fill')), 'n': len(dr['items'])})

    def headings(self):
        """Lines of dark text that start near the left margin (the instructions), top to bottom: [x0, y0, x1, y1]."""
        text = [p['b'] for p in self.parts if p['k'] == 'shape' and p['c'] == TEXT and 1 < p['b'][3] < 3 and p['b'][1] > 8]
        lines = []
        for x, y, w, h in sorted(text, key=lambda b: b[1]):
            line = next((l for l in lines if abs((l[1] + l[3]) / 2 - (y + h / 2)) < 1), None)
            if line:
                line[0], line[1], line[2], line[3] = min(line[0], x), min(line[1], y), max(line[2], x + w), max(line[3], y + h)
            else:
                lines.append([x, y, x + w, y + h])
        return [l for l in lines if l[0] < 16 and l[2] - l[0] > 10 and l[1] < 87.5]   # below: the teacher's note

    def heading(self, i):
        return self.headings()[i]

    def band(self, i):
        """The page between heading i and the next heading (or the teacher's note at the bottom)."""
        hs = self.headings()
        top = hs[i][3]
        bottom = hs[i + 1][1] if i + 1 < len(hs) else 90
        return [0, top, 100, bottom - top]

    def find(self, area, kind='shape', w=(0, 100), h=(0, 100), colour=None, fill=None, items=None):
        x, y, aw, ah = area
        out = []
        for p in self.parts:
            bx, by, bw, bh = p['b']
            if p['k'] != kind or not (w[0] <= bw <= w[1] and h[0] <= bh <= h[1]):
                continue
            if not (x - .3 <= bx and bx + bw <= x + aw + .3 and y - .3 <= by and by + bh <= y + ah + .3):
                continue
            if colour and p.get('c') != colour:
                continue
            if fill is not None and p.get('fill') != fill:
                continue
            if items is not None and p.get('n') != items:
                continue
            if not any(abs(bx - o[0]) < .4 and abs(by - o[1]) < .4 and abs(bw - o[2]) < .4 and abs(bh - o[3]) < .4 for o in out):
                out.append(p['b'])
        return sorted(out, key=lambda b: (round(b[1] / 2), b[0]))

    def objects(self, area, min_size=2.5, **kw):
        """Outlined pictures in an area: overlapping shapes joined into one box each."""
        boxes = [b for b in self.find(area, **kw) if max(b[2], b[3]) >= min_size]
        merged = []
        for b in sorted(boxes, key=lambda b: -b[2] * b[3]):
            for m in merged:
                if b[0] < m[0] + m[2] and m[0] < b[0] + b[2] and b[1] < m[1] + m[3] and m[1] < b[1] + b[3]:
                    x0, y0 = min(m[0], b[0]), min(m[1], b[1])
                    m[2], m[3] = max(m[0] + m[2], b[0] + b[2]) - x0, max(m[1] + m[3], b[1] + b[3]) - y0
                    m[0], m[1] = x0, y0
                    break
            else:
                merged.append(list(b))
        return sorted(merged, key=lambda b: (round(b[1] / 4), b[0]))


def blobs(n, area, expected, min_area=0.08, blank=(), specks=True):
    """The separate pictures in an area of page n's image, found as joined patches of ink; the join distance is
    raised until there are exactly `expected` of them (the number on the page says how many there are)."""
    import cv2
    import numpy as np
    im = cv2.imread(str(Path(__file__).resolve().parents[1] / f'books/{BOOK}/p{n:03d}.jpg'))
    H, W = im.shape[:2]
    x, y, w, h = area
    x0, y0, x1, y1 = int(x * W / 100), int(y * H / 100), int((x + w) * W / 100), int((y + h) * H / 100)
    sub = im[y0:y1, x0:x1].astype(int)
    ink = ((sub.max(axis=2) - sub.min(axis=2) > 40) | (sub.sum(axis=2) < 600)).astype(np.uint8)
    for bx, by, bx1, by1 in blank:     # e.g. the heading's words, when pictures sit beside it
        ink[max(0, int(by * H / 100) - y0 - 2):max(0, int(by1 * H / 100) - y0 + 2), max(0, int(bx * W / 100) - x0 - 2):max(0, int(bx1 * W / 100) - x0 + 2)] = 0
    tried = []
    for join in range(1, 40, 2):
        m = cv2.dilate(ink, np.ones((join, join), np.uint8))
        k, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
        boxes = []
        for i in range(1, k):
            bx, by, bw, bh, a = stats[i]
            if bw * bh / (W * H) * 100 >= min_area:
                boxes.append([(x0 + bx + join // 2) / W * 100, (y0 + by + join // 2) / H * 100, (bw - join) / W * 100, (bh - join) / H * 100])
        if boxes and specks:     # specks (sprinkles, a stray mark) are much smaller than the pictures
            typical = sorted(b[2] * b[3] for b in boxes)[len(boxes) * 3 // 4]
            boxes = [b for b in boxes if b[2] * b[3] >= typical * .3]
        if boxes and len(boxes) < expected:
            # pictures printed touching each other join into one patch two or three pictures tall (or wide): split it
            med_h = sorted(b[3] for b in boxes)[len(boxes) // 2]
            med_w = sorted(b[2] for b in boxes)[len(boxes) // 2]
            split = []
            for b in boxes:
                ky, kx = max(1, round(b[3] / med_h * 1.15 - .15)), max(1, round(b[2] / med_w * 1.15 - .15))
                for i in range(ky):
                    for j in range(kx):
                        split.append([b[0] + j * b[2] / kx, b[1] + i * b[3] / ky, b[2] / kx, b[3] / ky])
            if len(split) == expected:
                boxes = split
        tried.append(len(boxes))
        if len(boxes) == expected:
            return [rnd(b) for b in sorted(boxes, key=lambda b: (round(b[1] / 6), b[0]))]
    raise AssertionError(f'page {n}: wanted {expected} pictures in {area}, found {tried}')


def pictures_in(pg, area, expected, blank=()):
    """The pictures to colour: found in the page image, or else as the PDF's drawn outlines, whichever gives the expected count."""
    try:
        return blobs(pg.n, area, expected, blank=blank)
    except AssertionError as e:
        for fill in (False, None):
            objs = pg.objects([0, area[1], 100, area[3]], min_size=2.5, fill=fill)
            if len(objs) == expected:
                return [rnd(b) for b in objs]
        raise e


def rnd(b):
    return [round(v, 2) for v in b]


def union(boxes, pad=1.5):
    x0 = min(b[0] for b in boxes) - pad
    y0 = min(b[1] for b in boxes) - pad
    x1 = max(b[0] + b[2] for b in boxes) + pad
    y1 = max(b[1] + b[3] for b in boxes) + pad
    x0, y0 = max(x0, 0), max(y0, 0)
    return rnd([x0, y0, min(x1, 100) - x0, min(y1, 100) - y0])


def after(pg, i):
    """Where a heading's button goes: just after its last word, on its line."""
    x0, y0, x1, y1 = pg.heading(i)
    return (round(x1 + 2.5, 2), round((y0 + y1) / 2, 2))


def title_of(i, pg, text):
    return text


# ---------- page types ----------
def grid_cells(pg, area, size=(4, 16)):
    """The cells of a tracing grid (rectangles of one size), and the bigger example cell(s) if any."""
    return [rnd(b) for b in pg.find(area, w=(size[0], 25), h=size, colour='#ffffff', items=1)]


def trace_grid(pg, i, title, say='Trace each number, then write it in the empty boxes.', size=(4, 16), extra=()):
    area = pg.band(i)
    cells = grid_cells(pg, area, size) + [rnd(b) for b in extra]
    assert len(cells) >= 6, (pg.n, title, len(cells))
    return write(title, say, after(pg, i), union(cells), cells)


def colour_objects(pg, i, title, say, names_colours, min_size=2.5, area=None, objects=None):
    """names_colours: one (name, colours) per object, in reading order; or a single (name, colours) for all of them."""
    objs = objects or pg.objects(area or pg.band(i), min_size=min_size, fill=False)
    if isinstance(names_colours, tuple):
        names_colours = [names_colours] * len(objs)
    assert len(objs) == len(names_colours), (pg.n, title, len(objs), len(names_colours), objs)
    parts = [(name, tuple(rnd(b)), cols) for b, (name, cols) in zip(objs, names_colours)]
    return colour(title, say, after(pg, i), union(objs), parts)


NUMBER_WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve',
                'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty']

Q_PAGES = {}
NOTES = []      # printing mistakes found while building


def page(n):
    def wrap(f):
        Q_PAGES[n] = f
        return f
    return wrap


def build():
    out = {}
    for n, f in sorted(Q_PAGES.items()):
        qs = [q for q in f(Page(n)) if q]
        place_buttons(qs)
        out[str(n)] = qs
    return out


# ---------- numbers 1 to 10: count and trace, then colour the number and the objects ----------
COUNT_TRACE = {   # page: (number, the objects to colour in reading order, the number's outline first)
    10: (1, [('car', [C['red'], C['blue'], C['black']])]),
    14: (2, [('ball', [C['red'], C['blue'], C['green'], C['yellow']])] * 2),
    18: (3, [('apple', [C['red'], C['green']])] * 3),
    22: (4, [('pencil', MANY)] * 4),
    28: (5, [('fish', [C['orange'], C['blue'], C['green'], C['yellow']])] * 5),
    34: (6, [('butterfly', MANY)] * 6),
    40: (7, [('star', [C['yellow'], C['red'], C['orange']])] * 7),
    44: (8, [('leaf', [C['green'], C['leaf']])] * 8),
    48: (9, [('strawberry', [C['red'], C['green']])] * 9),
}
FINGERS = {11: 1, 15: 2, 19: 3, 23: 4, 29: 5, 35: 6, 41: 7, 45: 8, 49: 9, 59: 10}
TRACE_11_20 = {   # page: (number, the objects to colour)
    66: (11, ('pear', [C['green'], C['yellow'], C['brown']])),
    69: (12, ('balloon', MANY)),
    72: (13, ('banana', [C['yellow'], C['green'], C['brown']])),
    75: (14, ('cap', MANY)),
    78: (15, ('ball', MANY)),
    85: (16, ('doughnut', [C['pink'], C['light brown'], C['brown'], C['yellow']])),
    88: (17, ('cupcake', MANY + [C['light brown'], C['brown']])),
    91: (18, ('mug', MANY)),
    94: (19, ('star', [C['yellow'], C['orange']])),
    97: (20, ('candy', MANY)),
}


def make_count_trace(n, number, objects):
    @page(n)
    def _(pg):
        x, y, w, h = pg.band(1)
        objs = pictures_in(pg, [4, y + .4, 92, h - .4], number + 1)
        return [trace_grid(pg, 0, 'Count and trace the number.', f'Count the dots. Trace the number {number} in every box.'),
                colour_objects(pg, 1, 'Colour the number and the objects.', f'Colour the number {number} and the {objects[0][0]}{"s" if number > 1 else ""}.',
                               [(f'number {number}', MANY)] + objects, objects=objs)]


for n, (number, objects) in COUNT_TRACE.items():
    make_count_trace(n, number, objects)


def make_fingers(n, number):
    @page(n)
    def _(pg):
        return [trace_grid(pg, 0, 'Count on fingers then trace and write the number.',
                           f'Show {number} on your fingers. Trace the number {number}, then write it in the empty boxes.', size=(4, 18))]


for n, number in FINGERS.items():
    make_fingers(n, number)


def make_trace_11_20(n, number, objects):
    @page(n)
    def _(pg):
        return [trace_grid(pg, 0, 'Trace and write the number.', f'Trace the number {number}, then write it in the empty boxes.', size=(4, 18)),
                colour_objects(pg, 1, 'Count and colour the objects.', f'Count the {objects[0]}s. Colour all {number} of them.', objects,
                               objects=pictures_in(pg, [4, pg.heading(1)[1], 92, pg.band(1)[3] + pg.heading(1)[3] - pg.heading(1)[1]], number, blank=[pg.heading(1)]))]


for n, (number, objects) in TRACE_11_20.items():
    make_trace_11_20(n, number, objects)


# ---------- shared exercises ----------
def numbers_in(pg, area, count, min_h=2.5):
    """The printed numbers in an area, in reading order: digit shapes side by side joined into one number."""
    glyphs = [b for b in pg.find(area, h=(min_h, 12), w=(.3, 12)) if b[2] < 12]
    glyphs = [g for g in glyphs if not any(o is not g and o[0] <= g[0] and o[1] <= g[1] and g[0] + g[2] <= o[0] + o[2] + .01
                                            and g[1] + g[3] <= o[1] + o[3] + .01 and o[2] * o[3] > g[2] * g[3] for o in glyphs)]
    nums = []
    for g in sorted(glyphs, key=lambda b: (round((b[1] + b[3] / 2) / 3), b[0])):
        last = nums[-1] if nums else None
        if last and abs((last[1] + last[3] / 2) - (g[1] + g[3] / 2)) < 2.5 and g[0] - (last[0] + last[2]) < 1.6:
            x0, y0 = min(last[0], g[0]), min(last[1], g[1])
            last[2], last[3] = max(last[0] + last[2], g[0] + g[2]) - x0, max(last[1] + last[3], g[1] + g[3]) - y0
            last[0], last[1] = x0, y0
        else:
            nums.append(list(g))
    assert len(nums) == count, (pg.n, area, len(nums), nums)
    return [rnd(b) for b in nums]


def number_blobs(n, area, expected, gap=.75):
    """Printed numbers in an area: each digit found in the image, then digits side by side (closer than `gap`
    times their height) joined into one number."""
    import cv2
    import numpy as np
    im = cv2.imread(str(Path(__file__).resolve().parents[1] / f'books/{BOOK}/p{n:03d}.jpg'))
    H, W = im.shape[:2]
    x, y, w, h = area
    x0, y0, x1, y1 = int(x * W / 100), int(y * H / 100), int((x + w) * W / 100), int((y + h) * H / 100)
    sub = im[y0:y1, x0:x1].astype(int)
    ink = ((sub.max(axis=2) - sub.min(axis=2) > 40) | (sub.sum(axis=2) < 600)).astype(np.uint8)
    ink = cv2.dilate(ink, np.ones((3, 3), np.uint8))
    k, lab, stats, _ = cv2.connectedComponentsWithStats(ink, 8)
    digits = [list(map(int, stats[i][:4])) for i in range(1, k) if stats[i][3] > H * .015]
    rows = []        # digits whose middles are at about the same height make a row
    for d in sorted(digits, key=lambda d: d[1] + d[3] / 2):
        if rows and abs(rows[-1][0] - (d[1] + d[3] / 2)) < d[3] * .5:
            rows[-1][1].append(d)
        else:
            rows.append([d[1] + d[3] / 2, [d]])
    digits = [d for _, row in rows for d in sorted(row, key=lambda d: d[0])]

    def group(gap):
        nums = []
        for d in digits:
            last = nums[-1] if nums else None
            if last and abs((last[1] + last[3] / 2) - (d[1] + d[3] / 2)) < d[3] * .5 and d[0] - (last[0] + last[2]) < gap * d[3] \
                    and abs(last[3] - d[3]) < .12 * d[3]:     # digits of one number are the same size
                nx0, ny0 = min(last[0], d[0]), min(last[1], d[1])
                last[2], last[3] = max(last[0] + last[2], d[0] + d[2]) - nx0, max(last[1] + last[3], d[1] + d[3]) - ny0
                last[0], last[1] = nx0, ny0
            else:
                nums.append(list(d))
        return nums

    # the widest gap inside a number that still keeps the numbers apart: try from wide to narrow
    nums = next((g for g in (group(k / 20) for k in range(16, 3, -1)) if len(g) == expected), group(gap))
    out = [rnd([(x0 + b[0]) / W * 100, (y0 + b[1]) / H * 100, b[2] / W * 100, b[3] / H * 100]) for b in nums]
    assert len(out) == expected, (n, area, len(out), out)
    return out


def count_pictures(n, area):
    """How many separate pictures there are in an area of the page image (for groups drawn as one picture)."""
    import cv2
    import numpy as np
    im = cv2.imread(str(Path(__file__).resolve().parents[1] / f'books/{BOOK}/p{n:03d}.jpg'))
    H, W = im.shape[:2]
    x, y, w, h = area
    sub = im[int(y * H / 100):int((y + h) * H / 100), int(x * W / 100):int((x + w) * W / 100)].astype(int)
    ink = ((sub.max(axis=2) - sub.min(axis=2) > 40) | (sub.sum(axis=2) < 600)).astype(np.uint8)
    ink = cv2.dilate(ink, np.ones((5, 5), np.uint8))
    k, lab, stats, _ = cv2.connectedComponentsWithStats(ink, 8)
    areas = sorted(stats[i][4] for i in range(1, k))
    typical = areas[len(areas) * 3 // 4] if areas else 0
    return len([a for a in areas if a >= typical * .3])


def find_and_circle(pg, i, number, values):
    x, y, w, h = pg.band(i)
    nums = number_blobs(pg.n, [2, y + .3, 96, h - .3], len(values))
    options = [{'x': b[0] - .8, 'y': b[1] - .8, 'w': b[2] + 1.6, 'h': b[3] + 1.6, 'correct': v == number, 'label': str(v)}
               for b, v in zip(nums, values)]
    options = [{k: round(v, 2) if isinstance(v, float) else v for k, v in o.items()} for o in options]
    return choose(f'Find and circle the number {number}.', f'Find every {number}. Tap each one to circle it.', after(pg, i), union(nums), options)


def tick_group(pg, i, number, title=None, frames=None):
    """Groups of pictures in frames, each with a small box under it: tick the box of the group with `number` pictures."""
    area = pg.band(i)
    frames = frames or [b for b in pg.find(area, w=(20, 60), h=(8, 30))]
    frames = [f for f in frames if not any(o is not f and abs(o[0] - f[0]) < .5 and abs(o[1] - f[1]) < .5 for o in frames[:frames.index(f)])]
    boxes = pg.find(area, w=(3, 9), h=(3, 7))
    options = []
    for k, f in enumerate(frames):
        n = GROUP_COUNTS[pg.n][k] if pg.n in GROUP_COUNTS else len([b for b in pg.find(f, kind='img') if b[2] < f[2] * .8]) or count_pictures(pg.n, [f[0] + .8, f[1] + .8, f[2] - 1.6, f[3] - 1.6])
        under = min(boxes, key=lambda b: abs(b[0] + b[2] / 2 - (f[0] + f[2] / 2)) + abs(b[1] - (f[1] + f[3])))
        options.append({'x': under[0], 'y': under[1], 'w': under[2], 'h': under[3], 'correct': n == number, 'label': f'{n} pictures'})
    if sum(o['correct'] for o in options) != 1:     # a printing mistake: no group (or two) has that many
        NOTES.append(f'page {pg.n}: "{title or f"Tick the group with {number} objects."}" left out - the groups have {" and ".join(o["label"] for o in options)}')
        return None
    return choose(title or f'Tick the group with {number} objects.', f'Count the pictures in each group. Tap the box under the group with {number}.',
                  after(pg, i), union(frames + [[o['x'], o['y'], o['w'], o['h']] for o in options]), options)


def count_trace_write(pg, i, number, title='Count, trace and write the number.'):
    """The picture to count, and two boxes beside it: trace the number in the first, write it in the second."""
    area = pg.band(i)
    boxes = pg.find([70, area[1], 30, area[3]], w=(6, 14), h=(5, 10))
    boxes = [b for b in boxes if not any(o is not b and abs(o[0] - b[0]) < 1 and abs(o[1] - b[1]) < 1 for o in boxes[:boxes.index(b)])]
    assert len(boxes) == 2, (pg.n, boxes)
    pictures = [b for b in pg.find(area, kind='img')] or [[8, area[1] + 1, 60, area[3] - 2]]
    return write(title, f'Count the pictures. Trace the number {number} in the first box, then write it in the second box.',
                 after(pg, i), union(pictures + boxes), [rnd(b) for b in boxes])


# groups whose pictures touch, so the counting is done by eye (left group, right group)
GROUP_COUNTS = {95: [19, 18], 98: [18, 20]}

ACT_11_20 = {   # page: (number, the numbers of "Find and circle" in reading order)
    67: (11, [11, 12, 11, 13, 11, 10, 9, 11, 15, 11, 10, 11]),
    70: (12, [10, 12, 10, 12, 10, 12, 12, 10, 12, 10, 10, 12]),
    73: (13, [13, 12, 10, 13, 10, 13, 9, 13, 15, 10, 13, 11]),
    76: (14, [10, 14, 10, 13, 14, 14, 9, 10, 14, 10, 14, 11]),
    79: (15, [15, 12, 15, 13, 10, 15, 9, 15, 15, 15, 10, 11]),
    86: (16, [16, 12, 16, 13, 16, 16, 9, 16, 15, 6, 10, 16]),
    89: (17, [12, 17, 10, 17, 13, 17, 17, 10, 17, 14, 17, 11]),
    92: (18, [18, 18, 10, 18, 13, 18, 17, 12, 18, 14, 18, 11]),
    95: (19, [13, 19, 16, 19, 19, 11, 9, 12, 19, 18, 10, 19]),
    98: (20, [20, 12, 20, 13, 10, 20, 9, 20, 15, 20, 10, 11]),
}


def make_act_11_20(n, number, values):
    @page(n)
    def _(pg):
        return [tick_group(pg, 0, number), count_trace_write(pg, 1, number), find_and_circle(pg, 2, number, values)]


for n, (number, values) in ACT_11_20.items():
    make_act_11_20(n, number, values)


# ---------- pages with their own layout ----------
def opt(b, correct, label, pad=.8):
    return {'x': round(b[0] - pad, 2), 'y': round(b[1] - pad, 2), 'w': round(b[2] + 2 * pad, 2), 'h': round(b[3] + 2 * pad, 2),
            'correct': correct, 'label': label}


def marked(kind, title, say, button, crop, options):
    """A tap exercise whose answer gets the printed mark: kind 'tick' (✓), 'cross' (✗) or None (a ring)."""
    q = choose(title, say, button, crop, options)
    if kind:
        q['mark'] = kind
        q['label'] = 'Tick' if kind == 'tick' else 'Cross'     # the button says what to do
    return q


def boxes_of(options):
    return [[o['x'], o['y'], o['w'], o['h']] for o in options]


def tick_and_cross(tick_title, cross_title, tick_say, cross_say, buttons, pictures, circles, tick_i, cross_i, labels):
    """'Tick (✓) the ... and cross (✗) the ...': two exercises on the same answer circles."""
    crop = union(pictures + circles)
    tick = marked('tick', tick_title, tick_say, buttons[0], crop, [opt(c, k == tick_i, labels[k]) for k, c in enumerate(circles)])
    cross = marked('cross', cross_title, cross_say, buttons[1], crop, [opt(c, k == cross_i, labels[k]) for k, c in enumerate(circles)])
    return [tick, cross]


@page(3)
def _(pg):
    nums = [[15.1, 17.1, 3.8, 18.7], [54.2, 16.6, 14.7, 18.5], [9.9, 43.0, 15.0, 19.2], [53.7, 43.5, 14.4, 19.6], [13.6, 70.6, 16.0, 19.3]]
    return [write('Touch and feel the numbers with objects.', 'Trace each big number with your finger, following the arrows. Say the number and count its pictures.',
                  (43, 94.5), union(nums), nums)]


@page(4)
def _(pg):
    nums = [[10.0, 17.1, 16.8, 19.7], [52.4, 16.8, 15.7, 19.3], [9.7, 43.6, 16.6, 18.8], [53.1, 41.1, 14.3, 20.8], [10.4, 70.6, 23.4, 19.2]]
    return [write('Touch and feel the numbers with objects.', 'Trace each big number with your finger, following the arrows. Say the number and count its pictures.',
                  (43, 94.5), union(nums), nums)]


@page(5)
def _(pg):
    rows = [[8.7, 14.0, 83.6, 8.5], [8.7, 23.5, 83.6, 21.5], [8.7, 46.8, 83.6, 39.8]]
    return [write('Trace.', 'Trace each dotted line from the red dot, without lifting your pencil.', (17, 10.4), union(rows, .5), rows)]


@page(6)
def _(pg):
    rows = [[8.9, 13.5, 83.2, 32.5], [8.9, 46.5, 83.2, 28.5], [8.9, 76.5, 83.2, 10.5]]
    return [write('Trace.', 'Trace each circle and the wavy line from the red dot.', (17, 10.4), union(rows, .5), rows)]


@page(7)
def _(pg):
    return tick_and_cross('Tick (✓) the big house.', 'Cross (✗) the small house.', 'Which house is big? Tap its circle to tick it.',
                          'Which house is small? Tap its circle to cross it.', [(81.6, 59.5), (84.5, 64)],
                          [[21.6, 62.5, 34.6, 27.8], [64.0, 73.2, 21.3, 16.3]], [[14.9, 77.7, 6.7, 5.2], [79.8, 72.5, 6.7, 5.2]], 0, 1, ['big house', 'small house'])


@page(8)
def _(pg):
    return tick_and_cross('Tick (✓) the box with more objects.', 'Cross (✗) the box with less objects.', 'Which box has more balls? Tap its circle to tick it.',
                          'Which box has less balls? Tap its circle to cross it.', [(81.3, 60.3), (84.5, 64.2)],
                          [[16.1, 65.4, 35.4, 18.5], [57.4, 65.4, 27.6, 18.5]], [[30.2, 80.5, 7.2, 5.7], [67.6, 80.3, 7.2, 5.7]], 0, 1, ['more', 'less'])


def tick_boxes(pg, i, title, say, boxes, correct, labels, kind='tick', pictures=()):
    return marked(kind, title, say, after(pg, i), union(list(pictures) + boxes), [opt(b, k in correct, labels[k]) for k, b in enumerate(boxes)])


def colour_ten_frame(pg, i, count, things, frame_area):
    cells = [rnd(b) for b in pg.find(frame_area, w=(4, 6.5), h=(3, 5), colour='#ffffff', items=1)]
    assert len(cells) == 10, (pg.n, len(cells))
    return colour(f'Colour one box for each {things[:-1] if things.endswith("s") else things}.', f'Count the {things}. Colour one box for each: {count} boxes.',
                  after(pg, i), union(cells + [[frame_area[0], frame_area[1], 1, 1]]), [(f'box {k + 1}', tuple(b), MANY) for k, b in enumerate(cells)])


def colour_numbers(pg, i, number, keep):
    """'Colour the number N': the outlined numbers in a row; only those that are N can be coloured."""
    area = pg.band(i)
    outlines = pg.find(area, w=(2, 20), h=(10, 20), fill=False)
    outlines = [b for b in outlines if not any(o is not b and abs(o[0] - b[0]) < .3 and abs(o[1] - b[1]) < .3 for o in outlines[:outlines.index(b)])]
    chosen = [rnd(b) for b in sorted(outlines, key=lambda b: b[0]) if keep(b)]
    return colour(f'Colour the number {number}.', f'Find every {number} in the row and colour it. Do not colour the other numbers.',
                  after(pg, i), union(chosen), [(f'number {number}', tuple(b), MANY) for b in chosen])


@page(12)
def _(pg):
    houses = blobs(12, [25, 74, 70, 15], 3)
    return [tick_boxes(pg, 0, 'Tick the tree with 1 apple.', 'Count the apples on each tree. Tap the box of the tree with 1 apple.',
                       [[27.8, 28.4, 5.2, 4.1], [57.4, 28.4, 5.2, 4.1], [87.0, 28.4, 5.2, 4.1]], {1}, ['no apple', '1 apple', '2 apples'], pictures=[[8.2, 11.8, 85.6, 23.8]]),
            count_trace_write(pg, 1, 1),
            colour('Colour 1 house.', 'Colour the number 1 and one house.', after(pg, 2), union(houses + [[11.6, 75.0, 2.3, 11.4]]),
                   [('number 1', (11.6, 75.0, 2.3, 11.4), MANY)] + [('house', tuple(h), [C['red'], C['blue'], C['yellow'], C['brown']]) for h in houses])]


@page(16)
def _(pg):
    return [colour_ten_frame(pg, 0, 2, 'bees', [60, 15, 35, 15]),
            count_trace_write(pg, 1, 2),
            colour_numbers(pg, 2, 2, lambda b: b[2] > 6)]


def tick_counted(pg, i, number, title, say, frames, boxes, kind='tick'):
    """Groups in frames, a box under each: tick every group that has `number` pictures (counted from the PDF)."""
    options = []
    for f, b in zip(frames, boxes):
        n = len([p for p in pg.find(f, kind='img') if p[2] < f[2] * .8])
        options.append(opt(b, n == number, f'{n} pictures'))
    assert any(o['correct'] for o in options), (pg.n, [o['label'] for o in options])
    return marked(kind, title, say, after(pg, i), union(frames + boxes), options)


@page(20)
def _(pg):
    glasses = [[31.5, 79.3, 13, 10], [49.3, 79.3, 13, 10], [65.3, 79.3, 13, 10], [81.3, 79.3, 13, 10]]    # they stand on one blue stripe
    return [tick_boxes(pg, 0, 'Tick the groups with 3 objects.', 'Count each group. Tap the box under every group with 3.',
                       [[18.3, 27.9, 6.3, 5.0], [47.1, 27.9, 6.3, 5.0], [75.7, 27.9, 6.3, 5.0]], {0, 2}, ['3 carrots', '1 pepper', '3 tomatoes'],
                       pictures=[[7.5, 13.4, 85, 17.3]]),
            count_trace_write(pg, 1, 3),
            colour('Colour 3 glasses.', 'Trace and colour the number 3. Then colour 3 glasses.', after(pg, 2), union(glasses + [[9.6, 74.5, 9.0, 11.6]]),
                   [('number 3', (9.6, 74.5, 9.0, 11.6), MANY)] + [('glass', tuple(g), [C['blue'], C['grey'], C['purple']]) for g in glasses])]


@page(24)
def _(pg):
    flowers = [[31.5, 75.5, 11, 11], [44.2, 75.5, 11, 11], [56.9, 75.5, 11, 11], [69.6, 75.5, 11, 11], [82.3, 75.5, 11, 11]]
    return [colour_ten_frame(pg, 0, 4, 'snails', [60, 15, 35, 15]),
            count_trace_write(pg, 1, 4),
            colour('Colour 4 flowers.', 'Trace and colour the number 4. Then colour 4 flowers.', after(pg, 2), union(flowers + [[9.8, 74.3, 8.7, 11.8]]),
                   [('number 4', (9.8, 74.3, 8.7, 11.8), MANY)] + [('flower', tuple(f), [C['yellow'], C['orange'], C['red'], C['pink']]) for f in flowers])]


@page(25)
def _(pg):
    pics, circles = [[9.3, 64.2, 51.0, 26.3], [59.0, 71.9, 34.6, 18.6]], [[9.3, 64.4, 6.7, 5.2], [84.3, 71.6, 6.7, 5.2]]
    crop = union(pics + circles)
    return [marked('tick', 'Tick (✓) the long vehicle.', 'Which vehicle is long? Tap its circle to tick it.', (78, 59.7), crop,
                   [opt(circles[0], True, 'bus'), opt(circles[1], False, 'car')]),
            marked(None, 'Circle the short one.', 'Which vehicle is short? Tap its circle.', (84.5, 64.2), crop,
                   [opt(circles[0], False, 'bus'), opt(circles[1], True, 'car')])]


@page(26)
def _(pg):
    pics = [[12.3, 61.4, 17.1, 27.8], [33.5, 77.3, 9.2, 11.2], [62.0, 72.0, 8.2, 17.0], [71.4, 63.0, 12.9, 26.3]]
    circles = [[10.8, 71.6, 6.7, 5.2], [42.0, 76.4, 6.7, 5.2], [54.7, 76.4, 6.7, 5.2], [84.8, 76.4, 6.7, 5.2]]
    names = ['giraffe', 'monkey', 'short lamp', 'tall lamp']
    crop = union(pics + circles)
    return [marked('tick', 'Tick (✓) the tall one in each pair.', 'In each pair, which one is tall? Tap its circle to tick it.', (31, 63.5), crop,
                   [opt(c, k in (0, 3), names[k]) for k, c in enumerate(circles)]),
            marked('cross', 'Cross (✗) the short one in each pair.', 'In each pair, which one is short? Tap its circle to cross it.', (31, 68), crop,
                   [opt(c, k in (1, 2), names[k]) for k, c in enumerate(circles)])]


@page(30)
def _(pg):
    fives = [[9.7, 75.1, 11.5, 13.9], [38.3, 75.1, 11.5, 13.9], [66.8, 75.1, 11.5, 13.9]]
    return [colour_ten_frame(pg, 0, 5, 'leaves', [60, 15, 35, 15]),
            count_trace_write(pg, 1, 5),
            colour('Colour the number 5.', 'Find every 5 in the row and colour it. Do not colour the other numbers.', after(pg, 2), union(fives),
                   [('number 5', tuple(b), MANY) for b in fives])]


def third(row, k, of=3):
    x, y, w, h = row
    return [round(x + k * w / of, 2), y, round(w / of, 2), h]


@page(31)
def _(pg):
    # each group's printed numbers, and which of them is the count: 3 bananas, 5 fish, 4 dolls, 2 lamps
    answers = [third([16.5, 32.5, 23.3, 5.8], 2), third([59.0, 32.5, 26.5, 5.8], 2), third([16.4, 63.3, 26.5, 5.8], 1), third([61.2, 63.3, 26.2, 5.8], 0)]
    rings = [[31.0 + k * 10.75, 78.6, 8.8, 8.2] for k in range(5)]
    return [colour('Count the objects and colour the correct number.', 'Count each group. Colour the number that tells how many.', after(pg, 0),
                   union([[10.7, 11.9, 78, 57.2]]), [(f'number', tuple(b), MANY) for b in answers]),
            write('Write numbers from 1 to 5.', 'Write 1, 2, 3, 4 and 5 in the caterpillar\'s circles, one in each.', after(pg, 1), union(rings), rings)]


@page(32)
def _(pg):
    boxes = [[38.6, 20.4, 8.1, 4.9], [80.0, 20.4, 8.1, 4.9], [38.6, 35.4, 8.1, 4.9], [80.0, 35.4, 8.1, 4.9]]
    nums = {'3': [17.0, 47.1, 11.2, 6.9], '4': [17.0, 56.8, 11.2, 6.9], '1': [16.7, 66.6, 11.8, 6.9]}
    pics = {'1': [71.8, 45.7, 15.8, 9.7], '3': [71.8, 55.5, 15.8, 9.7], '4': [71.4, 65.2, 16.6, 9.7]}
    dots = []
    for k in nums:
        n, p = nums[k], pics[k]
        dots += [(k, round(n[0] + n[2] + 1.2, 2), round(n[1] + n[3] / 2, 2)), (k, round(p[0] - 1.2, 2), round(p[1] + p[3] / 2, 2))]
    return [write('Count and write.', 'Count the pictures in each box. Write how many in its small box.', after(pg, 0), union([[10.9, 12.3, 72.4, 27.1]]), boxes),
            match('Count the objects and match them with the correct number.', 'Count the pictures. Draw a line from each number to the pictures it tells.',
                  after(pg, 1), union(list(nums.values()) + list(pics.values())), dots)]


@page(36)
def _(pg):
    frames = [[10.8, 14.2, 23.2, 16.7], [39.7, 14.2, 23.2, 16.7], [68.0, 14.2, 23.2, 16.7]]
    under = [[18.7, 29.7, 7.5, 5.7], [47.6, 29.7, 7.5, 5.7], [75.9, 29.7, 7.5, 5.7]]
    boxes = pg.find(pg.band(2), w=(5, 6), h=(3.8, 4.6))
    boxes = [rnd(b) for b in boxes if not any(o is not b and abs(o[0] - b[0]) < .3 for o in boxes[:boxes.index(b)])]
    assert len(boxes) == 9, boxes
    right = [boxes[2], boxes[3], boxes[8]]          # 6 cherries, 3 leaves, 6 watermelon slices
    return [tick_counted(pg, 0, 6, 'Tick the boxes with six birds.', 'Count the birds in each box. Tap the small box under every box with six.', frames, under),
            count_trace_write(pg, 1, 6),
            colour('Count and colour the box with the correct number.', 'Count each group. Colour the box with the number that tells how many.',
                   after(pg, 2), union([[12, 73, 79, 17]]), [('box', tuple(b), MANY) for b in right])]


def guided(q, shape):
    """Dashed outlines cannot hold a flood fill: colour each part inside its printed shape (app.js p.outline)."""
    for p in q['parts']:
        p['outline'] = shape
    return q


def trace_and_colour(pg, i, shape_name, outline, shapes, colour_name):
    title_trace, title_colour = f'Trace the {shape_name}s.', f'Colour the {shape_name}s {colour_name}.'
    return [write(title_trace, f'Trace each dotted {shape_name} with your pencil.', after(pg, i), union(shapes), shapes),
            guided(colour(title_colour, f'Colour each {shape_name} {colour_name}.', after(pg, i), union(shapes),
                          [(shape_name, tuple(b), [C[colour_name]]) for b in shapes]), outline)]


@page(37)
def _(pg):
    return trace_and_colour(pg, 0, 'circle', 'ellipse', [[16.1, 75.5, 17.1, 13.0], [42.0, 75.5, 17.1, 13.0], [68.4, 75.5, 17.1, 13.0]], 'red')


@page(38)
def _(pg):
    return [colour('Colour red.', 'Colour the apple and the strawberry red. Their leaves are green.', after(pg, 0),
                   union([[16.9, 57.8, 33.9, 29.2], [59.3, 61.7, 23.0, 23.9]]),
                   [('apple', (16.9, 57.8, 33.9, 29.2), [C['red'], C['green'], C['brown']]), ('strawberry', (59.3, 61.7, 23.0, 23.9), [C['red'], C['green']])])]


@page(42)
def _(pg):
    frames = [[7.5, 71.5, 27.4, 17.3], [36.3, 71.5, 27.4, 17.3], [65.0, 71.5, 27.4, 17.3]]
    boxes = [[18.3, 85.9, 6.3, 5.0], [47.1, 85.9, 6.3, 5.0], [75.7, 85.9, 6.3, 5.0]]
    return [colour_ten_frame(pg, 0, 7, 'birds', [60, 15, 35, 15]),
            count_trace_write(pg, 1, 7),
            write('Count and write the correct number.', 'Count the mushrooms in each group. Write how many in the box under it.', after(pg, 2),
                  union(frames + boxes), boxes)]


@page(46)
def _(pg):
    flags = [[19.8, 14.4, 26.4, 17.3], [57.0, 14.4, 26.4, 17.3]]
    flag = flags[0]      # the left flag has 8 stars, the right one 5
    rows = {'7': blobs(46, [21, 73.2, 71, 8.8], 9), '8': blobs(46, [21, 83.6, 71, 6.2], 9)}
    options = [dict(opt(b, True, 'jellyfish' if g == '7' else 'starfish', .3), group=g) for g, bs in rows.items() for b in bs]
    cross = marked('cross', 'Cross out the objects according to the given number.', 'Look at the number in each row. Cross out that many pictures: 7 jellyfish, then 8 starfish.',
                   after(pg, 2), union([b for bs in rows.values() for b in bs] + [[9.3, 75.2, 8, 6.1]]), options)
    cross['counts'] = {'7': 7, '8': 8}
    return [colour('Colour the flag with 8 stars.', 'Count the stars on each flag. Colour the flag that has 8 stars.', after(pg, 0), union(flags),
                   [('flag', tuple(flag), MANY)]),
            count_trace_write(pg, 1, 8), cross]


@page(50)
def _(pg):
    bags = [[12.5, 13.1, 21.8, 21.5], [40.2, 13.1, 21.8, 21.5], [68.0, 13.1, 21.8, 21.5]]
    boxes = [[20.4, 14.1, 4.7, 3.7], [47.9, 14.1, 4.7, 3.7], [75.7, 14.1, 4.7, 3.7]]
    circles = [rnd(b) for b in pg.find([20, 75, 72, 5.5], w=(5.4, 5.8), h=(4.2, 4.6), items=4)]
    squares = [rnd(b) for b in pg.find([20, 84, 72, 5.5], w=(5.4, 5.8), h=(4.2, 4.6), items=1)]
    assert len(circles) == 10 and len(squares) == 10, (len(circles), len(squares))
    return [tick_counted(pg, 0, 9, 'Tick the bag with 9 strawberries.', 'Count the strawberries in each bag. Tap the box on the bag with 9.', bags, boxes),
            count_trace_write(pg, 1, 9),
            colour('Colour the shapes according to the given number.', 'Colour 8 circles in the first row and 9 squares in the second row.', after(pg, 2),
                   union(circles + squares), [('circle', tuple(b), MANY) for b in circles] + [('square', tuple(b), MANY) for b in squares])]


@page(51)
def _(pg):
    pics = [[8.7, 73.3, 15.6, 12.3], [21.2, 64.7, 33.4, 26.3], [56.7, 77.8, 11.1, 9.0], [68.5, 68.6, 25.3, 19.9]]
    circles = [[10.8, 67.8, 7.2, 5.7], [28.0, 63.2, 7.2, 5.7], [57.6, 72.1, 7.2, 5.7], [74.5, 64.4, 7.2, 5.7]]
    names = ['pear', 'watermelon', 'onion', 'pumpkin']
    crop = union(pics + circles)
    return [marked('tick', 'Tick (✓) the heavy object in each group.', 'In each group, which one is heavy? Tap its circle to tick it.', (84.5, 60.2), crop,
                   [opt(c, k in (1, 3), names[k]) for k, c in enumerate(circles)]),
            marked('cross', 'Cross (✗) the light object in each group.', 'In each group, which one is light? Tap its circle to cross it.', (84.5, 64.3), crop,
                   [opt(c, k in (0, 2), names[k]) for k, c in enumerate(circles)])]


@page(52)
def _(pg):
    balls = sorted(pg.find([15, 65, 75, 6], w=(4.3, 4.7), h=(3.4, 3.8), items=4), key=lambda b: b[0])
    assert len(balls) == 5
    same = sorted([[9.8, 79.6, 5.6, 4.4], [28.2, 80.5, 5.6, 4.4], [47.0, 80.5, 5.6, 4.4], [83.5, 75.7, 5.6, 4.4]], key=lambda b: b[0])
    return [tick_boxes(pg, 0, 'Tick (✓) the object that is different.', 'Which ball is not like the others? Tap its circle to tick it.',
                       [rnd(b) for b in balls], {1}, ['ball', 'football', 'ball', 'ball', 'ball'], pictures=[[11.9, 58.6, 74, 10]]),
            tick_boxes(pg, 1, 'Tick (✓) the objects that are the same.', 'Which birds are the same? Tap their circles to tick them.',
                       same, {0, 2}, ['green duck', 'yellow duckling', 'green duck', 'hen'], pictures=[[13.1, 74.4, 75.2, 16.9]])]


@page(53)
def _(pg):
    return trace_and_colour(pg, 1, 'square', 'rectangle', [[16.4, 74.9, 16.9, 13.6], [40.4, 74.9, 16.9, 13.6], [64.3, 74.9, 16.9, 13.6]], 'blue')


@page(54)
def _(pg):
    return [colour('Colour blue.', 'Colour the car and the whale blue.', after(pg, 0), union([[10.2, 66.4, 44.8, 19.5], [51.3, 58.0, 41.5, 23.4]]),
                   [('car', (10.2, 66.4, 44.8, 19.5), [C['blue'], C['grey'], C['black']]), ('whale', (51.3, 58.0, 41.5, 23.4), [C['blue'], C['grey']])])]


@page(56)
def _(pg):
    return [trace_grid(pg, 0, 'Trace and write the number.', 'Trace the number 0, then write it in the empty boxes.', size=(6, 16)),
            tick_boxes(pg, 1, 'Tick (✓) the basket with 0 carrots.', 'Which basket has no carrots? Tap its circle to tick it.',
                       [[22.7, 83.8, 3.9, 3.1], [47.9, 83.8, 3.9, 3.1], [72.6, 83.8, 3.9, 3.1]], {2}, ['1 carrot', '2 carrots', '0 carrots'],
                       pictures=[[11.1, 72.8, 77.7, 15.6]])]


@page(58)
def _(pg):
    mushrooms = blobs(58, [22, 61, 72, 28.5], 10)
    return [trace_grid(pg, 0, 'Count and trace the number.', 'Count the dots. Trace the number 10 in every box.', size=(6, 16)),
            colour_objects(pg, 1, 'Colour the number and the objects.', 'Colour the number 10 and the 10 mushrooms.',
                           [('number 10', MANY)] + [('mushroom', [C['red'], C['white'] if 'white' in C else C['yellow'], C['brown']])] * 10,
                           objects=[[9.3, 63.2, 17.0, 14.3]] + mushrooms)]


@page(60)
def _(pg):
    return [tick_group(pg, 0, 10), count_trace_write(pg, 1, 10), find_and_circle(pg, 2, 10, [10, 12, 10, 13, 10, 10, 9, 10, 15, 10, 10, 11])]


def match_counts(pg, i, title, say, numbers, boxes, frames, crop_extra=()):
    """Numbers on the left, framed groups of pictures on the right: join each number to the group with that many
    pictures (the pictures are counted in the PDF)."""
    counts = [len([p for p in pg.find(f, kind='img') if p[2] < f[2] * .8]) for f in frames]
    dots = []
    for value, b in zip(numbers, boxes):
        assert counts.count(value) == 1, (pg.n, value, counts)
        f = frames[counts.index(value)]
        dots += [(str(value), round(b[0] + b[2] + .9, 2), round(b[1] + b[3] / 2, 2)), (str(value), round(f[0] - .3, 2), round(f[1] + f[3] / 2, 2))]
    return match(title, say, after(pg, i), union(boxes + frames + list(crop_extra)), dots)


@page(61)
def _(pg):
    boxes = [[9.3, 17.2, 8.1, 4.5], [9.3, 30.3, 8.1, 4.5], [9.3, 43.3, 8.1, 4.5], [9.3, 56.3, 8.1, 4.5], [9.3, 69.4, 8.1, 4.5], [9.3, 82.4, 8.1, 4.5]]
    frames = [rnd(b) for b in pg.find([55, 12, 40, 80], w=(29, 32), h=(11, 13))]
    frames = [f for f in frames if not any(o is not f and abs(o[1] - f[1]) < .3 for o in frames[:frames.index(f)])]
    return [match_counts(pg, 0, 'Count the objects and match them with the correct numbers.', 'Count the pictures in each box. Draw a line from each number to the box with that many.',
                         [3, 9, 7, 10, 6, 1], boxes, frames)]


@page(62)
def _(pg):
    # each group's two numbers, and the count: 6 apples, 8 pears, 7 stars, 10 flowers
    options = [opt([37.0, 14.6, 5.0, 4.8], False, '4'), opt([37.0, 20.6, 5.0, 4.8], True, '6'),
               opt([79.5, 14.6, 5.0, 4.8], True, '8'), opt([78.8, 20.6, 6.2, 4.8], False, '10'),
               opt([37.0, 29.8, 5.0, 4.8], False, '9'), opt([37.0, 35.8, 5.0, 4.8], True, '7'),
               opt([79.5, 29.8, 5.0, 4.8], False, '5'), opt([78.8, 35.8, 6.2, 4.8], True, '10')]
    boxes = [[73.0, 48.9, 5.5, 3.8], [73.4, 55.5, 5.5, 3.8], [81.7, 63.2, 5.5, 3.8], [73.0, 71.1, 5.5, 3.8]]
    return [choose('Count the objects and circle the correct number.', 'Count the pictures in each box. Tap the number that tells how many.',
                   after(pg, 0), union([[12.5, 13.0, 72, 28.4]]), options),
            write('Count the objects in the picture and write their numbers in the boxes.', 'Count the children, slides, swings and dogs in the park. Write each number in its box.',
                  (84.5, 47.5), union(boxes + [[13, 48, 60, 30]]), boxes)]


@page(63)
def _(pg):
    return [write('Join the numbers from 1 to 10 to complete the picture.', 'Start at 1. Draw a line to 2, then 3, and on to 10. Then colour the picture.',
                  after(pg, 0), [8, 12, 86, 78], [[9, 13, 84, 76]])]


def before_after_between(pg, heads, last_between=None):
    before = [[14.7, 17.3, 5.6, 4.7], [43.0, 17.3, 5.7, 4.7], [71.8, 17.3, 5.7, 4.7], [14.7, 26.3, 5.6, 4.7], [43.0, 26.3, 5.7, 4.7], [72.3, 26.3, 5.7, 4.7]]
    after_ = [[20.0, 41.5, 5.6, 4.7], [50.8, 41.5, 5.6, 4.7], [82.4, 41.5, 5.6, 4.7], [20.0, 52.4, 5.6, 4.7], [50.8, 52.4, 5.6, 4.7], [82.4, 52.4, 5.6, 4.7]]
    between = [[18.5, 69.4, 5.6, 4.8], [48.0, 69.4, 5.7, 4.8], [77.0, 69.4, 5.6, 4.8], [19.0, 83.2, 5.6, 4.8], [48.0, 83.2, 5.7, 4.8]] + (last_between or [[77.0, 83.2, 5.6, 4.8]])
    return [write('Write the number that comes before.', 'Look at each number. Write the number that comes just before it in the empty box.', after(pg, heads[0]),
                  union(before, 3), before),
            write('Write the number that comes after.', 'Look at each number. Write the number that comes just after it in the empty box.', after(pg, heads[1]),
                  union(after_, 3), after_),
            write('Write the number that comes between the two numbers.', 'Write the number that comes between the two numbers in each cloud.', after(pg, heads[2]),
                  union(between, 4), between)]


@page(64)
def _(pg):
    return before_after_between(pg, (0, 1, 4))


@page(80)
def _(pg):
    boxes = [rnd(b) for b in pg.find([10, 14, 15, 76], w=(12, 13), h=(9, 10.5), colour='#ffffff')]
    frames = [rnd(b) for b in pg.find([65, 12, 35, 80], w=(30, 32), h=(13.5, 15))]
    assert len(boxes) == 5 and len(frames) == 5, (boxes, frames)
    return [write('Trace each number.', 'Trace the numbers 11, 12, 13, 14 and 15.', after(pg, 0), union(boxes), boxes),
            match_counts(pg, 0, 'Count the objects in each box. Match each number to the correct box.', 'Count the fruit in each box. Draw a line from each number to the box with that many.',
                         [11, 12, 13, 14, 15], boxes, frames)]


@page(81)
def _(pg):
    col = lambda c: 16.9 + c * 10.7
    row = lambda r: 23.6 + r * 7.8
    path = [(2, 0), (3, 0), (3, 1), (3, 2), (2, 2), (2, 3), (1, 3), (0, 3), (0, 4), (0, 5), (1, 5), (1, 4), (2, 4), (2, 5), (3, 5)]   # 1 to 15
    cells = [[round(col(c), 2), round(row(r), 2), 10.7, 7.8] for r, c in path]
    return [colour('Help the baby fish to reach its mother by colouring the numbers in sequence from 1 to 15.',
                   'Colour 1, then 2, then 3, and on to 15. Each number is next to the one before it.', (60, 13.5), union(cells),
                   [(f'{k + 1}', tuple(b), MANY) for k, b in enumerate(cells)])]


@page(82)
def _(pg):
    return trace_and_colour(pg, 2, 'rectangle', 'rectangle', [[16.4, 76.2, 27.4, 10.5], [52.4, 76.2, 27.4, 10.5]], 'yellow')


@page(83)
def _(pg):
    return [colour('Colour yellow.', 'Colour the mango and the flower yellow.', after(pg, 0), union([[11.6, 59.0, 36.9, 29.3], [57.2, 60.5, 34.0, 27.9]]),
                   [('mango', (11.6, 59.0, 36.9, 29.3), [C['yellow'], C['green'], C['brown']]), ('flower', (57.2, 60.5, 34.0, 27.9), [C['yellow'], C['brown']])])]


@page(99)
def _(pg):
    boxes = [rnd(b) for b in pg.find([10, 16, 15, 76], w=(12, 13), h=(9, 10.5), colour='#ffffff')]
    frames = [rnd(b) for b in pg.find([65, 14, 35, 80], w=(30, 32), h=(13.5, 15))]
    assert len(boxes) == 5 and len(frames) == 5, (boxes, frames)
    return [write('Trace each number.', 'Trace the numbers 16, 17, 18, 19 and 20.', after(pg, 0), union(boxes), boxes),
            match_counts(pg, 0, 'Count the objects in each box. Match each number to the correct box.', 'Count the pictures in each box. Draw a line from each number to the box with that many.',
                         [16, 17, 18, 19, 20], boxes, frames)]


@page(100)
def _(pg):
    circles = sorted(pg.find([15, 38.5, 70, 3.5], w=(2.8, 3.2), h=(2.2, 2.6)), key=lambda b: b[0])
    assert len(circles) == 8, circles
    caps = len(pg.find([7, 12, 42, 23], kind='img'))
    bananas = len(pg.find([51, 12, 42, 23], kind='img'))
    printed = [19, 16, 20, 13, 15, 17, 16, 18]
    counts = [caps] * 4 + [bananas] * 4
    assert sum(p == c for p, c in zip(printed, counts)) == 2, (caps, bananas)
    boxes = sorted(pg.find([15, 49, 70, 21], w=(9, 10), h=(6.5, 7.2)), key=lambda b: (round(b[1]), b[0]))
    assert len(boxes) == 10, boxes
    empty = [boxes[k] for k in (1, 3, 5, 7, 8)]     # 11 _ 13 _ 15 / _ 17 _ _ 20
    return [marked('tick', 'Count the objects and tick (✓) the correct number.', 'Count the caps, then the bananas. Tap the circle under the number that tells how many.',
                   after(pg, 0), union([[7.2, 12.8, 85, 29]]), [opt(c, p == n, str(p), .6) for c, p, n in zip(circles, printed, counts)]),
            write('Write the missing numbers.', 'Count on from 11 to 20. Write the missing numbers in the empty boxes.', after(pg, 1), union(boxes), [rnd(b) for b in empty])]


@page(101)
def _(pg):
    return trace_and_colour(pg, 2, 'triangle', 'triangle', [[14.8, 74.9, 18.1, 13.9], [39.1, 74.9, 18.1, 13.9], [63.4, 74.9, 18.1, 13.9]], 'green')


@page(102)
def _(pg):
    return [colour('Colour green.', 'Colour the leaf and the grapes green.', after(pg, 0), union([[11.7, 61.9, 36.6, 20.0], [45.8, 53.2, 46.9, 33.0]]),
                   [('leaf', (11.7, 61.9, 36.6, 20.0), [C['green'], C['leaf']]), ('grapes', (45.8, 53.2, 46.9, 33.0), [C['green'], C['leaf'], C['brown']])])]


@page(103)
def _(pg):
    frames = [rnd(b) for b in pg.find([10, 14, 85, 75], w=(19.5, 20.5), h=(15.5, 16.2))]
    frames = [f for f in frames if not any(o is not f and abs(o[0] - f[0]) < .3 and abs(o[1] - f[1]) < .3 for o in frames[:frames.index(f)])]
    left = sorted([f for f in frames if f[0] < 50], key=lambda b: b[1])
    right = sorted([f for f in frames if f[0] > 50], key=lambda b: b[1])
    assert len(left) == 4 and len(right) == 4, frames
    # left: duck, apple, pear, pumpkin; right: strawberry, orange, banana, car
    pairs = [('yellow', 0, 2), ('red', 1, 0), ('green', 2, 3), ('orange', 3, 1)]
    dots = []
    for name, l, r in pairs:
        dots += [(name, round(left[l][0] + left[l][2] + .3, 2), round(left[l][1] + left[l][3] / 2, 2)),
                 (name, round(right[r][0] - .3, 2), round(right[r][1] + right[r][3] / 2, 2))]
    return [match('Match each object with another object of the same colour.', 'Draw a line from each picture to the picture of the same colour.',
                  after(pg, 0), union(frames), dots)]


@page(104)
def _(pg):
    # the house drawn in dashed shapes, coloured by the code: circle red, square green, triangle yellow, rectangle blue
    shapes = [('roof', [31.8, 19.3, 41.2, 23.8], 'triangle', 'yellow'), ('chimney', [23.8, 31.2, 8.0, 12.1], 'rectangle', 'blue'),
              ('round window', [40.5, 27.4, 17.5, 13.7], 'ellipse', 'red'), ('window', [29.7, 47.7, 16.1, 11.9], 'rectangle', 'green'),
              ('window', [51.9, 47.7, 16.2, 11.9], 'rectangle', 'green'), ('door', [42.6, 62.0, 12.5, 16.6], 'rectangle', 'blue'),
              ('round window', [29.6, 65.4, 8.7, 6.9], 'ellipse', 'red'), ('round window', [58.9, 65.4, 8.7, 6.9], 'ellipse', 'red')]
    col = colour('Colour each shape using the colour code.', 'Circles red, squares green, the triangle yellow and rectangles blue.', after(pg, 0),
                 union([b for _, b, _, _ in shapes]), [(n, tuple(b), [C[c]]) for n, b, _, c in shapes])
    for p, (_, _, outline, _) in zip(col['parts'], shapes):
        p['outline'] = outline
    count = [[58.2, 86.6, 7.4, 5.8], [69.7, 85.6, 6.5, 7.8], [80.0, 86.3, 8.5, 6.5]]
    return [write('Trace each shape.', 'Trace all the dotted lines of the house.', after(pg, 0), [22, 17, 54, 64], [[23, 18, 52, 62]]), col,
            write('Count and write the number.', 'Count the squares, the rectangles and the triangles in the house. Write each number in its shape.',
                  (36, 89), union(count + [[47.5, 86.5, 7.6, 6.0]]), count)]


@page(105)
def _(pg):
    hidden = {14: [71, 14.5, 8, 7.5], 13: [27, 22.5, 9.5, 8], 16: [51, 25.5, 9, 8], 11: [80, 39, 7, 8.5], 18: [3, 59.5, 9.5, 8],
              12: [46, 59.5, 9.5, 8], 15: [78, 59.5, 9, 8], 17: [53.5, 72.5, 9, 8], 20: [77.5, 78.5, 9.5, 8.5], 19: [42, 86, 9, 8]}
    return [choose('Find and circle the numbers (11-20) hidden in the picture.', 'Look carefully! Find the numbers 11 to 20 in the picture and tap each one.',
                   (81, 11.7), [1, 12, 98, 85], [opt(b, True, str(n), 0) for n, b in sorted(hidden.items())])]


@page(106)
def _(pg):
    cells = [rnd(b) for b in pg.find([10, 11, 80, 79], w=(10, 11), h=(7.2, 8), colour='#ffffff', items=1)]
    assert len(cells) == 60, len(cells)
    return [write('Trace and write.', 'Trace each number, then write it two times in the boxes beside it.', after(pg, 0), union(cells), cells)]


@page(107)
def _(pg):
    centres = [(44.1, 25.4), (68.7, 25.4), (82.0, 26.6), (85.1, 37.9), (61.5, 43.1), (48.7, 43.1), (24.6, 43.1), (16.4, 55.7),
               (41.0, 60.5), (55.4, 60.5), (69.2, 60.5), (68.2, 77.1), (52.3, 77.1)]
    rings = [[round(x - 5.5, 2), round(y - 4.3, 2), 11, 8.6] for x, y in centres]
    return [write('Write the missing numbers.', 'Count along the caterpillar from 1 to 20. Write the missing numbers in the empty circles.',
                  after(pg, 0), union(rings), rings)]


@page(108)
def _(pg):
    # the last cloud prints _ 19 _: both outer boxes are empty (the number before and the number after)
    return before_after_between(pg, [k for k, h in enumerate(pg.headings()) if h[0] < 12][:3], [[71.6, 83.2, 5.6, 4.8], [84.2, 83.2, 5.6, 4.8]])


@page(109)
def _(pg):
    return [marked('tick', 'Tick (✓) the thin object.', 'Which one is thin? Tap its circle to tick it.', after(pg, 0), union([[8.7, 61.9, 82.2, 24.6]]),
                   [opt([16.9, 64.0, 6.7, 5.2], False, 'thick log'), opt([81.6, 66.9, 6.7, 5.2], True, 'thin stick')])]


@page(110)
def _(pg):
    return [marked('tick', 'Tick (✓) the child that is up.', 'Which child is up high? Tap the circle to tick it.', after(pg, 0), union([[18.0, 54.4, 65.0, 32.7]]),
                   [opt([27.2, 74.4, 6.7, 5.2], False, 'boy at the bottom'), opt([62.6, 57.1, 6.7, 5.2], True, 'girl at the top')])]


@page(111)
def _(pg):
    return [write('Join the numbers from 1 to 20 to complete the picture.', 'Start at 1. Draw a line to 2, then 3, and on to 20. Then colour the picture.',
                  after(pg, 0), [8, 12, 86, 78], [[9, 13, 84, 76]])]


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    only = [int(a) for a in sys.argv[1:]]
    if only:
        for k in list(Q_PAGES):
            if k not in only:
                del Q_PAGES[k]
    data = build()
    with open(root / 'books/questions-maxford-maths.js', 'w', encoding='utf-8', newline='\n') as f:
        f.write('// Generated by tools/make_maxford_maths.py: the printed exercises of Maxford Global Qaida 3+ Maths.\n')
        f.write('window.BOOK_QUESTIONS = window.BOOK_QUESTIONS || {};\n')
        f.write("window.BOOK_QUESTIONS['%s'] = " % BOOK + json.dumps(data, indent=1, ensure_ascii=False) + ';\n')
    print(len(data), 'pages,', sum(len(q) for q in data.values()), 'questions')
    if not only:
        # the page palettes of the Write / Colour pencil: black for writing, plus the colours of the page's colouring tasks
        path = root / 'books/colour-palettes.json'
        palettes = json.loads(path.read_text(encoding='utf-8'))
        name_of = {v.lower(): k for k, v in palettes['colours'].items()}
        pages = {}
        for n in range(1, len(pdf_pages) + 1):
            qs = data.get(str(n), [])
            colours = ['black'] + [name_of[c.lower()] for q in qs if q['kind'] == 'colour' for p in q['parts'] for c in p['colours']]
            colours = list(dict.fromkeys(colours))
            tasks = [q['title'] for q in qs if q['kind'] == 'colour']
            pages[str(n)] = {'picture': '; '.join(tasks) if tasks else 'No requested colouring: black pencil for reading notes, matching or writing',
                             'colours': colours}
        palettes['books'][BOOK] = pages
        path.write_text(json.dumps(palettes, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    for note in NOTES:
        print('  note:', note)
