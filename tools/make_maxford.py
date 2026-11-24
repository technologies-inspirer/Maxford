"""Build the activities for Maxford Global Qaida 3+ English, letters a to z. Writes books/activities-maxford.js.

On each "Sound" page: a find-the-picture game, and the publisher's own videos once they are put in
videos/maxford-qaida-3/ named like "Story of Letter a.mp4". No home-made animations or narration.
On each "Trace and say the sound" page: "Show me how", where the pencil writes the two big letters and the three
rows of dotted letters, then colours the sketch at the bottom.

    python tools/make_maxford.py
"""
import json
import os

import cv2
import numpy as np

from ink import PAD, make_ink
from book_colours import page_colours

# How "Show me how" says to write each letter (as in English 3+).
HOW = {
    'a': 'Go round like a ball, then go up, and come down with a little tail.',
    'b': 'Start at the top, go straight down, then go up and round.',
    'c': 'Start at the top and go round, like a big open mouth.',
    'd': 'Go round like a ball, then go up tall, and come down.',
    'e': 'Go across, then round and round.',
    'f': 'Start with a hook at the top, go down, then a line across.',
    'g': 'Go round like a ball, then go down and curl like a hook.',
    'h': 'Go down tall, then go up and make a hump.',
    'i': 'Go straight down, then put a dot on top.',
    'j': 'Go down and curl like a hook, then put a dot on top.',
    'k': 'Go down tall, then in, and out.',
    'l': 'Go straight down from the top, with a little tail.',
    'm': 'Go down, then make two humps.',
    'n': 'Go down, then up and over, one hump.',
    'o': 'Go round and round, like an orange.',
    'p': 'Go down long, then up and round.',
    'q': 'Go round like a ball, then go down long.',
    'r': 'Go down, then up and over a little.',
    's': 'Curve like a snake, round one way, then round the other way.',
    't': 'Go down with a little tail, then a line across.',
    'u': 'Go down and round like a cup, then up and down.',
    'v': 'Slide down, then slide up.',
    'w': 'Down, up, down, up.',
    'x': 'Slide down one way, then slide down the other way.',
    'y': 'Go down and round, then down long with a hook.',
    'z': 'Go across, slide down, then go across again.',
}

BOOK = 'maxford-global-qaida-3-english'
VIDEO_DIR = 'videos/maxford-qaida-3/'

LETTER_PAGE = dict(zip('abcdefghijklmnopqrstuvwxyz',
                       [11, 15, 19, 23, 31, 35, 39, 43, 49, 53, 57, 61, 69, 73, 77, 81, 87, 91, 95, 99, 107, 111, 115,
                        119, 125, 129]))

# The phonic poem printed on each Sound page: the three words with their lines, then the closing line.
POEM = {
    'a': [('apple', 'red and bright'), ('ant', 'so small and light'), ('alligator', 'big and wide'), 'is the sound we say with pride!'],
    'b': [('banana', 'yellow and sweet'), ('ball', 'bouncing at your feet'), ('bear', 'furry and strong'), 'is the sound we say all day long!'],
    'c': [('car', 'drives down the street'), ('cap', 'looks nice and neat'), ('cat', 'soft and small'), 'is the sound we hear in them all!'],
    'd': [('dog', 'runs with the deer'), ('duck', 'swims very near'), ('deer', 'runs by the tree'), 'is the sound, say it with me!'],
    'e': [('envelope', 'ready to send'), ('egg', 'a tasty friend'), ('elephant', 'big and strong'), 'is the sound that sings along!'],
    'f': [('fan', 'goes round and round'), ('frog', 'jumps on the ground'), ('fish', 'swims in the sea'), 'is the sound, say it with me!'],
    'g': [('grapes', 'juicy and sweet'), ('goat', 'with little feet'), ('guava', 'fresh and round'), 'is the sound that we have found!'],
    'h': [('hen', 'pecks on the ground'), ('hat', 'brown and round'), ('house', 'cosy and small'), 'is the sound we hear in them all!'],
    'i': [('inkpot', 'blue and round'), ('insect', 'crawls on the ground'), ('igloo', 'snowy and white'), 'is the sound we say just right!'],
    'j': [('jar', 'with jam inside'), ('jug', 'is by its side'), ('jet', 'flies far away'), 'is the sound we love to say!'],
    'k': [('kitten', 'soft and small'), ('key', 'hangs on the wall'), ('kettle', 'shiny and bright'), 'is the sound we say just right!'],
    'l': [('lion', 'loud and strong'), ('leaf', 'floats along'), ('lemon', 'yellow and bright'), 'is the sound we say just right!'],
    'm': [('monkey', 'jumps with cheer'), ('map', 'shows the way clear'), ('mango', 'yellow and sweet'), 'is the sound we love to repeat!'],
    'n': [('newspaper', 'nice and neat'), ('nuts', 'a crunchy treat'), ('nest', 'up in the tree'), 'is the sound, say it with me!'],
    'o': [('orange', 'juicy and sweet'), ('octopus', 'eight arms so neat'), ('ostrich', 'running to see'), 'is the sound, say it with me!'],
    'p': [('parrot', 'up in the tree'), ('peacock', 'pretty to see'), ('pear', 'juicy and sweet'), 'is the sound we love to repeat!'],
    'q': [('quill', 'soft and light'), ('quilt', 'warm and bright'), ('quail', 'quiet and small'), 'is the sound we hear in them all!'],
    'r': [('racket', 'ready to play'), ('rabbit', 'hops all day'), ('ring', 'shiny and bright'), 'is the sound we say just right!'],
    's': [('snake', 'slides on the ground'), ('sun', 'shines all around'), ('sunflower', 'tall and bright'), 'is the sound we say just right!'],
    't': [('tiger', 'under the tree'), ('turtle', 'slow as can be'), ('tomato', 'red and round'), 'is the sound we have found!'],
    'u': [('umpire', 'ready to play'), ('umbrella', 'keeps rain away'), ('urn', 'pretty and small'), 'The umpire holds an umbrella, standing tall!'],
    'v': [('van', 'moving fast'), ('valley', 'wide and vast'), ('vest', 'fits just right'), 'The van moves through the valley, a lovely sight!'],
    'w': [('watch', 'tells the time'), ('well', 'looks just fine'), ('wood', 'on the ground'), 'is the sound we have found!'],
    'x': [('xylophone', 'plays a song'), ('Christmas tree', 'tall and strong'), ('X-ray', 'bones we see'), 'is the sound, say it with me!'],
    'y': [('yarn', 'soft and long'), ('yo-yo', 'goes up and down'), ('yak', 'big and strong'), 'is the sound we hear all around!'],
    'z': [('zebra', 'black and white'), ('zip', 'close it tight'), ('zoo', 'where animals stay'), 'The zebra at the zoo is out to play!'],
}

# How the voice says each letter's sound (it reads "/a/" as the letter's name otherwise).
SOUND = dict(a='ah', b='buh', c='kuh', d='duh', e='eh', f='fff', g='guh', h='huh', i='ih', j='juh', k='kuh', l='lll',
             m='mmm', n='nnn', o='o', p='puh', q='kwuh', r='rrr', s='sss', t='tuh', u='uh', v='vvv', w='wuh', x='ks',
             y='yuh', z='zzz')

# the sketch to colour at the bottom of each trace page: name, colour word, colour
COLOUR = {
    'a': ('apple', 'red', '#e63946'), 'c': ('cap', 'blue', '#4aa3df'), 'd': ('duck', 'yellow', '#f9c74f'),
    'e': ('elephant', 'grey', '#9aa5b1'), 'g': ('grapes', 'green', '#7bc043'), 'i': ('igloo', 'blue', '#90e0ef'),
    'j': ('jug', 'blue', '#4aa3df'), 'k': ('kangaroo', 'brown', '#c68642'), 'l': ('leaf', 'green', '#43aa8b'),
    'm': ('monkey', 'brown', '#a0522d'), 'n': ('nest', 'brown', '#b07d48'), 'o': ('orange', 'orange', '#ff9f1c'),
    'p': ('parrot', 'green', '#43aa8b'), 'q': ('quail', 'brown', '#b5835a'), 'r': ('rabbit', 'light brown', '#d4a373'),
    's': ('snake', 'green', '#90be6d'), 't': ('turtle', 'green', '#52b788'), 'u': ('umbrella', 'red', '#e63946'),
    'v': ('vase', 'red', '#e63946'), 'w': ('window', 'blue', '#a2d2ff'), 'x': ('xylophone', 'orange', '#f4a261'),
}

# where the three "as in" pictures sit on a Sound page (x from, x to), and the game's view of them
THIRDS = [(4, 33), (34, 60), (61, 98)]
LESSON_VIDEOS = [('Story', 'Story of Letter {L}.mp4'), ('Phonic Poem', 'Letter {L} Phonic Poem.mp4'),
                 ('Vocabulary', 'Letter {L} Vocabulary.mp4')]
# each video gets its own button, stacked at the top left of the big picture: icon and top (%)
VIDEO_BUTTONS = {'Story': ('📖', 20), 'Phonic Poem': ('🎵', 25), 'Vocabulary': ('🔤', 30)}


def page_img(p):
    return cv2.imread('books/%s/p%03d.jpg' % (BOOK, p))


def pct_box(x0, y0, x1, y1, W, H):
    return [round(x0 / W * 100, 2), round(y0 / H * 100, 2), round((x1 - x0) / W * 100, 2), round((y1 - y0) / H * 100, 2)]


def big_letter(im, xa, xb, ya=11, yb=25.8):
    """The hollow letter drawn in colour inside the given part of the page (in %)."""
    H, W = im.shape[:2]
    x0, x1, y0, y1 = int(W * xa / 100), int(W * xb / 100), int(H * ya / 100), int(H * yb / 100)
    m = (im[y0:y1, x0:x1].min(axis=2) < 200).astype(np.uint8)
    m[m.mean(axis=1) > .6] = 0                                   # a guide line running across
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    keep = [i for i in range(1, n) if st[i][4] > 40]
    ys, xs = np.nonzero(np.isin(lab, keep))
    return pct_box(x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1, W, H)


def dotted_row(im, ya, yb, n=5, xa=6, xb=95):
    """The n dotted letters in one writing row, left to right (xa, xb: the part of the page across, in %)."""
    H, W = im.shape[:2]
    y0, y1, x0, x1 = int(H * ya / 100), int(H * yb / 100), int(W * xa / 100), int(W * xb / 100)
    crop = im[y0:y1, x0:x1]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    spread = crop.max(axis=2).astype(int) - crop.min(axis=2)
    dark = (gray < 170) & (spread < 70)
    cols = np.nonzero(dark.sum(axis=0))[0]
    groups, start, prev = [], cols[0], cols[0]
    for c in cols[1:]:
        if c - prev > W * .02:
            groups.append((start, prev)); start = c
        prev = c
    groups.append((start, prev))
    groups = sorted(sorted(groups, key=lambda g: -dark[:, g[0]:g[1] + 1].sum())[:n])
    out = []
    for a, b in groups:
        rows = dark[:, a:b + 1].sum(axis=1)
        ys = np.nonzero(rows)[0]
        # keep the letter itself: the longest stretch of rows with ink, not a stray mark above or below it
        runs, s, pv = [], ys[0], ys[0]
        for v in ys[1:]:
            if v - pv > H * .022:
                runs.append((s, pv)); s = v
            pv = v
        runs.append((s, pv))
        top, bot = max(runs, key=lambda r: rows[r[0]:r[1] + 1].sum())
        out.append(pct_box(x0 + a, y0 + top, x0 + b + 1, y0 + bot + 1, W, H))
    return out


def find_same(im, box, xa, xb, ya=11, yb=25.8):
    """Where the letter in box appears again inside the given part of the page (the second big letter)."""
    H, W = im.shape[:2]
    x, y, w, h = box
    tpl = (im[int(y / 100 * H):int((y + h) / 100 * H), int(x / 100 * W):int((x + w) / 100 * W)].min(axis=2) < 200).astype(np.float32)
    reg = (im[int(ya / 100 * H):int(yb / 100 * H), int(xa / 100 * W):int(xb / 100 * W)].min(axis=2) < 200).astype(np.float32)
    res = cv2.matchTemplate(reg, tpl, cv2.TM_CCORR_NORMED)
    _, _, _, (mx, my) = cv2.minMaxLoc(res)
    return [round(xa + mx / W * 100, 2), round(ya + my / H * 100, 2), w, h]


def fill_ink(page, box):
    """The inside of a hollow letter, as pink ink (same layout as tools/ink.py: the box plus a 25% margin)."""
    im = page_img(page)
    H, W = im.shape[:2]
    x, y, w, h = box
    px, py = w * PAD, h * PAD
    bx = [round(x - px, 2), round(y - py, 2), round(w + 2 * px, 2), round(h + 2 * py, 2)]
    X0, Y0 = int(bx[0] / 100 * W), int(bx[1] / 100 * H)
    X1, Y1 = int((bx[0] + bx[2]) / 100 * W), int((bx[1] + bx[3]) / 100 * H)
    crop = im[Y0:Y1, X0:X1]
    # only the letter's own box (plus a hair) counts, so labels and icons nearby are left out
    lx0, ly0 = int((x - .6) / 100 * W) - X0, int((y - .6) / 100 * H) - Y0
    lx1, ly1 = int((x + w + .6) / 100 * W) - X0, int((y + h + .6) / 100 * H) - Y0
    area = np.zeros(crop.shape[:2], bool)
    area[max(0, ly0):ly1, max(0, lx0):lx1] = True
    line = (crop.min(axis=2) < 215) & area
    line = cv2.morphologyEx(line.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)).astype(bool)
    white = ~line
    white[~area] = True
    n, lab = cv2.connectedComponents(white.astype(np.uint8))
    # depth = how many outlines lie between a white patch and the outside: odd depth is inside the letter
    depth = {lab[0, 0]: 0}
    k = max(7, int(W * .006))          # just wide enough to step over the outline, not over a thin stroke
    frontier = [lab[0, 0]]
    while frontier:
        nxt = []
        for c in frontier:
            near = cv2.dilate((lab == c).astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
            for o in np.unique(lab[near & white]):
                if o not in depth:
                    depth[o] = depth[c] + 1
                    nxt.append(o)
        frontier = nxt
    inside = np.isin(lab, [c for c, d in depth.items() if d % 2 == 1])
    mask = (inside | line).astype(np.float32)
    mask = cv2.GaussianBlur(mask, (3, 3), 0)
    rgba = np.zeros(crop.shape[:2] + (4,), np.uint8)
    rgba[..., :3] = (0x6f, 0x2f, 0xd6)
    rgba[..., 3] = np.clip(mask * 255, 0, 255).astype(np.uint8)
    os.makedirs('books/%s/ink' % BOOK, exist_ok=True)
    name = 'books/%s/ink/p%03d_%d_%d.png' % (BOOK, page, round(x * 10), round(y * 10))
    cv2.imwrite(name, rgba)
    return name, bx


def solid_ink(page, box):
    """A big letter printed solid in colour (with a white dashed guide inside), as pink ink: the letter's own
    colour, its dashes closed over, in the same layout as tools/ink.py (the box plus a 25% margin)."""
    im = page_img(page)
    H, W = im.shape[:2]
    x, y, w, h = box
    px, py = w * PAD, h * PAD
    bx = [round(x - px, 2), round(y - py, 2), round(w + 2 * px, 2), round(h + 2 * py, 2)]
    X0, Y0 = max(0, int(bx[0] / 100 * W)), max(0, int(bx[1] / 100 * H))
    X1, Y1 = int((bx[0] + bx[2]) / 100 * W), int((bx[1] + bx[3]) / 100 * H)
    crop = im[Y0:Y1, X0:X1].astype(int)
    area = np.zeros(crop.shape[:2], bool)
    ax0, ay0 = int((x - .5) / 100 * W) - X0, int((y - .5) / 100 * H) - Y0
    ax1, ay1 = int((x + w + .5) / 100 * W) - X0, int((y + h + .5) / 100 * H) - Y0
    area[max(0, ay0):ay1, max(0, ax0):ax1] = True
    letter = (((crop.max(axis=2) - crop.min(axis=2)) > 80) | (crop.max(axis=2) < 110)) & area
    k = max(5, int(W * .008))
    letter = cv2.morphologyEx(letter.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    # only the letter's big parts (and the dot of i or j), not a bit of the picture beside it
    n, lab, st, _ = cv2.connectedComponentsWithStats(letter)
    big = max(st[1:, 4]) if n > 1 else 0
    keep = np.isin(lab, [i for i in range(1, n) if st[i, 4] > big * .04])
    mask = cv2.GaussianBlur(keep.astype(np.float32), (3, 3), 0)
    rgba = np.zeros(crop.shape[:2] + (4,), np.uint8)
    rgba[..., :3] = (0x6f, 0x2f, 0xd6)
    rgba[..., 3] = np.clip(mask * 255, 0, 255).astype(np.uint8)
    os.makedirs('books/%s/ink' % BOOK, exist_ok=True)
    name = 'books/%s/ink/p%03d_%d_%d.png' % (BOOK, page, round(x * 10), round(y * 10))
    cv2.imwrite(name, rgba)
    return name, bx


# "Touch and feel the letters" (pages 3 to 6): each big letter, where it is printed (the boxes of the page's
# exercise in tools/make_maxford_questions.py), and the picture beside it
TOUCH = {
    3: ('abcdef', ['apple', 'ball', 'cat', 'dog', 'envelope', 'fish'],
        [[9.8, 14.8, 18, 13.3], [55.6, 12.3, 15, 17.3], [9.4, 44.4, 16.3, 13.8], [53.8, 40.4, 16.3, 19.2], [8.8, 70.8, 17.3, 13.8], [55, 68.5, 13.5, 19.5]]),
    4: ('ghijkl', ['grapes', 'house', 'igloo', 'jug', 'kettle', 'lion'],
        [[9.1, 14.8, 14.6, 16], [54.6, 12.8, 13.5, 18.3], [11.3, 42, 6, 15.5], [56.3, 40.4, 10, 19.7], [9.1, 68.5, 14, 18.5], [58.1, 68.7, 5, 17.7]]),
    5: ('mnopqr', ['mango', 'nest', 'orange', 'peacock', 'quilt', 'racket'],
        [[9.4, 13.8, 21.9, 12], [55.6, 13.8, 14.1, 12], [9.1, 40.6, 18.4, 13.8], [55.6, 39.9, 15.6, 17.5], [7.5, 67.9, 22.5, 17.9], [55.6, 68.8, 12.9, 14.2]]),
    6: ('stuvwxyz', ['sunflower', 'turtle', 'umbrella', 'vest', 'well', 'xylophone', 'yak', 'zebra'],
        [[11.9, 12.8, 10.4, 11.8], [53.5, 11.3, 12.8, 15.8], [10.4, 32.5, 13.6, 12.4], [54.1, 35, 13.4, 12.3],
         [6.3, 55.2, 21.5, 12.2], [54.6, 54.7, 12.9, 11.6], [11, 76, 12.1, 14.6], [55, 77.4, 11.9, 11.5]]),
}


def touch_page(page):
    """Touch and feel the letters: trace each big letter in turn, hearing how it is written and its sound."""
    letters, words, boxes = TOUCH[page]
    steps = []
    for k, (L, word, box) in enumerate(zip(letters, words, boxes)):
        src, ib = solid_ink(page, box)
        first = 'Touch and feel the letters, and say their sounds. ' if k == 0 else ''
        steps.append({'say': f'{first}The letter {L}. {HOW[L]} {L} says {SOUND[L]}, as in {word}.',
                      'marks': [{'glyph': L, 'box': box, 'ink': {'src': src, 'box': ib}}]})
    steps[-1]['say'] += ' Well done! Now it is your turn.'
    return {'type': 'fill', 'title': 'Touch and feel the letters', 'steps': steps, 'colours': page_colours(BOOK, page)}


def sketch(im):
    """The outline drawing to colour at the bottom of a trace page, as an ellipse (cx, cy, rx, ry in %)."""
    H, W = im.shape[:2]
    x0, x1, y0, y1 = int(W * .4), int(W * .98), int(H * .61), int(H * .97)
    crop = im[y0:y1, x0:x1]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    spread = crop.max(axis=2).astype(int) - crop.min(axis=2)
    dark = ((gray < 120) & (spread < 60)).astype(np.uint8)
    dark = cv2.dilate(dark, np.ones((7, 7), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(dark)
    i = 1 + int(np.argmax(st[1:, 4]))
    sx, sy, sw, sh = st[i][:4]
    cx, cy = (x0 + sx + sw / 2) / W * 100, (y0 + sy + sh / 2) / H * 100
    return [round(cx, 1), round(cy, 1), round(sw / W * 100 * .36, 1), round(sh / H * 100 * .36, 1)]


def videos_for(L, names):
    return [{'title': t, 'src': VIDEO_DIR + n.format(L=L)} for t, n in names if os.path.exists(VIDEO_DIR + n.format(L=L))]


def say_sound(text, L):
    return text.replace('/%s/' % L, SOUND[L])


def letter_page(L, p):
    words = [w for w, _ in POEM[L][:3]]
    s = SOUND[L]
    end = POEM[L][3]
    end = end if end[0].isupper() else f'{s} {end}'
    vids = videos_for(L, LESSON_VIDEOS)
    return [{'type': 'videos', 'label': v['title'], 'icon': VIDEO_BUTTONS[v['title']][0], 'title': v['title'] + ' of letter ' + L,
             'button': {'x': 45, 'y': VIDEO_BUTTONS[v['title']][1]}, 'videos': [v]} for v in vids] + [game_for(L, words)]


def game_for(L, words):
    return {
        'type': 'game', 'title': f'Find the {L} words!', 'button': {'x': 30, 'y': 63},
        'crop': {'x': 2, 'y': 67, 'w': 96, 'h': 23},
        'targets': [{'name': w, 'x': a, 'y': 68, 'w': b - a, 'h': 21, 'say': f'{w[0].upper() + w[1:]} begins with {SOUND[L]}.'}
                    for (a, b), w in zip(THIRDS, words)]}


def trace_page(L, page):
    im = page_img(page)
    big1 = big_letter(im, 20.5, 42)
    # the second big letter has guide arrows and start dots on it; it is the same letter, so it is found by
    # matching the first one, and takes the first one's ink
    big2 = find_same(im, big1, 66, 99, 10, 27)
    rows = [dotted_row(im, a, b) for a, b in ((27.9, 38.2), (38.4, 50.3), (50.6, 61.6))]
    src1, ib1 = fill_ink(page, big1)
    ib2 = [round(big2[0] - big1[2] * PAD, 2), round(big2[1] - big1[3] * PAD, 2), ib1[2], ib1[3]]
    def marks(bs):
        out = []
        for b in bs:
            src, box = make_ink(BOOK, page, b)
            m = {'glyph': L, 'box': b}
            # letters printed too faint to cut out (like the small l) are simply drawn by the pencil
            if cv2.imread(src, cv2.IMREAD_UNCHANGED)[..., 3].mean() > 8:
                m['ink'] = {'src': src, 'box': box}
            else:
                os.remove(src)
            out.append(m)
        return out
    steps = [
        {'say': f'Let us write the letter {L}. {HOW[L]}', 'marks': [{'glyph': L, 'box': big1, 'ink': {'src': src1, 'box': ib1}}]},
        {'say': 'Again! ' + HOW[L], 'marks': [{'glyph': L, 'box': [big2[0], big2[1], big1[2], big1[3]], 'ink': {'src': src1, 'box': ib2}}]},
        {'say': 'Now trace the small letters.', 'marks': marks(rows[0])},
        {'say': 'Next line.', 'marks': marks(rows[1])},
        {'say': 'One more line. Good job!', 'marks': marks(rows[2])},
    ]
    if L in COLOUR:
        name, word, col = COLOUR[L]
        cx, cy, rx, ry = sketch(im)
        steps.append({'say': f'Now let us colour the {name}. Let us make it {word}! Well done! Now it is your turn.',
                      'marks': [{'scribble': page_colours(BOOK, page)[0], 'cx': cx, 'cy': cy, 'rx': rx, 'ry': ry}]})
    else:
        steps[-1]['say'] = 'One more line. Well done! Now it is your turn.'
    act = {'type': 'fill', 'title': 'Trace and say the sound', 'steps': steps}
    act['colours'] = page_colours(BOOK, page)
    how = videos_for(L, [('How to write ' + L, 'Letter {L} Formation.mp4')])
    if how:
        act['video'] = how[0]
    elif L in PARTS and videos_for(L, [('', PARTS_FILE)]):
        start, end = PARTS[L][0]
        act['video'] = {'title': 'How to write ' + L, 'src': part_src(L, start, end)}
    return act


def dotted_bands(im, ya=26, yb=80, xa=6, xb=95):
    """The writing rows of dotted letters between ya and yb (in %), top to bottom, as (top, bottom) in %."""
    H, W = im.shape[:2]
    y0, y1, x0, x1 = int(H * ya / 100), int(H * yb / 100), int(W * xa / 100), int(W * xb / 100)
    crop = im[y0:y1, x0:x1]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    spread = crop.max(axis=2).astype(int) - crop.min(axis=2)
    dark = (gray < 170) & (spread < 70)
    rows = np.nonzero(dark.sum(axis=1) > 2)[0]
    bands, s, pv = [], rows[0], rows[0]
    for v in rows[1:]:
        if v - pv > H * .015:
            bands.append((s, pv)); s = v
        pv = v
    bands.append((s, pv))
    bands = [(a, b) for a, b in bands if b - a > H * .03]          # a row of letters, not a stray mark
    return [(round((y0 + a) / H * 100 - .8, 2), round((y0 + b) / H * 100 + .8, 2)) for a, b in bands]


def write_page(L, page):
    """"Trace, write and say the sound": the big guided letter, the small dotted letter on its lines, then four
    rows of five dotted letters; the last row of start marks is the child's own writing."""
    im = page_img(page)
    big = big_letter(im, 42, 64, 10, 26)
    small = dotted_row(im, 10, 27.5, n=1, xa=68, xb=95)
    bands = dotted_bands(im)
    assert len(bands) == 4, (L, page, bands)
    rows = [dotted_row(im, a, b) for a, b in bands]
    src, ib = fill_ink(page, big)
    def marks(bs):
        out = []
        for b in bs:
            s, box = make_ink(BOOK, page, b)
            m = {'glyph': L, 'box': b}
            if cv2.imread(s, cv2.IMREAD_UNCHANGED)[..., 3].mean() > 8:
                m['ink'] = {'src': s, 'box': box}
            else:
                os.remove(s)
            out.append(m)
        return out
    steps = [{'say': f'Let us write the letter {L}. {HOW[L]}', 'marks': [{'glyph': L, 'box': big, 'ink': {'src': src, 'box': ib}}]}]
    if small:
        steps.append({'say': 'Now the small one on its lines.', 'marks': marks(small)})
    steps += [{'say': 'Now trace the dotted letters.', 'marks': marks(rows[0])},
              {'say': 'Next line.', 'marks': marks(rows[1])},
              {'say': 'Next line.', 'marks': marks(rows[2])},
              {'say': f'One more line. Then write {L} on your own on the last line. Well done!', 'marks': marks(rows[3])}]
    act = {'type': 'fill', 'title': 'Trace, write and say the sound', 'steps': steps}
    act['colours'] = page_colours(BOOK, page)
    return act


def az_page(page):
    """Review: "Trace the letters a - z": rows of five dotted letters, a to z."""
    im = page_img(page)
    letters = iter('abcdefghijklmnopqrstuvwxyz')
    steps = []
    for k, (a, b) in enumerate(dotted_bands(im, 10, 93)):
        row = dotted_row(im, a, b, n=5 if k < 5 else 2)
        marks = []
        for box in row:
            L = next(letters)
            s, ib = make_ink(BOOK, page, box)
            marks.append({'glyph': L, 'box': box, 'ink': {'src': s, 'box': ib}})
        names = ', '.join(m['glyph'] for m in marks)
        steps.append({'say': f'Trace {names}.' if k else f'Let us trace the letters, a to z. Trace {names}.', 'marks': marks})
    assert next(letters, None) is None, 'all 26 letters found'
    steps[-1]['say'] += ' Well done! You know all the letters!'
    return {'type': 'fill', 'title': 'Trace the letters a - z', 'steps': steps, 'colours': page_colours(BOOK, page)}


def dotted_shapes(im, box, min_size=2.0, join=21):
    """The dotted lines and curves to trace inside box (x, y, w, h in %), top to bottom and left to right."""
    H, W = im.shape[:2]
    x, y, w, h = box
    x0, y0, x1, y1 = int(W * x / 100), int(H * y / 100), int(W * (x + w) / 100), int(H * (y + h) / 100)
    crop = im[y0:y1, x0:x1]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    spread = crop.max(axis=2).astype(int) - crop.min(axis=2)
    dark = ((gray < 170) & (spread < 70)).astype(np.uint8)
    joined = cv2.dilate(dark, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (join, join)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(joined)
    out = []
    for i in range(1, n):
        sx, sy, sw, sh, area = st[i]
        b = pct_box(x0 + sx, y0 + sy, x0 + sx + sw, y0 + sy + sh, W, H)
        if max(b[2], b[3]) >= min_size:
            out.append(b)
    return sorted(out, key=lambda b: (round(b[1] / 3), b[0]))


def band_pieces(box, rtl=False):
    """A long white path split into equal boxes across, as few as keep each box plus the 25% margin that
    tools/ink.py cuts on the page (a margin off the page would stretch the ink)."""
    x, y, w, h = box
    assert y - h * PAD >= 0 and y + h * (1 + PAD) <= 100, box
    for n in range(1, 8):
        pieces = [[round(x + w * k / n, 2), y, round(w / n, 2), h] for k in range(n)]
        if all(p[0] - p[2] * PAD >= 0 and p[0] + p[2] * (1 + PAD) <= 100 for p in pieces):
            return pieces[::-1] if rtl else pieces
    raise ValueError(box)


def lines_page(page, title, areas, colour_say):
    """Pre-writing: trace each dotted line or curve (its own shape, cut from the page), then colour the picture."""
    im = page_img(page)
    steps = []
    for say, box in areas:
        marks = []
        # [x, y, w, h, 'band']: a white path on a coloured band, one shape in its own box;
        # [x, y, w, h]: grey dotted lines, found one by one
        band = box[4] if len(box) == 5 else None       # 'band' (left to right) or 'band-rtl'
        box = box[:4]
        for b in (band_pieces(box, band == 'band-rtl') if band else dotted_shapes(im, box)):
            s, ib = make_ink(BOOK, page, b)
            marks.append({'glyph': 'ur', 'box': b, 'ink': {'src': s, 'box': ib}})
        steps.append({'say': say, 'marks': marks})
    steps[-1]['say'] += ' ' + colour_say
    return {'type': 'fill', 'title': title, 'steps': steps, 'colours': page_colours(BOOK, page)}


# One video for the three pages after a Sound page ("Letter b Formation and Activities.mp4"): the part for each
# page, as (start, end) in seconds, found by looking through the video. end None = to the end of the video.
PARTS_FILE = 'Letter {L} Formation and Activities.mp4'
PARTS = {
    'b': [(0, 67), (67, 95), (95, None)],
}
# where the Watch button sits on the second and third page (x, y in %), and what the part shows
PART_PAGES = [('Trace, write and say {L}', (66, 22)), ('Activities for {L}', (72, 52.5))]


def part_src(L, start, end):
    return VIDEO_DIR + PARTS_FILE.format(L=L) + '#t=%g' % start + (',%g' % end if end else '')


def part_pages(L, p):
    """Watch buttons on the "Trace, write and say" page and the Activities page, each playing its own part."""
    if L not in PARTS or not videos_for(L, [('', PARTS_FILE)]):
        return {}
    out = {}
    for k, ((start, end), (title, (x, y))) in enumerate(zip(PARTS[L][1:], PART_PAGES)):
        t = title.format(L=L)
        out[p + 2 + k] = [{'type': 'videos', 'label': 'Watch', 'icon': '🎬', 'title': t, 'button': {'x': x, 'y': y},
                           'videos': [{'title': t, 'src': part_src(L, start, end)}]}]
    return out


if __name__ == '__main__':
    acts = {}
    for L, p in LETTER_PAGE.items():
        acts[p] = letter_page(L, p)
        acts[p + 1] = trace_page(L, p + 1)
        acts[p + 2] = write_page(L, p + 2)
        acts.update(part_pages(L, p))
        print(L, end=' ', flush=True)
    # Pre-writing pages 7 to 10: trace the lines from their start dots, then colour the picture.
    acts[7] = lines_page(7, 'Standing lines', [
        ('Standing lines! Start at the dot and go straight down.', [8, 13, 40, 35]),
        ('Again! Straight down from each dot.', [52, 13, 40, 35])], 'Now colour the house.')
    acts[8] = lines_page(8, 'Sleeping lines', [
        ('Sleeping lines! Start at the dot and go straight across.', [8, 13, 85, 16]),
        ('Again! Straight across from each dot.', [8, 31, 85, 16])], 'Now colour the well.')
    acts[9] = lines_page(9, 'Curved lines', [
        ('Curved lines! Start at the dot and curve round.', [8, 12.5, 84, 11]),
        ('Again! Curve round from each dot.', [8, 25, 84, 25]),
        ('Now trace the big curves on the orange page, one column at a time.', [9, 53, 20.5, 37, 'band']),
        ('Next column.', [29.5, 53, 20.5, 37, 'band']),
        ('Next column.', [50, 53, 20.5, 37, 'band']),
        ('Last column.', [70.5, 53, 21, 37, 'band'])], 'Well done!')
    acts[10] = lines_page(10, 'Loops and curves', [
        ('Loops! Start at the dot by the fish and go round and round.', [24, 13, 70, 12, 'band']),
        ('Waves! From the turtle\'s dot, go up and down.', [13, 27, 75, 12, 'band-rtl']),
        ('Zigzag curves! From the octopus\' dot, up and down.', [23, 38.5, 67, 11, 'band']),
        ('Circles! From the submarine\'s dot, go round each circle.', [14, 52.5, 56, 9, 'band']),
        ('Bumps! From the starfish\'s dot, go over each bump.', [27, 65.5, 63, 9, 'band']),
        ('Clouds! From the seahorse\'s dot, go round each cloud.', [26, 77.5, 56, 10, 'band'])], 'Well done!')
    acts[133] = az_page(133)
    for p in TOUCH:
        acts[p] = touch_page(p)
    acts = dict(sorted(acts.items()))
    print()
    with open('books/activities-maxford.js', 'w', encoding='utf-8', newline='\n') as f:
        f.write('// Generated by tools/make_maxford.py: letters a to z of Maxford Global Qaida 3+ English.\n')
        f.write("window.BOOK_ACTIVITIES['%s'] = " % BOOK)
        f.write(json.dumps(acts, indent=1, ensure_ascii=False))
        f.write(';\n')
    print(len(acts), 'pages')
