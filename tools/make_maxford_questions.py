"""The printed exercises of Maxford Global Qaida 3+ English as questions (app.js openQuestion).

Every position is % of the page, measured on a grid drawn over the page picture. Writes
books/questions-maxford.js. Kinds: choose (circle, tick or cross out: tap the right ones), write (on the
printed lines), colour (the outlined pictures or letters, in their colours), match (draw a line between dots).

    python tools/make_maxford_questions.py
"""
import json
from pathlib import Path

BOOK = 'maxford-global-qaida-3-english'
C = {'red': '#e63946', 'orange': '#f4a261', 'yellow': '#f9c74f', 'green': '#43aa8b', 'leaf': '#4caf50', 'blue': '#4aa3df',
     'purple': '#7b5ea7', 'pink': '#ff8fab', 'brown': '#8d5524', 'light brown': '#d4a373', 'grey': '#9aa5b1', 'black': '#222222'}
MANY = [C[k] for k in ('red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink')]


def box(x, y, w, h):
    return {'x': x, 'y': y, 'w': w, 'h': h}


def Q(kind, title, say, button, crop, **more):
    return {'type': 'question', 'kind': kind, 'title': title, 'say': say, 'button': {'x': button[0], 'y': button[1]}, 'crop': box(*crop), **more}


def tap(x, y, correct, label, w=5.2, h=4.8):
    """A thing to tap, centred at (x, y)."""
    return {'x': round(x - w / 2, 2), 'y': round(y - h / 2, 2), 'w': w, 'h': h, 'correct': correct, 'label': label}


def letters(options, w=5.2, h=5):
    return [tap(x, y, ok, label, w, h) for x, y, ok, label in options]


def pictures(options, w=13, h=11):
    return [tap(x, y, ok, label, w, h) for x, y, ok, label in options]


def choose(title, say, button, crop, options):
    return Q('choose', title, say, button, crop, options=options)


def write(title, say, button, crop, lines, trace=None):
    """trace ('letter' or 'number'): the boxes hold big printed letters (or numbers), traced over themselves."""
    more = {'trace': trace} if trace else {}
    return Q('write', title, say, button, crop, hint={'x': lines[0][0] + 2, 'y': lines[0][1] + 2}, lines=[box(*l) for l in lines], **more)


def colour(title, say, button, crop, parts):
    """parts: (name, (x, y, w, h), colours, letter) - letter: only the letter's band is coloured."""
    out = []
    for name, b, colours, *letter in parts:
        part = {'part': name, 'box': box(*b), 'colours': colours}
        if letter and letter[0]:
            part['letter'] = True
        out.append(part)
    first = out[0]['box']
    return Q('colour', title, say, button, crop, hint={'x': first['x'] + first['w'] / 2, 'y': first['y'] + first['h'] / 2}, parts=out)


def match(title, say, button, crop, dots):
    return Q('match', title, say, button, crop, dots=[{'id': i, 'x': x, 'y': y} for i, x, y in dots])


# ---- shared wordings ----
def circle_letter(L, crop, options, button):
    return choose(f'Circle the letter "{L}".', f'Find every letter {L}. Tap each one to circle it.', button, crop,
                  letters([(x, y, l == L, l) for x, y, l in options], 6, 6.5))


def trace_first(title, crop, lines, button):
    return write(title, 'Trace the dotted letter at the start of each word.', button, crop, lines)


def trace_letters(L, crop, lines, button):
    return write(f'Trace the letter {L}.', f'Trace the dotted letter {L} at the top of each box.', button, crop, lines)


def tick(crop, options, button):
    return choose('Tick the correct beginning sound for each picture.', 'Say the name of each picture. Tap the box under the sound it begins with.',
                  button, crop, letters(options, 6, 5.5))


def write_first(title, crop, lines, button):
    return write(title, 'Say the name of each picture. Write the letter it begins with on its lines.', button, crop, lines)


def circle_sound(crop, options, button, title='Circle the correct beginning sound for each picture.'):
    return choose(title, 'Say the name of each picture. Tap the letter it begins with.', button, crop, letters(options, 5, 6))


def match_letter(L, crop, pairs, button):
    """The letter in the middle with a dot for each picture that begins with it; pictures that do not, have no partner."""
    dots = []
    for name, (lx, ly), (px, py) in pairs:
        dots += [(name, lx, ly), (name, px, py)]
    return match(f'Match the letter {L} with the correct pictures.', f'Draw a line from the letter {L} to each picture that begins with {L}.', button, crop, dots)


def touch_and_feel(boxes):
    """The big letters with numbered arrows: trace each one with a finger and say its sound."""
    return [write('Touch and feel the letters and say the sounds.', 'Trace each big letter, following the arrows. Say its sound and the name of its picture.',
                  (43, 95.5), (5, 10, 90, 83), boxes, trace='letter')]


def tap_group(title, say, button, items, group):
    """A vocabulary page: tap every picture of one group (the animals, the fruits)."""
    return choose(title, say, button, (8, 26, 86, 64), pictures([(x, y, kind == group, name) for x, y, name, kind in items], 14, 13))


AZ_ROWS = [[7.5, y, 85, 10.6] for y in (14.7, 27.8, 41, 54, 67.2, 80.3)]

Q_PAGES = {
    3: touch_and_feel([[9.8, 14.8, 18, 13.3], [55.6, 12.3, 15, 17.3], [9.4, 44.4, 16.3, 13.8], [53.8, 40.4, 16.3, 19.2],
                       [8.8, 70.8, 17.3, 13.8], [55, 68.5, 13.5, 19.5]]),
    4: touch_and_feel([[9.1, 14.8, 14.6, 16], [54.6, 12.8, 13.5, 18.3], [11.3, 42, 6, 15.5], [56.3, 40.4, 10, 19.7],
                       [9.1, 68.5, 14, 18.5], [58.1, 68.7, 5, 17.7]]),
    5: touch_and_feel([[9.4, 13.8, 21.9, 12], [55.6, 13.8, 14.1, 12], [9.1, 40.6, 18.4, 13.8], [55.6, 39.9, 15.6, 17.5],
                       [7.5, 67.9, 22.5, 17.9], [55.6, 68.8, 12.9, 14.2]]),
    6: touch_and_feel([[11.9, 12.8, 10.4, 11.8], [53.5, 11.3, 12.8, 15.8], [10.4, 32.5, 13.6, 12.4], [54.1, 35, 13.4, 12.3],
                       [6.3, 55.2, 21.5, 12.2], [54.6, 54.7, 12.9, 11.6], [11, 76, 12.1, 14.6], [55, 77.4, 11.9, 11.5]]),
    29: [tap_group('Identify the animals.', 'Say each name aloud. Then tap every animal (not the birds).', (47, 25.1), [
        (16.3, 33, 'cat', 'animal'), (40.3, 36.5, 'horse', 'animal'), (18.1, 53.7, 'goat', 'animal'), (40, 59.7, 'tiger', 'animal'),
        (17.5, 74.5, 'rabbit', 'animal'), (39.4, 78.9, 'sheep', 'animal'), (59.4, 35.5, 'sparrow', 'bird'), (85, 38.5, 'pigeon', 'bird'),
        (58.4, 52.8, 'parrot', 'bird'), (85, 58.2, 'duck', 'bird'), (59.8, 72, 'owl', 'bird'), (83.8, 77.9, 'eagle', 'bird')], 'animal')],
    67: [tap_group('Identify the fruits.', 'Say each name aloud. Then tap every fruit (not the vegetables).', (84.5, 19.3), [
        (16.9, 34, 'onion', 'veg'), (39, 38.5, 'potato', 'veg'), (20.6, 53.3, 'carrot', 'veg'), (38.8, 61.1, 'peas', 'veg'),
        (16.9, 72.8, 'cucumber', 'veg'), (38.8, 78.9, 'brinjal', 'veg'), (59.4, 34.5, 'apple', 'fruit'), (84, 39.4, 'pear', 'fruit'),
        (58.5, 53.3, 'mango', 'fruit'), (83.8, 61.1, 'strawberry', 'fruit'), (59.4, 72.5, 'grapes', 'fruit'), (81.9, 79.9, 'peach', 'fruit')], 'fruit')],
    134: [write('Write the letters a - z.', 'Write the small letters a to z in order on the lines.', (42, 10.6), (6, 13, 88, 79), AZ_ROWS)],
    135: [write('Write the letters a - z.', 'Write the small letters a to z in order on the lines.', (42, 10.6), (6, 13, 88, 79), AZ_ROWS)],
    14: [
        circle_letter('a', (7, 12, 86, 23.5), [
            (12.5, 20.2, 'r'), (21.5, 20.7, 'b'), (30.3, 17, 'a'), (50, 17.8, 'a'), (40.3, 22.7, 'm'), (52.5, 24.7, 'm'),
            (65.3, 21.9, 'b'), (75.6, 20.2, 'r'), (84, 16.6, 'a'), (85.8, 22.9, 's'), (15.5, 29.6, 'a'), (27.8, 27.6, 'd'),
            (41.3, 29.6, 'a'), (59.4, 30.8, 's'), (71.5, 29.6, 'g'), (85.4, 30.8, 'a')], (36, 10.4)),
        trace_first('Trace the letter that makes the beginning sound.', (8, 38, 82, 41),
                    [[48, 41.5, 40, 9], [23.5, 55.5, 29, 9], [50, 69, 25, 9]], (68, 36.5)),
    ],
    18: [
        trace_letters('b', (9, 12.5, 82, 39), [[17.5, 14.5, 11.5, 9.5], [44, 14.5, 11.5, 9.5], [71, 14.5, 11.5, 9.5]], (72, 10.4)),
        choose('Trace the letter and circle the correct picture.', 'Which picture begins with b? Tap it to circle it.', (80, 10.4), (9, 12.5, 82, 39),
               pictures([(23.1, 30.6, False, 'fish'), (22.5, 43.4, True, 'ball'), (50.6, 31.6, True, 'bear'), (51.2, 44.9, False, 'ant'),
                         (77.5, 31.1, False, 'almond'), (78.1, 41.9, True, 'banana')], 13, 11)),
        circle_sound((17, 56.5, 64, 22), [(27.8, 75.1, False, 'a'), (36, 75.1, True, 'b'), (62.9, 75.1, True, 'b'), (70.3, 75.1, False, 'a')], (67, 54)),
    ],
    22: [
        tick((8, 12, 84, 42), [(21.5, 37.7, False, 'b'), (21.5, 50.3, True, 'c'), (48.8, 37.7, False, 'a'), (48.8, 50.3, True, 'c'),
                               (76.5, 37.7, True, 'c'), (77.1, 50.3, False, 'b')], (75, 10.4)),
        write_first('Write the beginning sound for each picture.', (8, 58, 84, 21.5),
                    [[12, 70, 17, 8.5], [42.5, 70, 17, 8.5], [71.5, 70, 17, 8.5]], (63, 57.5)),
    ],
    26: [
        match_letter('d', (8, 12, 85, 70), [('dog', (42.8, 42), (26.3, 38.9)), ('duck', (42.8, 51), (26.3, 64.1)), ('deer', (58.6, 42), (77, 38.9))], (82, 10.4)),
    ],
    27: [
        colour('Colour the pictures.', 'Colour the apple, the ball and the cap.', (80, 10.4), (9, 12.5, 82, 24), [
            ('apple', (16.3, 15.3, 13.7, 11.8), [C['red'], C['green'], C['brown']]),
            ('ball', (43, 15.8, 14.3, 10.6), [C['red'], C['blue'], C['yellow']]),
            ('cap', (69.4, 16.3, 16.9, 9.1), [C['blue'], C['yellow'], C['red']])]),
        write_first('Write the beginning letter for each picture.', (9, 13, 82, 24), [[17.5, 29.4, 11.5, 5.8], [44.3, 29.4, 11.5, 5.8], [71, 29.4, 11.5, 5.8]], (88, 10.4)),
        circle_sound((11, 41.5, 78, 20), [(18.1, 58.2, False, 'b'), (22, 58.2, True, 'c'), (38.1, 58.2, True, 'a'), (43.3, 58.2, False, 'b'),
                                          (58.3, 58.2, False, 'c'), (63.3, 58.2, True, 'd'), (77.6, 58.2, True, 'b'), (82.8, 58.2, False, 'a')], (84, 39.5),
                     'Look at the pictures and circle the correct beginning sound.'),
        choose('Say the sound and circle the correct picture.', 'Say each sound. Tap the picture that begins with it.', (66, 62.5), (9, 65.5, 83, 29.5),
               pictures([(23.8, 73, False, 'banana'), (40, 73, True, 'ant'), (65.3, 72.8, True, 'ball'), (84.6, 73.2, False, 'cap'),
                         (22.5, 87.6, True, 'cat'), (39.8, 88.3, False, 'apple'), (66.9, 87.3, True, 'deer'), (82.5, 87.3, False, 'alligator')], 12, 10)),
    ],
    28: [
        colour('Colour the beginning sound.', 'Colour each big letter.', (88, 10.4), (14, 13, 20, 57), [
            ('a', (19.1, 15.3, 8.4, 6.4), MANY, True), ('b', (20, 29.4, 7.5, 8.6), MANY, True),
            ('c', (20, 45.9, 7.5, 6.4), MANY, True), ('d', (20, 60.4, 7.5, 8.1), MANY, True)]),
        choose('Circle the correct picture.', 'Say each letter. Tap the picture that begins with it.', (88, 10.4), (37, 13, 55, 58),
               pictures([(48.1, 18.7, False, 'tomato'), (74.4, 18.7, True, 'alligator'), (48.5, 33.5, False, 'pear'), (75, 33, True, 'banana'),
                         (49.4, 48.8, True, 'cap'), (75, 48.8, False, 'leaf'), (48.8, 65.6, False, 'hen'), (76.3, 65.6, True, 'dog')], 14, 12)),
    ],
    34: [
        circle_letter('e', (7, 12, 86, 23.5), [
            (12.5, 19.7, 'r'), (21.5, 20.4, 'b'), (30.3, 16.8, 'e'), (50, 17.6, 'e'), (40.3, 22.5, 'm'), (52.5, 24.5, 'm'),
            (65.3, 21.5, 'b'), (75.6, 20.2, 'r'), (84, 16.3, 'e'), (85.8, 22.5, 's'), (15.5, 29.4, 'e'), (27.8, 27.1, 'd'),
            (41.3, 29.4, 'e'), (59.4, 30.6, 's'), (71.5, 29.4, 'g'), (85.4, 30.6, 'e')], (40, 10)),
        trace_letters('e', (9, 40, 81, 38.5), [[15.5, 41, 11.5, 9], [42.5, 41, 11.5, 9], [70, 41, 11.5, 9]], (64, 37.4)),
        choose('Trace the letter and circle the correct picture.', 'Which picture begins with e? Tap it to circle it.', (71, 37.4), (9, 40, 81, 38.5),
               pictures([(20.4, 57, True, 'egg'), (19.6, 69, False, 'mango'), (48.8, 57, False, 'cap'), (49, 70.2, True, 'envelope'),
                         (75.6, 57.7, True, 'elephant'), (77.5, 71.2, False, 'quail')], 14, 11)),
    ],
    38: [
        trace_first('Trace the letter that makes the beginning sound.', (10, 12, 82, 41), [[41.5, 14, 17, 9], [41.5, 27, 17, 9], [41.5, 41, 17, 9]], (76, 10.3)),
        circle_sound((12, 58, 78, 24), [(19.4, 77.4, False, 'e'), (26.5, 77.4, True, 'f'), (47, 77.4, True, 'f'), (53.3, 77.4, False, 'e'),
                                        (74.4, 77.4, True, 'f'), (80.6, 77.4, False, 'g')], (72, 56.3)),
    ],
    42: [
        write('Circle the letter that makes the beginning sound.', 'Say the name of each picture. Write the letter it begins with on its lines.', (70, 10), (8, 12, 85, 29),
              [[15.3, 30.1, 13.2, 6.2], [44, 33.5, 13.1, 5.9], [73.3, 30.1, 13, 6.2]]),
        tick((9, 46, 83, 34), [(21.6, 67.9, False, 'f'), (21.6, 76.7, True, 'g'), (48.8, 67.9, True, 'g'), (48.8, 76.7, False, 'e'),
                               (77.1, 67.9, True, 'g'), (77.1, 76.7, False, 'f')], (76, 43.4)),
    ],
    46: [
        match_letter('h', (8, 12, 85, 70), [('hat', (43, 42), (24.8, 36.7)), ('house', (59, 42), (78.1, 36.7)), ('hen', (59, 52), (78.1, 59.4))], (82, 10.4)),
    ],
    47: [
        choose('Tick the correct beginning letter.', 'Say the name of each picture. Tap the box under the letter it begins with.', (60, 10.4), (10, 13, 80, 61),
               letters([(43.8, 25.4, True, 'e'), (61, 25.4, False, 'f'), (77.9, 25.4, False, 'g'),
                        (44, 40.6, False, 'h'), (61, 40.6, False, 'g'), (77.9, 40.6, True, 'f'),
                        (44, 56, False, 'e'), (61, 56, True, 'g'), (77.9, 56, False, 'h'),
                        (44, 71.2, False, 'f'), (61, 71.2, False, 'e'), (77.9, 71.2, True, 'h')], 6, 5.5)),
        colour('Colour the pictures that begin with the letter "f".', 'Which pictures begin with f? Colour them.', (74, 77), (10, 78, 80, 16), [
            ('fish', (31.9, 82.3, 19.6, 8.4), [C['orange'], C['blue'], C['yellow']]),
            ('fan', (76.3, 79.4, 12.1, 13.3), [C['blue'], C['grey']])]),
    ],
    48: [
        match('Match the letters with the pictures.', 'Draw a line from each letter to the picture that begins with it.', (58, 9.8), (8, 11, 85, 34),
              [('hen', 20.4, 20.5), ('egg', 40.3, 20.5), ('frog', 60.1, 20.5), ('grapes', 80, 20.5),
               ('egg', 20, 31.5), ('grapes', 40.6, 31.5), ('hen', 60, 31.5), ('frog', 80.6, 31.5)]),
        write_first('Look at the pictures and write the initial letter for each.', (8, 48, 85, 24),
                    [[20.3, 51.3, 13.5, 6.1], [49, 51.3, 12.3, 6.1], [76.9, 51.3, 12.1, 6.1],
                     [20.6, 63.9, 13.8, 5.9], [48.1, 63.9, 13.5, 5.9], [76.9, 63.9, 12.1, 5.9]], (88, 45.8)),
    ],
    52: [
        write('Write the letter that makes the beginning sound.', 'Say each word. Write the missing first letter on the lines.', (78, 10.3), (8, 13, 84, 38),
              [[37, 15, 9, 8.4], [33, 28.2, 6.5, 8], [41, 41.6, 9, 8.2]]),
        choose('Cross out the objects that do not begin with the letter "i".', 'Which things do not begin with i? Tap each one to cross it out.', (84.5, 54.5), (8, 60, 84, 22),
               pictures([(16.9, 66.6, False, 'insect'), (35.6, 73, True, 'cat'), (47.8, 66.4, False, 'ink'), (62.5, 74, True, 'hen'), (80.4, 66, False, 'igloo')], 12, 12)),
    ],
    56: [
        tick((9, 12, 82, 42), [(21.6, 37.3, False, 'i'), (21.6, 49.8, True, 'j'), (48.9, 37.3, True, 'j'), (48.9, 49.8, False, 'h'),
                               (76.6, 37.3, False, 'h'), (76.6, 49.8, True, 'j')], (77, 10)),
        trace_first('Trace the beginning sound for each picture.', (9, 59, 82, 21), [[12.3, 70, 16.5, 8], [42.8, 70, 16.2, 8], [71.9, 70, 16.2, 8]], (64, 57.2)),
    ],
    60: [
        circle_letter('k', (9, 13.3, 84, 26.7), [
            (13.8, 20.7, 'a'), (22.8, 21, 'k'), (31.3, 16.8, 'l'), (51.3, 17.9, 'k'), (71, 16, 'a'), (85.3, 17.1, 'e'),
            (41.3, 23.3, 'm'), (53.8, 25.4, 'm'), (66.6, 22.4, 'b'), (77.5, 21.2, 'r'), (86.9, 23.5, 's'), (16.6, 30.4, 'e'),
            (28.8, 28.3, 'd'), (42.3, 30.3, 'e'), (60.4, 31.6, 's'), (72.8, 28.9, 'k'), (81.3, 26.9, 'a'), (86.6, 31.6, 'e'),
            (26.6, 36.1, 'm'), (39.4, 35.7, 'k'), (51.9, 36.3, 'b'), (66.5, 36.2, 'r'), (81.5, 36.8, 'b')], (37, 10)),
        tick((9, 46, 82, 34), [(21.6, 67.9, True, 'k'), (21.6, 76.9, False, 'j'), (48.8, 67.9, False, 'j'), (48.8, 76.9, True, 'k'),
                               (77.1, 67.9, True, 'k'), (77.1, 76.9, False, 'i')], (77, 44.4)),
    ],
    64: [
        trace_letters('l', (9, 12.5, 82, 39), [[16.3, 13.3, 13.7, 9.4], [43.5, 13.3, 13.7, 9.4], [70.9, 13.3, 13.7, 9.4]], (67, 10.3)),
        choose('Trace the letter and circle the correct picture.', 'Which picture begins with l? Tap it to circle it.', (74, 10.3), (9, 12.5, 82, 39),
               pictures([(23.1, 30.6, True, 'lemon'), (22.3, 43.4, False, 'orange'), (50, 29.6, False, 'kitten'), (49.8, 42.4, True, 'lamb'),
                         (78.1, 30.6, True, 'leaf'), (78.1, 43.4, False, 'fish')], 13, 11)),
        circle_sound((17, 56.5, 64, 22), [(28.4, 75, False, 'k'), (36.6, 75, True, 'l'), (62.3, 75, True, 'l'), (70.4, 75, False, 'k')], (74, 54.1)),
    ],
    65: [
        choose('Look at each picture and circle the correct beginning sound.', 'Say the name of each picture. Tap the letter it begins with.', (88, 10.7), (12, 13, 78, 20),
               letters([(18.4, 29.4, False, 'i'), (22, 29.4, True, 'j'), (39.5, 29.4, True, 'k'), (43.6, 29.4, False, 'j'),
                        (59.3, 29.4, False, 'k'), (63.6, 29.4, True, 'l'), (79.8, 29.4, True, 'i'), (83.4, 29.4, False, 'j')], 3.4, 5.5)),
        write_first('Look at the pictures and write the beginning letter for each picture.', (12, 39, 80, 23.5),
                    [[19.4, 55.5, 11.5, 5.8], [46.3, 55.5, 11.5, 5.8], [73.1, 55.5, 11.5, 5.8]], (84.5, 33.3)),
        match('Match each letter to the same letter.', 'Draw a line from each letter to the same letter below.', (61, 65.9), (10, 67, 82, 30),
              [('i', 18.5, 76.5), ('j', 39.9, 76.5), ('k', 61.1, 76.5), ('l', 82.5, 76.5),
               ('l', 18.5, 85.5), ('k', 39.8, 85.5), ('j', 61.1, 85.5), ('i', 82.5, 85.5)]),
    ],
    66: [
        choose('Look at the pictures and circle the correct beginning letter.', 'Say the name of each picture. Tap the letter it begins with.', (87, 11.2), (14, 13.5, 72, 35),
               letters([(43.3, 17.3, False, 'l'), (43.3, 21.5, True, 'j'), (43.3, 26.7, False, 'k'),
                        (80.8, 17.3, True, 'k'), (80.8, 22.1, False, 'l'), (80.8, 26.4, False, 'j'),
                        (41.9, 34.2, False, 'i'), (41.9, 38.8, False, 'j'), (41.9, 43.6, True, 'l'),
                        (80, 34.5, False, 'l'), (80, 39.3, True, 'i'), (80, 44, False, 'k')], 5, 4.4)),
        write('Write "i".', 'Write the letter i on the lines to make the word igloo.', (26, 54.6), (10, 56, 28, 12), [[14.6, 60.2, 5.5, 5.7]]),
        colour('Trace and colour the igloo.', 'Trace the dotted igloo, then colour it.', (33, 54.6), (38, 48, 50, 26), [
            ('igloo', (41.6, 49.8, 44.3, 22.2), [C['blue'], C['grey'], C['purple']])]),
    ],
    72: [
        match_letter('m', (8, 12, 85, 70), [('mango', (43, 41), (26.3, 38.2)), ('monkey', (59, 41), (77.1, 38.2)), ('map', (50.9, 53), (50.9, 68.2))], (82, 9.7)),
    ],
    76: [
        circle_letter('n', (8.1, 12.1, 83.8, 21.7), [
            (12.9, 19.5, 'r'), (21.6, 19.7, 'b'), (30.4, 16.5, 'n'), (40.4, 22.2, 'm'), (50.3, 17.5, 'n'), (52.8, 24.2, 'm'),
            (65.6, 21.2, 'b'), (76.5, 20, 'r'), (84.1, 16, 'n'), (85.9, 22.2, 's'), (15.6, 29.2, 'n'), (27.8, 26.9, 'd'),
            (41.3, 29.2, 'n'), (59.4, 30.1, 's'), (71.6, 29.1, 'g'), (85.6, 30.1, 'n')], (40, 9.8)),
        trace_first('Trace the letter that makes the beginning sound.', (8, 39, 84, 41), [[37.5, 41.7, 20.9, 8.3], [44.6, 54.7, 21, 8.2], [41, 69.3, 48.6, 8.2]], (78, 36.9)),
    ],
    80: [
        choose('Cross out the objects that begin with the letter "o".', 'Which things begin with o? Tap each one to cross it out.', (82, 11), (9, 13.5, 82, 22),
               pictures([(16, 20.2, True, 'orange'), (30, 28.1, False, 'kitten'), (50, 23.7, True, 'ostrich'), (65, 30.6, False, 'lemon'), (79.8, 20.2, True, 'octopus')], 12, 12)),
        trace_letters('o', (10, 40, 81, 39), [[16.5, 40.9, 13.5, 9.4], [43.8, 40.9, 13.5, 9.4], [71, 40.9, 13.5, 9.4]], (67, 38.5)),
        choose('Trace the letter and circle the correct picture.', 'Which picture begins with o? Tap it to circle it.', (74, 38.5), (10, 40, 81, 39),
               pictures([(23.1, 57.2, True, 'octopus'), (21.5, 70, False, 'kitten'), (51, 57, False, 'guava'), (50, 70.2, True, 'orange'),
                         (77.8, 57.7, True, 'ostrich'), (77.1, 71.5, False, 'hen')], 13, 11)),
    ],
    84: [
        circle_sound((17, 13.5, 64, 22), [(27.1, 31.6, False, 'o'), (37, 31.6, True, 'p'), (62, 31.6, False, 'm'), (72, 31.6, True, 'p')], (74, 9.6)),
        tick((9, 40, 82, 41), [(21.6, 64.9, False, 'o'), (21.6, 77.5, True, 'p'), (48.9, 64.9, True, 'p'), (48.9, 77.5, False, 'm'),
                               (76.6, 64.9, False, 'n'), (76.6, 77.5, True, 'p')], (77, 38)),
    ],
    85: [
        match('Match the letters with the pictures.', 'Draw a line from each letter to the picture that begins with it.', (58, 10.5), (8, 11.5, 84, 33),
              [('nest', 20.4, 21.5), ('mango', 40.9, 21.5), ('ostrich', 60.4, 21.5), ('parrot', 80.1, 21.5),
               ('mango', 21, 33.5), ('ostrich', 43, 26), ('nest', 61.6, 33.5), ('parrot', 81, 32.5)]),
        choose('Say the sound and circle the correct picture.', 'Say each sound. Tap the picture that begins with it.', (69, 48), (9, 50, 85, 45),
               pictures([(20.3, 63.8, True, 'map'), (39, 62.1, False, 'cat'), (65.9, 64.1, True, 'nuts'), (83.5, 59, False, 'egg'),
                         (22.3, 85.8, False, 'apple'), (39.5, 79.4, True, 'octopus'), (62.9, 86.8, True, 'pear'), (81.3, 83.3, False, 'grapes')], 13, 12)),
    ],
    86: [
        colour('Colour the beginning sound.', 'Colour each big letter.', (76, 9.4), (14, 11, 78, 59), [
            ('m', (17.1, 11.6, 17.9, 11.2), MANY, True), ('n', (17.1, 26.9, 17.9, 11.3), MANY, True),
            ('o', (17.1, 42.4, 17.9, 11.3), MANY, True), ('p', (17.1, 57.7, 17.9, 11.3), MANY, True)]),
        choose('Circle the picture.', 'Say each letter. Tap the picture in its row that begins with it.', (83, 9.4), (14, 11, 78, 59),
               pictures([(51.9, 17.6, True, 'monkey'), (73.1, 17.8, False, 'parrot'), (51.5, 33.3, False, 'ball'), (73.1, 32.5, True, 'newspaper'),
                         (51.5, 48, False, 'mango'), (75.6, 48.1, True, 'orange'), (52.1, 64.3, True, 'peacock'), (75.6, 65.1, False, 'key')], 13, 12)),
    ],
    90: [
        # the quilt's printed letters are p and m (no q), so that column is left out
        tick((9, 12.5, 55, 34), [(21.9, 34.3, False, 'p'), (21.9, 43.4, True, 'q'), (49.1, 34.3, True, 'q'), (49.1, 43.4, False, 'p')], (77, 9.9)),
        write_first('Write the beginning sound of each picture.', (9, 52, 82, 25), [[15.9, 69, 11.5, 6], [44.6, 69, 11.5, 6], [73.4, 69, 11.5, 6]], (64, 50)),
    ],
    94: [
        circle_letter('r', (9.4, 12.1, 83.8, 21.7), [
            (14.1, 19.7, 'r'), (22.9, 20, 'b'), (31.6, 16.6, 'r'), (41.6, 22.2, 'm'), (51.6, 17.5, 'r'), (53.9, 24.4, 'm'),
            (66.9, 21.2, 'b'), (77.5, 20.2, 'e'), (85.6, 16, 'r'), (87.1, 22.4, 's'), (16.9, 29.2, 'n'), (29, 26.9, 'd'),
            (42.8, 29.2, 'r'), (60.6, 30.4, 's'), (72.9, 29.1, 'g'), (86.9, 30.4, 'r')], (40, 9.8)),
        trace_first('Trace the letter that makes the beginning sound.', (8, 39, 84, 41), [[35.4, 41.4, 20.9, 8.2], [34.8, 54.5, 32.4, 8.1], [35.4, 69, 32.5, 8.2]], (78, 36.7)),
    ],
    98: [
        match_letter('s', (8, 12, 85, 70), [('sunflower', (43, 41.5), (26.5, 38.3)), ('sun', (58.5, 50), (77.3, 63.6)), ('snake', (51, 52.5), (51, 69.5))], (82, 9.9)),
    ],
    102: [
        trace_letters('t', (9, 11.5, 82, 39), [[16.3, 12.1, 13.7, 9.6], [43.5, 12.1, 13.7, 9.6], [70.9, 12.1, 13.7, 9.6]], (67, 9.6)),
        choose('Trace the letter and circle the correct picture.', 'Which picture begins with t? Tap it to circle it.', (74, 9.6), (9, 11.5, 82, 39),
               pictures([(22.3, 29.1, False, 'parrot'), (23.1, 41.9, True, 'turtle'), (50, 29.1, True, 'tomato'), (50, 41.9, False, 'pear'),
                         (77.5, 28.6, False, 'bull'), (77.3, 41.9, True, 'tiger')], 13, 11)),
        choose('Circle the things that begin with the letter "t".', 'Which things begin with t? Tap each one to circle it.', (75, 54.1), (9, 56.5, 82, 24),
               pictures([(18.1, 73, True, 'turtle'), (35.6, 63.1, False, 'mango'), (51.3, 73.5, True, 'tomato'), (65.3, 63.1, False, 'onion'), (80.6, 71.5, True, 'tiger')], 13, 11)),
    ],
    103: [
        choose('Look at the pictures and circle the correct sound.', 'Say the name of each picture. Tap the letter it begins with.', (75, 10.7), (12, 13, 78, 20),
               letters([(18.1, 29.4, True, 'q'), (22.9, 29.4, False, 'r'), (38.9, 29.4, False, 's'), (43.3, 29.4, True, 't'),
                        (59.1, 29.4, True, 'r'), (63.5, 29.4, False, 's'), (79.5, 29.4, False, 'q'), (84.4, 29.4, True, 's')], 3.8, 5.5)),
        write_first('Look at the pictures and write the initial letter for each.', (12, 39, 80, 23.5),
                    [[19.4, 55.5, 11.5, 5.8], [46.3, 55.5, 11.5, 5.8], [73.1, 55.5, 11.5, 5.8]], (83, 35.7)),
        colour('Colour the pictures that begin with the letter "s".', 'Which pictures begin with s? Colour them.', (75, 66.2), (8, 69, 85, 26), [
            ('snake', (8.5, 73.5, 21.9, 17.8), [C['green'], C['yellow'], C['brown']]),
            ('sun', (70.4, 77.4, 22.8, 15.8), [C['yellow'], C['orange']])]),
    ],
    104: [
        choose('Tick the correct beginning letter.', 'Say the name of each picture. Tap the box under the letter it begins with.', (59, 6.8), (10, 9.5, 85, 60),
               letters([(44.1, 21.7, True, 'q'), (61.3, 21.7, False, 'r'), (78, 21.7, False, 's'),
                        (44.1, 37, False, 's'), (61.3, 37, True, 'r'), (78, 37, False, 't'),
                        (44.1, 52.3, False, 'q'), (61.3, 52.3, True, 's'), (78, 52.3, False, 'r'),
                        (44.1, 67.6, False, 's'), (61.3, 67.6, True, 't'), (78, 67.6, False, 'r')], 6, 5.5)),
    ],
    110: [
        choose('Cross out the things that begin with the letter "u".', 'Which things begin with u? Tap each one to cross it out.', (80, 10.8), (9, 12.5, 83, 23),
               pictures([(18.5, 19.2, True, 'umbrella'), (33.1, 29.1, False, 'ring'), (51.5, 22.2, True, 'uncle'), (68.8, 30.1, False, 'orange'), (83.1, 20.7, True, 'urn')], 12, 12)),
        trace_letters('u', (10, 40, 81, 39), [[16.5, 40.9, 13.5, 9.4], [43.8, 40.9, 13.5, 9.4], [71, 40.9, 13.5, 9.4]], (67, 38.5)),
        choose('Trace the letter and circle the correct picture.', 'Which picture begins with u? Tap it to circle it.', (74, 38.5), (10, 40, 81, 39),
               pictures([(22.5, 57.7, False, 'feather'), (23.1, 69, True, 'umbrella'), (50.6, 58.2, True, 'urn'), (50.6, 72, False, 'egg'),
                         (78.1, 54.7, False, 'envelope'), (78.4, 69, True, 'uncle')], 13, 11)),
    ],
    114: [
        tick((9, 12.5, 82, 34), [(21.6, 34.3, False, 'u'), (21.6, 43.4, True, 'v'), (48.9, 34.3, True, 'v'), (48.9, 43.4, False, 'u'),
                                 (77.1, 34.3, False, 't'), (77.1, 43.4, True, 'v')], (77, 10)),
        write_first('Write the beginning sound for each picture.', (9, 52, 82, 24), [[11.9, 68.5, 17.5, 5.9], [41.3, 68.5, 17.5, 5.9], [70.3, 68.5, 17.5, 5.9]], (64, 49.4)),
    ],
    118: [
        match_letter('w', (8, 12, 85, 70), [('watch', (43, 51), (26.3, 63.6)), ('well', (59, 51), (77.1, 63.6))], (82, 9.9)),
    ],
    122: [
        circle_letter('x', (8.1, 12.1, 83.8, 21.7), [
            (12.9, 19.5, 'r'), (21.6, 19.7, 'b'), (30.4, 16.5, 'x'), (40.4, 22.2, 'm'), (50.3, 17.5, 'x'), (52.8, 24.2, 'm'),
            (65.6, 21.2, 'b'), (76.3, 20.2, 'e'), (84.1, 16, 'x'), (85.9, 22.2, 's'), (15.6, 29.2, 'x'), (27.8, 26.9, 'd'),
            (41.3, 29.2, 'x'), (59.4, 30.1, 's'), (71.6, 29.1, 'g'), (85.6, 30.1, 'x')], (40, 9.8)),
        trace_first('Trace the letter "x" in each word.', (8, 39, 84, 41), [[35.4, 41.4, 28.1, 8.4], [22.5, 54.5, 48.5, 8.2], [39.6, 69.2, 48.1, 8.2]], (58, 36.7)),
    ],
    123: [
        match('Match the letters with the pictures.', 'Draw a line from each letter to the picture that begins with it.', (58, 10.5), (8, 11.5, 84, 33),
              [('umbrella', 20.4, 21.5), ('wood', 40.9, 21.5), ('vest', 60.4, 21.5), ('x-ray', 80.1, 21.5),
               ('x-ray', 21, 32.5), ('wood', 42.3, 33.5), ('umbrella', 63.1, 32.5), ('vest', 81.9, 32.5)]),
        choose('Say the sound and circle the correct picture.', 'Say each sound. Tap the picture that begins with it.', (69, 48), (9, 50, 85, 45),
               pictures([(23.1, 62.6, False, 'racket'), (40.6, 61.1, True, 'uncle'), (60, 65.1, False, 'ring'), (79.8, 59.2, True, 'van'),
                         (17.5, 86.8, False, 'kettle'), (36.9, 82.8, True, 'wood'), (63.8, 85.8, True, 'xylophone'), (85.4, 79.9, False, 'vest')], 13, 12)),
    ],
    124: [
        match('Match each letter to the same letter.', 'Draw a line from each letter to the same letter below.', (61, 6.7), (10, 8.5, 82, 32),
              [('u', 18.5, 17.3), ('v', 39.9, 17.3), ('w', 61.3, 17.3), ('x', 82.5, 17.3),
               ('x', 18.5, 32), ('u', 39.9, 32), ('v', 61.3, 32), ('w', 82.5, 32)]),
        choose('Look at the pictures and circle the correct sound.', 'Say the name of each picture. Tap the letter it begins with.', (75, 44.2), (12, 47, 78, 23.5),
               letters([(17.9, 67.9, True, 'u'), (22.9, 67.9, False, 'v'), (38.3, 67.9, True, 'v'), (43.5, 67.9, False, 'w'),
                        (59, 67.9, True, 'w'), (64.3, 67.9, False, 'x'), (79.4, 67.9, False, 'u'), (84.3, 67.9, True, 'x')], 4, 5.5)),
    ],
    128: [
        tick((9, 11.5, 82, 42), [(21.9, 36.7, False, 'x'), (21.9, 49.3, True, 'y'), (49, 36.7, True, 'y'), (49, 49.3, False, 'x'),
                                 (76.9, 36.7, False, 'w'), (76.9, 49.3, True, 'y')], (77, 9.7)),
        write_first('Write the correct beginning sound for each picture.', (16, 57, 65, 23), [[23.4, 73, 17.5, 5.9], [57.9, 73, 17.5, 5.9]], (74, 55.2)),
    ],
    132: [
        choose('Cross out the objects that do not begin with "z".', 'Which things do not begin with z? Tap each one to cross it out.', (78, 10.6), (9, 12.5, 84, 24),
               pictures([(18.8, 22.2, False, 'zebra'), (35, 29.1, True, 'ring'), (51.3, 22.2, False, 'zip'), (65.3, 30.1, True, 'octopus'), (83.5, 19.2, False, 'zoo')], 13, 13)),
        trace_letters('z', (10, 40, 81, 39), [[16.3, 40.9, 13.7, 9.4], [43.5, 40.9, 13.7, 9.4], [70.9, 40.9, 13.7, 9.4]], (67, 38.5)),
        choose('Trace the letter and circle the correct picture.', 'Which picture begins with z? Tap it to circle it.', (74, 38.5), (10, 40, 81, 39),
               pictures([(20.3, 56.2, False, 'octopus'), (23.1, 69, True, 'zebra'), (50.3, 58.7, True, 'zip'), (50, 72, False, 'map'),
                         (78.1, 56.7, False, 'parrot'), (77.3, 70, True, 'zoo')], 13, 11)),
    ],
}


PILL_W, PILL_H, GAP = 14.5, 3.5, 0.8   # a question button (styles.css .question-btn) as % of the page


def place_buttons(qs):
    """The button's point is where it goes on the instruction's line (its middle). The pill is drawn from its top-left
    corner, so: lift it by half its height, put a second button on the same line just after the first, keep both on the page."""
    lines = []   # buttons sharing a line: [[q, ...], ...]
    for q in qs:
        y = q['button']['y']
        line = next((l for l in lines if abs(l[0]['button']['y'] - y) < PILL_H), None)
        if line is None:
            lines.append([q])
        else:
            line.append(q)
    for line in lines:
        y = line[0]['button']['y'] - PILL_H / 2
        x = line[0]['button']['x']
        title_end = x - 2.5   # the point is set just after the instruction's last word
        width = len(line) * PILL_W + (len(line) - 1) * GAP
        x = min(x, 99 - width)
        if x < title_end - 1 and y < 12:
            # a long instruction at the top: the buttons go up into the coloured header, left of the Activities badge
            y, x = 3.6, min(x, 73 - width)
        for i, q in enumerate(line):
            q['button'] = {'x': round(x + i * (PILL_W + GAP), 2), 'y': round(y, 2)}
            if x < title_end - 1 and y > 3.6:
                print(f'  note: button "{q["title"][:40]}" covers the end of its instruction')


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    for qs in Q_PAGES.values():
        place_buttons(qs)
    data = {str(page): qs for page, qs in sorted(Q_PAGES.items())}
    with open(root / 'books/questions-maxford.js', 'w', encoding='utf-8', newline='\n') as f:
        f.write('// Generated by tools/make_maxford_questions.py: the printed exercises of Maxford Global Qaida 3+ English.\n')
        f.write('window.BOOK_QUESTIONS = window.BOOK_QUESTIONS || {};\n')
        f.write("window.BOOK_QUESTIONS['%s'] = " % BOOK + json.dumps(data, indent=1, ensure_ascii=False) + ';\n')
    print(len(data), 'pages,', sum(len(q) for q in data.values()), 'questions')
