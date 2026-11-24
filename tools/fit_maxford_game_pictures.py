"""Show each picture of the Qaida 3+ English word games whole (the bear's head was cut off), without its word.

    python tools/fit_maxford_game_pictures.py          # writes books/game-pictures-maxford.js
    python tools/fit_maxford_game_pictures.py --show   # and an overlay per game in tools/_game_pictures/

Each letter's game ("Find the b words!") shows the row of three pictures printed under "/b/ as in...". The
generated crop was one strip for the whole row, which cut a tall picture (the bear) and showed the word bands
under the pictures. Here each picture is measured on the page: in its column, the tallest run of printed rows
above the word band is the picture. The game then shows from the top of the tallest picture to the bottom of
the lowest, the words left out; each tapped box is its picture; and print above a short picture inside the crop
(the "/b/ as in..." heading) is covered with paper white. Loaded after books/game-crops.js, so it wins.
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BOOK = 'maxford-global-qaida-3-english'
TOP, BOTTOM = 57.0, 95.0      # where the row of pictures can be, % of the page


def load():
    script = ("global.window={BOOK_ACTIVITIES:{}};require('./books/activities-maxford.js');require('./books/library.js');"
              "const b=window.PDF_BOOKS.find(b=>b.id==='%s');console.log(JSON.stringify({dir:b.dir,acts:window.BOOK_ACTIVITIES['%s']}))") % (BOOK, BOOK)
    out = subprocess.run(['node', '-e', script], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', check=True).stdout
    return json.loads(out)


def runs_of(on, gap_max):
    """Runs of True in a 1-D mask, joining runs split by at most gap_max False values: [(start, end)]."""
    runs, start, gap, end = [], None, 0, 0
    for i, v in enumerate(on):
        if v:
            if start is None:
                start = i
            gap, end = 0, i
        elif start is not None:
            gap += 1
            if gap > gap_max:
                runs.append((start, end))
                start, gap = None, 0
    if start is not None:
        runs.append((start, end))
    return runs


def row_top(ink):
    """Where the row of pictures can start: under the letter's big story picture, which fills the right half."""
    h, w = ink.shape
    full = ink[:, int(.45 * w):int(.97 * w)].mean(axis=1) > .85
    rows = [y for y in range(int(.45 * h), int(.75 * h)) if full[y]]
    return (max(rows) / h * 100 + .6) if rows else TOP


def picture(ink, x0, x1, top=TOP):
    """The picture in a column (x0..x1 in pixels): (top, bottom, left, right) in pixels, or None."""
    h, w = ink.shape
    y0, y1 = int(top / 100 * h), int(BOTTOM / 100 * h)
    col = ink[y0:y1, x0:x1]
    rows = col.mean(axis=1) > .015
    runs = runs_of(rows, h * .009)           # a picture's parts (a hat over a face) stay one picture
    if not runs:
        return None
    a, b = max(runs, key=lambda r: r[1] - r[0])     # the picture is the tallest thing in its column
    cols = col[a:b + 1].mean(axis=0) > .02
    across = runs_of(cols, w * .028)
    l, r = max(across, key=lambda r: r[1] - r[0])   # its widest piece, not the edge of a neighbour
    return y0 + a, y0 + b, x0 + l, x0 + r


def main(show):
    data = load()
    out, notes = {}, []
    for page, acts in sorted(data['acts'].items(), key=lambda kv: int(kv[0])):
        for i, g in enumerate(acts if isinstance(acts, list) else [acts]):
            if g.get('type') != 'game':
                continue
            path = os.path.join(ROOT, data['dir'], 'p%03d.jpg' % int(page))
            im = np.asarray(Image.open(path).convert('RGB')).astype(int)
            H, W = im.shape[:2]
            # printed ink: anything that is not the white paper (pale pictures, an igloo, count too) ...
            ink = (im.min(axis=2) < 236) | (im.max(axis=2) - im.min(axis=2) > 24)
            # ... except the pale word bands under the pictures: rows low on the page that are mostly one soft colour
            soft = (im.min(axis=2) > 185) & (im.min(axis=2) < 246)
            band_rows = soft.mean(axis=1) > .45
            band_rows[:int(.78 * H)] = False
            ink[band_rows] = False
            pct = lambda v, n: round(v / n * 100, 2)
            boxes = []
            start = row_top(ink)
            # the "/b/ as in..." heading: a short line of print at the left, just under the story picture; it is
            # left out of the pictures and covered in the game
            heading = None
            hx0, hx1 = int(.01 * W), int(.36 * W)
            hrows = ink[:, hx0:hx1].mean(axis=1) > .01
            hy = int(start / 100 * H)
            while hy < int(.80 * H) and not hrows[hy]:
                hy += 1
            hy_end = hy
            while hy_end < int(.80 * H) and hrows[hy_end]:
                hy_end += 1
            if hy_end - hy < .05 * H:
                cols = np.where(ink[hy:hy_end, hx0:hx1].mean(axis=0) > 0)[0]
                if len(cols):
                    heading = (hx0 + cols[0], hy, hx0 + cols[-1], hy_end)
                    ink[hy:hy_end + 2, hx0 + cols[0]:hx0 + cols[-1] + 1] = False
            for t in g['targets']:
                x0, x1 = int(t['x'] / 100 * W), int((t['x'] + t['w']) / 100 * W)
                found = picture(ink, x0, x1, start)
                if not found:
                    notes.append(f'p{page}: no picture found for {t["name"]}')
                    boxes.append(None)
                    continue
                top, bottom, left, right = found
                boxes.append((pct(left, W), pct(top, H), pct(right, W), pct(bottom, H)))
            if None in boxes:
                continue
            pad = 1.0
            cy0 = max(0, min(b[1] for b in boxes) - pad)
            cy1 = min(100, max(b[3] for b in boxes) + .35)     # just under the lowest picture, before the word bands
            crop = {'x': g['crop']['x'], 'y': round(cy0, 2), 'w': g['crop']['w'], 'h': round(cy1 - cy0, 2)}
            targets = [{**t, 'x': round(b[0] - .6, 2), 'y': round(b[1] - .6, 2), 'w': round(b[2] - b[0] + 1.2, 2), 'h': round(b[3] - b[1] + 1.2, 2)}
                       for t, b in zip(g['targets'], boxes)]
            # anything printed in the crop that is not one of the pictures (the "/b/ as in..." heading above a
            # short picture, the top of a word band under one) is covered with paper white
            cx0, cx1 = int(crop['x'] / 100 * W), int((crop['x'] + crop['w']) / 100 * W)
            keep = np.zeros((H, W), bool)
            for b in boxes:
                keep[int((b[1] - .8) / 100 * H):int((b[3] + .8) / 100 * H), int((b[0] - .8) / 100 * W):int((b[2] + .8) / 100 * W)] = True
            stray = ink & ~keep
            hide = []
            if heading:
                hide.append({'x': pct(heading[0], W) - .4, 'y': pct(heading[1], H) - .4, 'w': pct(heading[2] - heading[0], W) + .8, 'h': pct(heading[3] - heading[1], H) + .8})
            # other stray print: only above the pictures (beside them it may be a picture's own loose part)
            ys, ye = int(cy0 / 100 * H), int(max(b[1] for b in boxes) / 100 * H)
            region = stray[ys:ye, cx0:cx1]
            if region.any():
                rr, cc = np.where(region)
                # group the stray print into boxes by columns of the row (one per picture gap or heading)
                for x_lo, x_hi in [(cx0, cx1)]:
                    sel = (cc + cx0 >= x_lo) & (cc + cx0 < x_hi)
                    if sel.sum() < 30:
                        continue
                    hy0, hy1 = rr[sel].min() + ys, rr[sel].max() + ys
                    hx0, hx1 = cc[sel].min() + cx0, cc[sel].max() + cx0
                    hide.append({'x': pct(hx0, W) - .3, 'y': pct(hy0, H) - .3, 'w': pct(hx1 - hx0, W) + .6, 'h': pct(hy1 - hy0, H) + .6})
            # a hidden box must not cover a picture: keep only the part above the pictures' tops
            safe = []
            for hb in hide:
                for b in boxes:
                    if hb['x'] < b[2] and b[0] < hb['x'] + hb['w'] and hb['y'] + hb['h'] > b[1]:
                        hb['h'] = max(0, b[1] - .4 - hb['y'])
                if hb['h'] > .3:
                    safe.append({k: round(v, 2) for k, v in hb.items()})
            out.setdefault(page, {})[str(i)] = {'crop': crop, 'targets': targets, **({'hide': safe} if safe else {})}
            notes.append(f'p{page} {g["title"]}: crop y {crop["y"]}-{round(cy1, 1)}' + (f', hides {len(safe)}' if safe else ''))
            if show:
                img = Image.open(path).convert('RGB')
                d = ImageDraw.Draw(img)
                Wp, Hp = img.size
                r = lambda o: [o['x'] / 100 * Wp, o['y'] / 100 * Hp, (o['x'] + o['w']) / 100 * Wp, (o['y'] + o['h']) / 100 * Hp]
                d.rectangle(r(crop), outline=(0, 120, 255), width=5)
                for t in targets:
                    d.rectangle(r(t), outline=(255, 0, 150), width=4)
                for hb in safe:
                    d.rectangle(r(hb), fill=(255, 255, 255), outline=(0, 200, 0), width=3)
                y0p, y1p = int(max(0, cy0 - 8) / 100 * Hp), int(min(100, cy1 + 8) / 100 * Hp)
                img = img.crop((0, y0p, Wp, y1p))
                img.thumbnail((700, 400))
                os.makedirs(os.path.join(ROOT, 'tools', '_game_pictures'), exist_ok=True)
                img.save(os.path.join(ROOT, 'tools', '_game_pictures', f'p{int(page):03}.jpg'), quality=82)
    with open(os.path.join(ROOT, 'books', 'game-pictures-maxford.js'), 'w', encoding='utf-8') as f:
        f.write('// Generated by tools/fit_maxford_game_pictures.py: each word game shows its pictures whole, without their words.\n')
        f.write('// Loaded after books/game-crops.js; its fixes win.\n')
        f.write("window.GAME_FIXES = window.GAME_FIXES || {};\n")
        f.write("window.GAME_FIXES['%s'] = Object.assign(window.GAME_FIXES['%s'] || {}, " % (BOOK, BOOK))
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write(');\n')
    print('\n'.join(notes))


if __name__ == '__main__':
    main('--show' in sys.argv)
