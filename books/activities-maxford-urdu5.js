// The first three rows of pictures on each beginning-letter worksheet, right to left.
const pictureRows = {
  10: [
    ['بس', 'پتّا', 'تتلی'],
    ['ٹوکری', 'پھل', 'جال'],
    ['چڑیا', 'حلوہ', 'خیمہ']
  ],
  11: [
    ['صندوق', 'ضعیف آدمی', 'طوطا'],
    ['مسخرہ', 'عینک', 'غلیل'],
    ['فٹ بال', 'قینچی', 'کتاب']
  ]
};
const rowEdges = { 10: [26.5, 37, 47.5, 57.5], 11: [26.5, 38.5, 49.5, 58] };

window.BOOK_ACTIVITIES = window.BOOK_ACTIVITIES || {};
window.BOOK_ACTIVITIES['maxford-global-qaida-5-urdu'] = Object.fromEntries(
  Object.entries(pictureRows).map(([page, rows]) => {
    const edges = rowEdges[page];
    return [page, [{
      type: 'game',
      title: 'تصویر پہچانیں',
      button: { x: 42, y: 7.8 },
      crop: { x: 16, y: edges[0], w: 78, h: edges.at(-1) - edges[0] },
      targets: rows.flatMap((names, row) => names.map((name, column) => ({
        name,
        x: [79, 48, 17][column],
        y: edges[row],
        w: 14.5,
        h: edges[row + 1] - edges[row]
      })))
    }]];
  })
);
