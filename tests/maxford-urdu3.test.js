import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import vm from 'node:vm';
import { getLearningBooks } from '../src/data/learningCatalog.js';

const ID = 'maxford-global-qaida-3-urdu';
const read = path => readFileSync(new URL('../' + path, import.meta.url), 'utf8');
const exists = path => existsSync(new URL('../' + path, import.meta.url));
const context = { window: { BOOK_QUESTIONS: {} } };
vm.createContext(context);
for (const file of ['books/library.js', 'books/questions-maxford-urdu.js']) vm.runInContext(read(file), context);
const { PDF_BOOKS, BOOK_QUESTIONS } = JSON.parse(JSON.stringify(context.window));
const book = PDF_BOOKS.find(item => item.id === ID);
const questions = BOOK_QUESTIONS[ID];

// pages that are read or listened to, with nothing to write, colour or mark: the book's opening pages, the picture of
// children writing, each letter's introduction (پڑھیں اور پہچانیں), the word pages (colours, opposites, animals, birds,
// vegetables, fruits, body parts) and the alphabet to read aloud at the end
const READ_ONLY = [1, 2, 8, 11, 15, 20, 24, 27, 30, 33, 38, 39, 40, 43, 46, 49, 54, 55, 56, 59, 62, 65, 68, 71, 74, 79, 80, 81, 84, 87,
  90, 95, 96, 97, 100, 103, 106, 111, 112, 113, 116, 119, 122, 125, 128, 133, 134, 135, 138, 141, 144, 147, 153, 159];

test('the 2026-27 Qaida 3+ Urdu has its 159 printed pages, reads right to left, in Play Group Urdu', () => {
  assert.equal(book.pages, 159);
  assert.equal(book.rtl, true);
  assert.ok(exists(`${book.dir}/cover.jpg`));
  for (let page = 1; page <= 159; page++) assert.ok(exists(`${book.dir}/p${String(page).padStart(3, '0')}.jpg`), `page ${page}`);
  assert.deepEqual(getLearningBooks(PDF_BOOKS, { classId: 'play-group', seriesId: 'maxford', subjectId: 'urdu' }).map(item => item.id), [ID]);
  // each letter's introduction page from ا to ک has the publisher's videos (its QR code, plus the YouTube list in
  // videos-extra.json); ض (page 90) has none yet
  const withVideos = [11, 15, 20, 24, 27, 30, 33, 40, 43, 46, 49, 56, 59, 62, 65, 68, 71, 74, 81, 84, 87, 97, 100, 103, 106, 113, 116, 119];
  assert.deepEqual(Object.keys(book.qr).map(Number), withVideos);
  for (const page of withVideos) {
    const ids = book.qr[page].videos.map(v => v.id);
    assert.ok(ids.length >= 2 && new Set(ids).size === ids.length, `page ${page}: videos, each once`);
  }
  assert.ok(book.qr[59].videos.every(v => /ڈ/.test(v.title)), 'page 59: the ڈ videos');
});

test('every page with a printed task has its exercises', () => {
  for (let page = 1; page <= 159; page++) {
    if (READ_ONLY.includes(page)) assert.equal(questions[page], undefined, `page ${page} is read aloud only`);
    else assert.ok(questions[page]?.length, `page ${page} has a printed task`);
  }
});

test('every exercise is in Urdu, well formed and on its page', () => {
  const inside = (b, what) => assert.ok(b.x >= -0.01 && b.y >= -0.01 && b.x + b.w <= 100.01 && b.y + b.h <= 100.01, what);
  for (const [page, items] of Object.entries(questions)) for (const q of items) {
    const what = `page ${page}: ${q.title}`;
    assert.match(q.title, /[؀-ۿ]/, `${what}: Urdu title`);
    assert.match(q.say, /[؀-ۿ]/, `${what}: Urdu instruction`);
    inside(q.crop, what);
    assert.ok(q.button.x >= 0 && q.button.x + 14.5 <= 99.5 && q.button.y >= 0 && q.button.y + 3.5 <= 100, `${what}: button on the page`);
    if (q.kind === 'choose') {
      assert.ok(q.options.some(o => o.correct), what);
      q.options.forEach(o => inside(o, what));
    } else if (q.kind === 'write') q.lines.forEach(l => inside(l, what));
    else if (q.kind === 'colour') q.parts.forEach(p => inside(p.box, what));
    else if (q.kind === 'match') {
      const ids = q.dots.map(d => d.id);
      for (const id of new Set(ids)) assert.equal(ids.filter(x => x === id).length, 2, `${what}: ${id} has one partner`);
    } else assert.fail(`${what}: unknown kind ${q.kind}`);
  }
});

test('each letter has its tracing rows and its picture to colour', () => {
  for (const page of [12, 21, 66, 148]) {
    const [trace, paint] = questions[page];
    assert.equal(trace.kind, 'write');
    assert.ok(trace.lines.length >= 6, `page ${page}: rows`);
    assert.equal(paint.kind, 'colour');
  }
  const right = (page, k) => questions[page][k].options.filter(o => o.correct).length;
  assert.equal(right(14, 0), 6, 'page 14: the six ا');
  assert.equal(right(23, 0), 7, 'page 23: the seven ب');
  assert.deepEqual(questions[132][0].options.filter(o => o.correct).map(o => o.label), ['ل', 'م', 'ک', 'ف']);
});
