"""The printed exercises of Maxford Global Qaida 3+ Urdu as questions (app.js openQuestion).

The PDF pages are vector drawings, like the Maths book: the tracing rows are found from their printed guide
lines, headings from the dark right-aligned text, pictures and outlines from the PDF's shapes. Titles and
spoken instructions are in Urdu, as printed. Writes books/questions-maxford-urdu.js.

    python tools/make_maxford_urdu.py
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_maxford_maths as M
from make_maxford_questions import C, MANY, choose, colour, match, write

BOOK = 'maxford-global-qaida-3-urdu'
PDF = r'D:\pdf\Maxford Global QAIDA 3+ URDU (160 Pgs) (8.87 X 11.25) (2026-27) Final Curve.pdf'
M.BOOK = BOOK                                   # M.blobs reads this book's page images
M.pdf_pages = [p for p in M.pymupdf.open(PDF) if not M.blank(p)]
Page, rnd, union, blobs, TEXT = M.Page, M.rnd, M.union, M.blobs, M.TEXT
PILL_W, PILL_H, GAP = 14.5, 3.5, 0.8

TRACE = 'پڑھیں اور پنسل پھیریں۔'
TRACE_SAY = 'لکیروں پر بنے حرف پر پنسل پھیریں، پھر خالی جگہ پر خود لکھیں۔'


def headings(pg):
    """Lines of dark text that end near the right margin (Urdu instructions), top to bottom: [x0, y0, x1, y1]."""
    text = [p['b'] for p in pg.parts if p['k'] == 'shape' and p['c'] == TEXT and p['fill'] and p['n'] > 30 and .8 < p['b'][3] < 3.8 and p['b'][1] > 8]
    lines = []
    for x, y, w, h in sorted(text, key=lambda b: b[1]):
        line = next((l for l in lines if abs((l[1] + l[3]) / 2 - (y + h / 2)) < .9), None)
        if line:
            line[0], line[1], line[2], line[3] = min(line[0], x), min(line[1], y), max(line[2], x + w), max(line[3], y + h)
        else:
            lines.append([x, y, x + w, y + h])
    return [l for l in lines if l[2] > 84 and l[2] - l[0] > 8 and l[1] < 87.5]


def before(pg, i=0, nth=0):
    """Where a heading's button goes: to the left of its first word (Urdu reads right to left), on its line."""
    x0, y0, x1, y1 = headings(pg)[i]
    return (round(max(1, x0 - 2 - PILL_W - nth * (PILL_W + GAP)), 2), round((y0 + y1) / 2 - PILL_H / 2, 2))


def guide_lines(pg, area=(0, 8, 100, 82), min_w=15):
    """The printed writing lines (thin horizontal strokes), each [x, y, w]."""
    out = []
    # tip boxes (a coloured note with its own little writing line) are not writing rows
    notes = [p['b'] for p in pg.parts if p['k'] == 'shape' and p.get('fill') and p.get('c') not in ('#ffffff', TEXT) and 12 < p['b'][2] < 35 and 4 < p['b'][3] < 20]
    for p in pg.parts:
        x, y, w, h = p['b']
        if any(n[0] - .3 <= x and x + w <= n[0] + n[2] + .3 and n[1] <= y <= n[1] + n[3] for n in notes):
            continue
        if p['k'] == 'shape' and h < .3 and w >= min_w and area[0] - .3 <= x and x + w <= area[0] + area[2] + .3 and area[1] <= y <= area[1] + area[3]:
            if not any(abs(o[0] - x) < .5 and abs(o[1] - y) < .5 for o in out):
                out.append([x, y, w])
    return sorted(out, key=lambda l: (l[1], l[0]))


def trace_rows(pg, area=(0, 8, 100, 82), row_h=10.8, top=None):
    """A writing box above each printed line: the dotted letters sit on it."""
    rows = []
    for x, y, w in guide_lines(pg, area):
        y0 = y - row_h
        if top is not None:
            y0 = max(y0, top)
        rows.append(rnd([x, y0, w, y + 1 - y0]))
    return rows


def trace_heading(pg):
    """The 'پڑھیں اور پنسل پھیریں' heading: the last heading above the first full-width writing line."""
    hs = headings(pg)
    full = [l for l in guide_lines(pg) if l[2] > 60]
    if not full:
        return 0
    above = [k for k, h in enumerate(hs) if h[3] < full[0][1] - 4]
    return above[-1] if above else 0


def trace_q(pg, rows, title=TRACE, say=TRACE_SAY, i=None, nth=0, button=None):
    assert rows, (pg.n, 'no writing lines')
    return write(title, say, button or before(pg, trace_heading(pg) if i is None else i, nth), union(rows, .8), rows)


def colour_picture(pg, name, colours, area=(3, 56, 52, 33.5)):
    """The outline picture to colour beside the letter (رنگ بھریں): everything drawn in its corner of the page."""
    def inside(p):
        x, y, w, h = p['b']
        cx, cy = x + w / 2, y + h / 2
        is_words = p['k'] == 'shape' and p.get('c') == TEXT and p.get('fill') and h < 3.8     # its label: "... میں رنگ بھریں"
        return (not is_words and h > .3 and max(w, h) > 3 and w < 55 and h < 40
                and area[0] <= cx <= area[0] + area[2] and area[1] <= cy <= area[1] + area[3] and y + h < 90)
    boxes = [p['b'] for p in pg.parts if inside(p)]
    assert boxes, (pg.n, 'no picture')
    b = union(boxes, 0)
    return colour('رنگ بھریں۔', f'{name} میں رنگ بھریں۔', (0, 0), union([b], 1), [(name, tuple(b), colours)])


Q_PAGES = {}
NOTES = []


def page(n):
    def wrap(f):
        Q_PAGES[n] = f
        return f
    return wrap


def place(qs):
    """Buttons not given a place go after the page's first heading (to its left), one beside another."""
    k = 0
    for q in qs:
        if q['button'] is None or q['button'] == {'x': None, 'y': None}:
            q['button'] = None
    for q in qs:
        if q['button'] is None:
            pg_head = q.pop('_head')
            x, y = pg_head
            q['button'] = {'x': round(max(1, x - k * (PILL_W + GAP)), 2), 'y': y}
            k += 1
        q.pop('_head', None)
    return qs


# ---------- each letter: a tracing page with a picture to colour, and a second tracing page ----------
# first tracing page: (the picture to colour, its colours)
LETTER_PAGES = {
    12: ('انگور', [C['green'], C['purple'], C['brown']]), 16: ('آم', [C['yellow'], C['orange'], C['green']]),
    21: ('بطخ', [C['yellow'], C['orange'], C['grey']]), 25: ('پتا', [C['green'], C['leaf']]),
    28: ('تتلی', MANY), 31: ('ٹماٹر', [C['red'], C['green']]), 34: ('ثمر (پھلوں کی ٹوکری)', MANY),
    41: ('جگ', [C['blue'], C['grey']]), 44: ('چاند', [C['yellow'], C['orange']]), 47: ('حلوہ کی پلیٹ', [C['orange'], C['yellow'], C['brown']]),
    50: ('خط', [C['yellow'], C['orange'], C['blue']]), 57: ('درخت', [C['green'], C['brown']]), 60: ('ڈبا', MANY),
    63: ('ذخیرہ', [C['light brown'], C['brown'], C['yellow']]), 66: ('رکشا', [C['green'], C['yellow'], C['black']]),
    69: ('پہاڑ', [C['grey'], C['brown'], C['blue']]), 72: ('زیبرا', [C['black'], C['grey']]), 75: ('ژالہ باری کی کھڑکی', [C['blue'], C['brown'], C['grey']]),
    82: ('سیب', [C['red'], C['green'], C['brown']]), 85: ('شیر', [C['orange'], C['yellow'], C['brown']]),
    88: ('صراحی', [C['brown'], C['orange'], C['light brown']]), 91: ('ضعیف (بزرگ)', MANY), 98: ('طیارہ', [C['blue'], C['grey'], C['red']]),
    101: ('ظروف (برتن)', [C['grey'], C['blue'], C['brown']]), 104: ('عقاب', [C['brown'], C['yellow'], C['light brown']]),
    107: ('غبارہ', [C['red'], C['blue'], C['yellow'], C['pink']]), 114: ('فراک', [C['pink'], C['red'], C['purple']]),
    117: ('قینچی', [C['blue'], C['red'], C['grey']]), 120: ('کیلا', [C['yellow'], C['green'], C['brown']]),
    123: ('گاجر', [C['orange'], C['green']]), 126: ('لٹو', MANY), 129: ('مالٹا', [C['orange'], C['green']]),
    136: ('ناریل', [C['brown'], C['light brown']]), 139: ('وردی', [C['blue'], C['grey'], C['black']]),
    142: ('ہاتھی', [C['grey'], C['black']]), 145: ('چائے کا کپ', [C['blue'], C['brown'], C['orange']]),
    148: ('یکہ (تانگا)', [C['brown'], C['light brown'], C['black']]),
}
SECOND_PAGES = [13, 17, 22, 26, 29, 32, 35, 42, 45, 48, 51, 58, 61, 64, 67, 70, 73, 76, 83, 86, 89, 92, 99, 102, 105, 108,
                115, 118, 121, 124, 127, 130, 137, 140, 143, 146, 149]
REVIEW_TRACE = [18, 36, 52, 77, 93, 109, 131, 150]


def make_first(n, name, colours):
    @page(n)
    def _(pg):
        hs = headings(pg)
        q1 = trace_q(pg, trace_rows(pg, top=9))
        q2 = colour_picture(pg, name, colours)
        x, y = before(pg, trace_heading(pg), 1)
        q2['button'] = {'x': x, 'y': y}
        return [q1, q2]


for n, (name, colours) in LETTER_PAGES.items():
    make_first(n, name, colours)


def make_second(n):
    @page(n)
    def _(pg):
        hs = headings(pg)
        return [trace_q(pg, trace_rows(pg, top=9))]


for n in SECOND_PAGES + REVIEW_TRACE:
    make_second(n)


# ---------- pages with their own layout ----------
def opt(b, correct, label, pad=.8):
    return {'x': round(b[0] - pad, 2), 'y': round(b[1] - pad, 2), 'w': round(b[2] + 2 * pad, 2), 'h': round(b[3] + 2 * pad, 2),
            'correct': correct, 'label': label}


def circle_letter_q(pg, letter, grid_area, is_letter, i=0, button=None):
    """'حرف X کو پہچان کر اس کے گرد دائرہ بنائیں': every printed letter in the box; the ones that are X are right."""
    shapes = [p['b'] for p in pg.parts if p['k'] == 'shape' and p.get('fill') and p.get('c') not in ('#ffffff', TEXT)
              and max(p['b'][2], p['b'][3]) > 1.8 and p['b'][2] < 9 and p['b'][3] < 9
              and grid_area[0] <= p['b'][0] and p['b'][0] + p['b'][2] <= grid_area[0] + grid_area[2]
              and grid_area[1] <= p['b'][1] and p['b'][1] + p['b'][3] <= grid_area[1] + grid_area[3]]
    shapes = [b for k, b in enumerate(shapes) if not any(abs(o[0] - b[0]) < .3 and abs(o[1] - b[1]) < .3 for o in shapes[:k])]
    options = [opt(b, is_letter(b), letter if is_letter(b) else 'دوسرا حرف', 1.2) for b in shapes]
    assert any(o['correct'] for o in options), (pg.n, letter)
    return choose(f'حرف "{letter}" کو پہچان کر اس کے گرد دائرہ بنائیں۔', f'جہاں جہاں حرف {letter} ہے، اسے چھو کر دائرہ لگائیں۔',
                  button or before(pg, i), union(shapes, 2), options)


@page(9)
def _(pg):
    rows = [[10, 16.5, 80, 17.5], [10, 38, 80, 13.5], [10, 56, 80, 13.5], [10, 73.5, 80, 17]]
    return [write('پنسل پھیریں۔', 'سرخ نقطے سے شروع کر کے ہر لکیر پر پنسل پھیریں۔', before(pg, 0), union(rows, .5), rows)]


@page(10)
def _(pg):
    rows = [[11, 16.5, 78.5, 16.3], [11, 36.8, 78.5, 13.5], [12, 54.3, 76, 16.2], [12, 74.4, 77.5, 15.6]]
    return [write('پنسل پھیریں۔', 'سرخ نقطے سے شروع کر کے ہر شکل پر پنسل پھیریں۔', before(pg, 0), union(rows, .5), rows)]


@page(14)
def _(pg):
    slots = [[71.8, 80.6, 13.7, 7.5], [43.0, 80.6, 13.7, 7.5], [14.1, 80.6, 13.7, 7.5]]
    return [circle_letter_q(pg, 'ا', [8, 15, 84, 41], lambda b: b[2] < 1 and b[3] > 3),     # ا is the thin upright stroke (آ is wider)
            write('تصویر کے نام کا پہلا حرف لکھیں۔', 'انار، انڈا، انگور: ہر تصویر کے نیچے اس کے نام کا پہلا حرف لکھیں۔', (45, 57.5),
                  union(slots + [[13.3, 61.5, 82, 16]]), slots)]


@page(19)
def _(pg):
    pics = [([9.5, 11.2, 19.4, 14.4], True, 'انگور'), ([34.7, 11.5, 18.7, 13.7], False, 'آم'), ([63.1, 13.4, 9.2, 9.7], True, 'انڈا'),
            ([13.6, 27.8, 12.4, 8.9], True, 'آلو'), ([37.5, 27.2, 13.2, 9.9], True, 'آڑو'), ([61.9, 27.1, 11.6, 10.1], False, 'انار')]
    return [choose('دیے گئے حرف سے شروع ہونے والی تصاویر کے گرد دائرہ لگائیں۔', 'پہلی قطار میں ا سے، دوسری قطار میں آ سے شروع ہونے والی تصویروں کو چھوئیں۔',
                   before(pg, 0), union([b for b, _, _ in pics] + [[80.1, 13.6, 11.8, 23.2]]), [opt(b, ok, name, .3) for b, ok, name in pics]),
            match('تصویر کو اس کے ابتدائی حرف سے ملائیں۔', 'ہر حرف سے اس تصویر تک لکیر کھینچیں جس کا نام اسی حرف سے شروع ہوتا ہے۔', before(pg, 1),
                  union([[6.5, 45.9, 12.5, 22.3], [71.3, 43.0, 22.2, 27.2]]),
                  [('آم', 19.6, 51.1), ('آم', 73.5, 63.3), ('انگور', 19.6, 63.5), ('انگور', 70.5, 51.2)])]


@page(23)
def _(pg):
    return [circle_letter_q(pg, 'ب', [8, 14.5, 84, 33], lambda b: 5.7 < b[2] < 6.3 and 2.9 < b[3] < 3.5),   # the seven ب are one shape
            match('حرف کو درست تصویر سے ملائیں۔', 'حرف ب سے ان تصویروں تک لکیر کھینچیں جن کا نام ب سے شروع ہوتا ہے: بستہ اور بکری۔', before(pg, 1),
                  union([[7.3, 52.4, 85.4, 38]]),
                  [('بستہ', 40.6, 66.0), ('بستہ', 25.6, 60.2), ('بکری', 59.4, 73.0), ('بکری', 70.3, 80.5)])]


def ticked(q):
    q['mark'] = 'tick'
    q['label'] = '✓ لگائیں'
    return q


@page(37)
def _(pg):
    boxes = sorted([b for b in pg.find([8, 35, 84, 4.5], w=(3.3, 3.7), h=(2.5, 2.9))], key=lambda b: b[0])
    boxes = [b for k, b in enumerate(boxes) if not any(abs(o[0] - b[0]) < .3 for o in boxes[:k])]
    assert len(boxes) == 6, boxes
    letters = ['ب', 'پ', 'ٹ', 'ت', 'ث', 'ت']        # under the leaf (پتا), the tomato (ٹماٹر) and the watermelon (تربوز)
    return [ticked(choose('تصویر کے درست ابتدائی حرف پر ✓ کا نشان لگائیں۔', 'ہر تصویر کا نام بولیں۔ جس حرف سے نام شروع ہوتا ہے اس کے خانے کو چھوئیں۔',
                          (52, 9.3), union([[7.8, 14.5, 84.4, 25]]), [opt(b, k in (1, 2, 5), letters[k], .6) for k, b in enumerate(boxes)])),
            match('حرف کو درست تصویر سے ملائیں۔', 'ث سے ثمر (پھلوں کی ٹوکری) اور ب سے بطخ تک لکیر کھینچیں۔', before(pg, 0),
                  union([[9.9, 42.9, 82.7, 25]]), [('ثمر', 79.4, 50.8), ('ثمر', 27.3, 62.8), ('بطخ', 79.4, 62.8), ('بطخ', 27.3, 50.8)])]


@page(53)
def _(pg):
    slots = [[11.2, 61.3, 18.0, 4.8], [39.6, 61.3, 18.0, 4.8], [67.9, 61.3, 18.0, 4.8]]
    # the rabbit's card (left) shows خ and ج, the key's card (right) ح and چ
    letters = [([14.7, 16.7, 4.9, 7.1], True, 'خ'), ([14.7, 29.0, 4.9, 5.3], False, 'ج'), ([58.5, 17.5, 4.9, 5.2], False, 'ح'), ([58.5, 28.4, 4.9, 5.3], True, 'چ')]
    return [choose('تصویر دیکھ کر درست حرف کے گرد دائرہ لگائیں۔', 'خرگوش اور چابی: ہر تصویر کے ساتھ اس حرف کو چھوئیں جس سے اس کا نام شروع ہوتا ہے۔',
                   (40, 9.3), union([[9.1, 13.7, 80.3, 23.6]]), [opt(b, ok, name) for b, ok, name in letters]),
            write('تصویر کے نام کا پہلا حرف لکھیں۔', 'چائے، جگ، حجام: ہر تصویر کے نیچے اس کے نام کا پہلا حرف لکھیں۔', (52, 37.8),
                  union([[7.3, 44.2, 82.4, 22.1]]), slots)]


@page(78)
def _(pg):
    cols = [18.2, 38.6, 59.0, 79.6]          # letters in the middle row: د ز ڈ ر
    top = [('دودھ', 0, 0, -3.5), ('رکشا', 1, 3, 0), ('درخت', 2, 0, 3.5), ('زیور', 3, 1, 0)]     # (picture, its column, its letter's column, dot shift)
    bottom = [('زیبرا', 0, 1, 0), ('دلیہ', 1, 0, 0), ('رسی', 2, 3, 0), ('ڈاکیا', 3, 2, 0)]
    dots = []
    for name, c, l, dx in top:
        dots += [(name, cols[c], 28.2), (name, round(cols[l] + dx, 2), 35.4)]
    for name, c, l, dx in bottom:
        dots += [(name, cols[c], 53.6), (name, round(cols[l] + dx, 2), 45.6)]
    return [match('ہر تصویر کو درست حرف سے ملائیں۔', 'ہر تصویر کا نام بولیں اور اسے اس حرف سے ملائیں جس سے نام شروع ہوتا ہے۔', (52, 9.6),
                  union([[9.6, 13.0, 79.2, 55.7]]), dots)]


@page(94)
def _(pg):
    boxes = [[14.0, 30.9, 5.2, 4.0], [33.8, 30.9, 5.2, 4.0], [58.4, 30.9, 5.2, 4.0], [78.2, 30.9, 5.2, 4.0]]
    names = ['ضرب (کلہاڑی)', 'چڑیا', 'سائیکل', 'گاڑی']      # left: ض with axe and sparrow; right: س with bicycle and car
    pics = [([9.2, 39.3, 15.9, 12.5], False, 'درخت'), ([32.2, 40.1, 15.9, 12.5], True, 'صندوق'), ([56.3, 41.8, 14.5, 9.0], False, 'ذرات'),
            ([9.1, 53.8, 16.1, 12.7], True, 'شیر'), ([35.2, 55.8, 9.9, 8.7], False, 'سیب'), ([56.4, 54.6, 13.9, 11.0], False, 'صراحی')]
    return [ticked(choose('حرف کے مطابق درست تصویر پر ✓ کا نشان لگائیں۔', 'ض کے ساتھ کلہاڑی یا چڑیا، س کے ساتھ سائیکل یا گاڑی: درست تصویر کے خانے کو چھوئیں۔',
                          (44, 9.3), union([[6.8, 13.1, 83.9, 22]]), [opt(b, k in (0, 2), names[k], .6) for k, b in enumerate(boxes)])),
            choose('حرف کے مطابق درست تصویر پر دائرہ لگائیں۔', 'پہلی قطار میں ص سے اور دوسری قطار میں ش سے شروع ہونے والی تصویر کو چھوئیں۔', (44, 35.5),
                   union([[9.1, 39.3, 81.1, 27.5]]), [opt(b, ok, name, .3) for b, ok, name in pics])]


@page(110)
def _(pg):
    slots = [[11.2, 31.2, 18.0, 4.8], [39.6, 31.2, 18.0, 4.8], [67.9, 31.2, 18.0, 4.8]]
    # left ع ط ظ, right ط ظ ع (the same letters are the same shape in the PDF)
    pairs = [('ع', 46.55, 65.35), ('ط', 55.95, 46.55), ('ظ', 65.35, 55.95)]
    dots = []
    for name, ly, ry in pairs:
        dots += [(name, 21.25, ly), (name, 74.95, ry)]
    return [write('تصویر کے نام کا پہلا حرف لکھیں۔', 'غلیل، ظروف، عقاب: ہر تصویر کے نیچے اس کے نام کا پہلا حرف لکھیں۔', (52, 9.3),
                  union([[7.3, 14.2, 82.4, 22.1]]), slots),
            match('ایک جیسے حروف کو آپس میں ملائیں۔', 'ہر حرف کو دوسری طرف اسی جیسے حرف سے لکیر کھینچ کر ملائیں۔', (52, 37.6),
                  union([[10.0, 42.1, 76.3, 27.4]]), dots)]


@page(132)
def _(pg):
    boxes = sorted(pg.find([14, 20, 45, 50], w=(3.7, 4.1), h=(2.8, 3.2)), key=lambda b: (round(b[1]), b[0]))
    boxes = [b for k, b in enumerate(boxes) if not any(abs(o[0] - b[0]) < .3 and abs(o[1] - b[1]) < .3 for o in boxes[:k])]
    assert len(boxes) == 12, boxes
    letters = ['ل', 'ق', 'ف', 'گ', 'م', 'ل', 'م', 'ق', 'ک', 'ل', 'ف', 'م']     # left to right in each row
    right = {0, 4, 8, 10}                                                       # lemon ل، fish م، boat ک، dove ف
    return [ticked(choose('تصویر کو دیکھ کر اس کے درست حرف کے خانے میں ✓ کا نشان لگائیں۔', 'لیموں، مچھلی، کشتی، فاختہ: ہر قطار میں اس حرف کا خانہ چھوئیں جس سے نام شروع ہوتا ہے۔',
                          (30, 9.3), union([[12.4, 12.9, 76.6, 56.3]]), [opt(b, k in right, letters[k], .6) for k, b in enumerate(boxes)]))]


def blank_boxes(lines, above=6.5):
    """A writing box over each printed blank line."""
    return [rnd([x, y - above, w, above + .8]) for x, y, w in lines]


@page(151)
def _(pg):
    blanks = sorted(pg.find([30, 20, 60, 55], w=(5.3, 5.7), h=(3.6, 4.0)), key=lambda b: (round(b[1]), b[0]))
    blanks = [rnd(b) for k, b in enumerate(blanks) if not any(abs(o[0] - b[0]) < .3 and abs(o[1] - b[1]) < .3 for o in blanks[:k])]
    assert len(blanks) == 5, blanks
    return [write('تصویر دیکھ کر پہلا حرف لکھیں اور لفظ مکمل کریں۔', 'نلکا، یاسمین، ہاکی، ویگن، یکہ: ہر تصویر کا نام بولیں اور خالی خانے میں پہلا حرف لکھیں۔',
                  (40, 9.3), union([[11.1, 13.4, 77.7, 58.6]]), blanks)]


@page(152)
def _(pg):
    cards = sorted(pg.find([8, 12, 83, 78], w=(38.5, 39.6), h=(23, 24)), key=lambda b: (round(b[1]), b[0]))
    cards = [b for k, b in enumerate(cards) if not any(abs(o[0] - b[0]) < .3 and abs(o[1] - b[1]) < .3 for o in cards[:k])]
    assert len(cards) == 6, cards
    names = [('سورج', [C['yellow'], C['orange']]), ('مالٹا', [C['orange'], C['green']]), ('سیب', [C['red'], C['green'], C['brown']]),
             ('پھول', [C['red'], C['pink'], C['green']]), ('طوطا', [C['green'], C['red'], C['yellow']]), ('دوات', [C['black'], C['blue'], C['grey']])]
    return [colour('درج ذیل تصاویر میں موزوں رنگ بھریں۔', 'ہر تصویر میں اس کا اصل رنگ بھریں۔', (50, 9.3), union(cards),
                   [(n, tuple(rnd(b)), cols) for b, (n, cols) in zip(cards, names)])]


@page(154)
def _(pg):
    return [trace_q(pg, trace_rows(pg, top=9), 'پنسل پھیریں اور یاد کریں۔', 'ا سے ے تک سب حروف پر پنسل پھیریں اور انہیں یاد کریں۔', button=(52, 9.3))]


@page(155)
def _(pg):
    lines = [l for l in guide_lines(pg, min_w=10) if 10 < l[2] < 11]
    assert len(lines) == 19, len(lines)
    boxes = blank_boxes(lines)
    return [write('حروفِ تہجی مکمل کریں۔', 'خالی جگہوں پر چھوٹے ہوئے حروف لکھ کر حروفِ تہجی مکمل کریں۔', (58, 9.3), union(boxes, 2), boxes)]


@page(156)
def _(pg):
    lines = guide_lines(pg, min_w=7)
    boxes = blank_boxes(lines)
    first = [b for b in boxes if b[1] < 40]
    middle = [b for b in boxes if 40 <= b[1] < 62]
    last = [b for b in boxes if b[1] >= 62]
    assert len(first) == 6 and len(middle) == 6 and len(last) == 6, (len(first), len(middle), len(last))
    return [write('پہلے آنے والے حروف لکھیں۔', 'ہر حرف سے پہلے آنے والا حرف خالی جگہ پر لکھیں۔', (48.5, 9.5), union(first, 2), first),
            write('درمیان میں آنے والے حروف لکھیں۔', 'دونوں حروف کے درمیان آنے والا حرف لکھیں۔', (42.5, 36.6), union(middle, 2), middle),
            write('بعد میں آنے والے حروف لکھیں۔', 'ہر حرف کے بعد آنے والا حرف خالی جگہ پر لکھیں۔', (47.5, 63.8), union(last, 2), last)]


@page(157)
def _(pg):
    parts = [('آم (۲)', (7.3, 14.2, 31.2, 26.1), [C['yellow'], C['orange'], C['green']]), ('بطخ (۱)', (49.9, 14.2, 31.0, 26.1), [C['yellow'], C['orange']]),
             ('چوزے (۴)', (7.3, 40.3, 31.2, 26.1), [C['yellow'], C['orange']]), ('تتلیاں (۳)', (49.9, 40.3, 31.0, 26.1), MANY),
             ('قلفیاں (۵)', (7.3, 66.6, 73.0, 23.0), MANY)]
    return [colour('گنتی بلند آواز سے پڑھیں اور رنگ بھریں۔', 'ہر خانے میں تصویریں گنیں، گنتی بلند آواز سے پڑھیں اور رنگ بھریں۔', (40, 9.3),
                   union([list(p[1]) for p in parts]), parts)]


@page(158)
def _(pg):
    numbers = {1: 20.0, 2: 36.5, 3: 52.8, 4: 69.3, 5: 85.9}          # the number circles down the right
    pictures = {'ناشپاتی': (20.0, 3), 'گیندیں': (36.5, 5), 'ویگن': (52.8, 1), 'لٹو': (69.3, 2), 'تالے': (85.9, 4)}
    dots = []
    for name, (y, n) in pictures.items():
        dots += [(name, 41.0, y), (name, 80.3, numbers[n])]
    return [match('عدد کو درست تصویر سے ملائیں۔', 'ہر عدد سے اتنی ہی چیزوں والی تصویر تک لکیر کھینچیں۔', (52, 9.3), union([[7, 11, 86, 81]]), dots)]


def raised_letters(pg):
    """The big letters of 'حروف اور تصاویر کی ابھری ہوئی صورت' pages: the coloured letter shapes (not the pictures),
    touching pieces joined into one letter."""
    imgs = [p['b'] for p in pg.parts if p['k'] == 'img']
    over_img = lambda b: any(i[0] - .5 <= b[0] and b[0] + b[2] <= i[0] + i[2] + .5 and i[1] - .5 <= b[1] and b[1] + b[3] <= i[1] + i[3] + .5 for i in imgs)
    pieces = [list(p['b']) for p in pg.parts if p['k'] == 'shape' and p.get('c') not in ('#ffffff', TEXT, None) and 12 < p['b'][1] < 92
              and 1.5 < max(p['b'][2], p['b'][3]) and p['b'][2] < 25 and p['b'][3] < 26 and not over_img(p['b'])
              and p.get('n', 0) > 2]
    letters = []
    for b in sorted(pieces, key=lambda b: -b[2] * b[3]):
        for m in letters:
            if b[0] < m[0] + m[2] + .6 and m[0] < b[0] + b[2] + .6 and b[1] < m[1] + m[3] + .6 and m[1] < b[1] + b[3] + .6:
                x0, y0 = min(m[0], b[0]), min(m[1], b[1])
                m[2], m[3] = max(m[0] + m[2], b[0] + b[2]) - x0, max(m[1] + m[3], b[1] + b[3]) - y0
                m[0], m[1] = x0, y0
                break
        else:
            letters.append(b)
    return [rnd(b) for b in sorted(letters, key=lambda b: (round(b[1] / 8), -b[0])) if b[3] > 6]


RAISED_EXTRA = {3: [[72.5, 45.5, 21, 17]]}      # page 3's red ب is drawn as a filled picture, so it is added by hand

for _n in (3, 4, 5, 6, 7):
    def _make(n):
        @page(n)
        def _(pg):
            letters = [rnd([b[0] - .8, b[1] - 1.5, b[2] + 1.6, b[3] + 2.3]) for b in raised_letters(pg)] + RAISED_EXTRA.get(n, [])
            return [write('حروف اور تصاویر کی ابھری ہوئی صورت', 'ہر بڑے حرف پر انگلی پھیریں، اس کی آواز بولیں اور ساتھ والی تصویر کا نام بتائیں۔',
                          (2, 9.6), union(letters), letters)]
    _make(_n)


def build():
    out = {}
    for n, f in sorted(Q_PAGES.items()):
        out[str(n)] = [q for q in f(Page(n)) if q]
    return out


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    only = [int(a) for a in sys.argv[1:]]
    if only:
        for k in list(Q_PAGES):
            if k not in only:
                del Q_PAGES[k]
    data = build()
    with open(root / 'books/questions-maxford-urdu.js', 'w', encoding='utf-8', newline='\n') as f:
        f.write('// Generated by tools/make_maxford_urdu.py: the printed exercises of Maxford Global Qaida 3+ Urdu.\n')
        f.write('window.BOOK_QUESTIONS = window.BOOK_QUESTIONS || {};\n')
        f.write("window.BOOK_QUESTIONS['%s'] = " % BOOK + json.dumps(data, indent=1, ensure_ascii=False) + ';\n')
    print(len(data), 'pages,', sum(len(q) for q in data.values()), 'questions')
    if not only:
        # the Write / Colour pencil's palette on each page: black for writing, plus the colours of its colouring tasks
        path = root / 'books/colour-palettes.json'
        palettes = json.loads(path.read_text(encoding='utf-8'))
        name_of = {v.lower(): k for k, v in palettes['colours'].items()}
        pages = {}
        for n in range(1, len(M.pdf_pages) + 1):
            qs = data.get(str(n), [])
            colours = list(dict.fromkeys(['black'] + [name_of[c.lower()] for q in qs if q['kind'] == 'colour' for p in q['parts'] for c in p['colours']]))
            tasks = [q['title'] for q in qs if q['kind'] == 'colour']
            pages[str(n)] = {'picture': '; '.join(tasks) if tasks else 'No requested colouring: black pencil for reading notes, matching or writing',
                             'colours': colours}
        palettes['books'][BOOK] = pages
        path.write_text(json.dumps(palettes, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    for note in NOTES:
        print('  note:', note)
