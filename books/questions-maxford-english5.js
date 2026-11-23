// Writing areas measured from the printed Prep English worksheets.
const box = (x, y, w, h) => ({ x, y, w, h });
const rows = (x, top, width, height, count, spacing) =>
  Array.from({ length: count }, (_, index) => box(x, top + index * spacing, width, height));
const write = (title, say, lines) => [{
  type: 'question',
  kind: 'write',
  title,
  say,
  button: { x: 66, y: 7.2 },
  crop: box(0, 12, 100, 77.5),
  lines
}];

const beginningSounds = write(
  'Write the beginning sound.',
  'Say the name of each picture. Write its first letter in the blank space.',
  [32.14, 74.28].flatMap(x => [17.65, 37, 56.36, 75.72].map(y => box(x, y, 5.8, 5.87)))
);
const missingVowels = write(
  'Write the missing vowel.',
  'Say the word for each picture. Write the missing vowel between the two letters.',
  [15.58, 42.92, 70.26].flatMap(x => [29.9, 55.7, 81.54].map(y => box(x + 4.55, y, 4, 5.33)))
);
const makeSentences = write(
  'Make sentences using the given words.',
  'Use the word beside each picture to make a sentence. Write it on the line.',
  rows(34.15, 18.33, 55.88, 4.89, 6, 12.314)
);

const questions = {
  12: beginningSounds,
  13: beginningSounds,
  14: beginningSounds,
  15: missingVowels,
  16: missingVowels,
  111: write(
    'Rewrite the sentences using sentence locks.',
    'Begin each sentence with a capital letter and end it with a full stop.',
    rows(9.34, 34.71, 82.34, 4.89, 5, 12.182)
  ),
  112: write(
    'Rewrite the questions using sentence locks.',
    'Begin each question with a capital letter and end it with a question mark.',
    rows(9.34, 34.85, 82.34, 4.89, 5, 12.182)
  ),
  113: write('Read and write the sentences.', 'Copy each sentence onto the line below it.', rows(9.34, 21.94, 82.34, 4.89, 6, 12.184)),
  119: makeSentences,
  120: makeSentences,
  121: makeSentences,
  122: makeSentences
};

for (const [page, sentence, x, width, starts] of [
  [86, 'This is a/an…', 31.13, 60.65, [22.99, 37.86, 52.72, 67.59, 82.27]],
  [87, 'That is a/an…', 31.15, 60.63, [22.82, 37.68, 52.55, 67.41, 82.1]],
  [90, 'These are…', 8.31, 60.08, [23.29, 38.15, 52.86, 67.79, 82.65]],
  [91, 'Those are…', 31.68, 60.04, [22.82, 37.68, 52.55, 67.41, 82.1]]
]) {
  questions[page] = write(`Read and write the sentences with “${sentence}”`,
    'Read each sentence aloud, then copy it on the line below it.',
    starts.map(y => box(x, y, width, 5.04)));
}

window.BOOK_QUESTIONS = window.BOOK_QUESTIONS || {};
window.BOOK_QUESTIONS['maxford-global-qaida-5-english'] = questions;
