const box = (x, y, w, h) => ({ x, y, w, h });
const writing = (title, say, button, crop, lines) => ({
  type: 'question',
  kind: 'write',
  title,
  say,
  button,
  crop,
  lines
});

// Measurements from the printed number-word worksheets, in page percentages.
const wordPages = [
  [7, 14.41, 45.35, 70.23, 22.44],
  [12, 14.23, 45.35, 70.23, 22.44],
  [21, 14.41, 44.68, 69.22, 23.46],
  [25, 14.23, 44.68, 69.22, 23.46],
  [29, 14.41, 44.68, 69.22, 23.46],
  [45, 14.41, 44.68, 69.22, 23.46],
  [49, 14.41, 44.68, 69.22, 23.46],
  [53, 14.41, 44.68, 69.22, 23.46],
  [57, 14.59, 44.68, 69.22, 23.46],
  [61, 14.41, 44.64, 69.18, 23.46]
];
const questions = Object.fromEntries(wordPages.map(([page, top, left, right, width], index) => [
  page,
  [writing(
    `Write the numbers ${index * 10}–${index * 10 + 9} in words.`,
    'Read the number word and copy it into the two blank boxes.',
    { x: 55, y: 10.8 },
    box(7, 13.6, 87, 76),
    Array.from({ length: 10 }, (_, row) =>
      [left, right].map(x => box(x, top + row * 7.7, width, 5.43))
    ).flat()
  )]
]));

questions[74] = [writing(
  'Addition with objects',
  'Count the objects in each group, then add the groups together. Write the total.',
  { x: 57, y: 8.2 },
  box(8, 14, 85, 74.8),
  [
    box(42.8, 16.2, 5, 4.5), box(70.7, 16.2, 5, 4.5), box(82.7, 14.8, 9.3, 7.2), box(39.8, 24.6, 8, 2.5),
    box(35, 31.7, 5, 4.5), box(72.2, 31.7, 5, 4.5), box(82.7, 30.4, 9.3, 7.2), box(42.5, 40.1, 8, 2.5),
    box(42.4, 47.3, 5, 4.5), box(71.7, 47.3, 5, 4.5), box(82.7, 46, 9.3, 7.2), box(47.6, 55.6, 8, 2.5),
    box(42.4, 62.3, 5, 4.5), box(82.7, 60.5, 9.3, 7.2), box(43, 70.6, 8, 2.5),
    box(43.5, 79.2, 5, 4.5), box(70.5, 79.2, 5, 4.5), box(82.7, 76, 9.3, 7.2), box(42.1, 86, 8, 2.5)
  ]
)];
questions[84] = [writing(
  'Subtraction with objects',
  'Count what is left in the first two pictures. In the other boxes, cross out the objects to subtract, then write each answer.',
  { x: 54, y: 8.2 },
  box(0, 14.3, 100, 74.5),
  [
    box(26.5, 36.2, 6, 3.4), box(77, 36.2, 6, 3.4),
    ...[45.4, 67.9].flatMap(y => [14, 41, 68].map(x => box(x, y, 21.4, 20.8)))
  ]
)];

window.BOOK_QUESTIONS = window.BOOK_QUESTIONS || {};
window.BOOK_QUESTIONS['maxford-global-qaida-5-maths'] = questions;
