// The writing grids on the printed Number practice pages.
const practicePages = [6, 8, 10, 12, 14, 20, 22, 24, 26, 30, 46, 48, 50, 52, 54, 60, 62, 64, 66, 68];
const grid = { x: 9, y: 12.2, w: 84.5, h: 34.4 };
const writeNumber = (number, crop, lines, button) => ({
  type: 'question',
  kind: 'write',
  title: `Trace and write the number ${number}.`,
  say: `Trace the dotted ${number}, then write it in the blank boxes.`,
  button,
  crop,
  lines,
  hint: { x: lines[0].x + 2, y: lines[0].y + 2 }
});

const gridCells = Array.from({ length: 4 }, (_, row) =>
  Array.from({ length: 6 }, (_, column) => ({
    x: 9.7 + column * 13.9,
    y: 12.4 + row * 8.5,
    w: 13.3,
    h: 8.2
  })).slice(row === 0 ? 2 : 0)
).flat();

const questions = Object.fromEntries(practicePages.map((page, index) => [
  page,
  [writeNumber(index + 1, grid, gridCells, { x: 49, y: 9.2 })]
]));

questions[27] = [
  writeNumber(0, { x: 11, y: 44.5, w: 76, h: 29 }, [
    ...[11.3, 31.1, 50.9].map(x => ({ x, y: 45, w: 19.5, h: 12.5 })),
    ...[36.9, 49.2, 61.5, 73.8].map(x => ({ x, y: 59.4, w: 12.2, h: 6.7 })),
    ...[12.3, 24.6, 36.9, 49.2, 61.5, 73.8].map(x => ({ x, y: 66.3, w: 12.2, h: 6.7 }))
  ], { x: 71, y: 44 }),
  {
    type: 'question',
    kind: 'choose',
    title: 'Tick the basket with 0 bananas.',
    say: 'Find the basket with no bananas and tap it.',
    button: { x: 58, y: 76 },
    crop: { x: 10, y: 77, w: 79, h: 14.5 },
    options: [
      { x: 11, y: 78, w: 24, h: 13, correct: false, label: 'Basket with two bananas' },
      { x: 37, y: 78, w: 24, h: 13, correct: true, label: 'Empty basket' },
      { x: 63, y: 78, w: 24, h: 13, correct: false, label: 'Basket with one banana' }
    ]
  }
];

window.BOOK_QUESTIONS = window.BOOK_QUESTIONS || {};
window.BOOK_QUESTIONS['maxford-global-qaida-4-maths'] = questions;
