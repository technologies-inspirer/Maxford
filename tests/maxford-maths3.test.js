import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import vm from 'node:vm';
import { getLearningBooks } from '../src/data/learningCatalog.js';

const ID = 'maxford-global-qaida-3-maths';
const read = path => readFileSync(new URL('../' + path, import.meta.url), 'utf8');
const exists = path => existsSync(new URL('../' + path, import.meta.url));
const context = { window: { BOOK_QUESTIONS: {} } };
vm.createContext(context);
for (const file of ['books/library.js', 'books/questions-maxford-maths.js']) vm.runInContext(read(file), context);
const { PDF_BOOKS, BOOK_QUESTIONS } = JSON.parse(JSON.stringify(context.window));
const book = PDF_BOOKS.find(item => item.id === ID);
const questions = BOOK_QUESTIONS[ID];

// pages whose only task is to say something aloud: About the Book, Contents, and "Number N: count and say"
const SAY_ONLY = [1, 2, 9, 13, 17, 21, 27, 33, 39, 43, 47, 55, 57, 65, 68, 71, 74, 77, 84, 87, 90, 93, 96];

test('the 2026-27 Qaida 3+ Maths has its 111 printed pages (the PDF\'s empty first page left out) in Play Group Maths', () => {
  assert.equal(book.pages, 111);
  assert.ok(exists(`${book.dir}/cover.jpg`));
  for (let page = 1; page <= 111; page++) assert.ok(exists(`${book.dir}/p${String(page).padStart(3, '0')}.jpg`), `page ${page}`);
  assert.deepEqual(getLearningBooks(PDF_BOOKS, { classId: 'play-group', seriesId: 'maxford', subjectId: 'maths' }).map(item => item.id), [ID]);
});

test('every page with a printed task has its exercises', () => {
  for (let page = 1; page <= 111; page++) {
    if (SAY_ONLY.includes(page)) assert.equal(questions[page], undefined, `page ${page} only asks to say the number`);
    else assert.ok(questions[page]?.length, `page ${page} has a printed task`);
  }
});

test('every exercise is well formed and sits on its page', () => {
  const inside = (b, what) => assert.ok(b.x >= 0 && b.y >= 0 && b.x + b.w <= 100.01 && b.y + b.h <= 100.01, what);
  for (const [page, items] of Object.entries(questions)) for (const q of items) {
    const what = `page ${page}: ${q.title}`;
    assert.equal(q.type, 'question');
    inside(q.crop, what);
    assert.ok(q.button.x >= 0 && q.button.x + 14.5 <= 99.5 && q.button.y >= 0 && q.button.y + 3.5 <= 100, `${what}: button on the page`);
    if (q.kind === 'choose') {
      assert.ok(q.options.some(o => o.correct), what);
      q.options.forEach(o => inside(o, what));
      if (q.mark) assert.ok(['tick', 'cross'].includes(q.mark), what);
      if (q.counts) for (const [group, n] of Object.entries(q.counts)) assert.ok(q.options.filter(o => o.group === group && o.correct).length >= n, what);
    } else if (q.kind === 'write') {
      assert.ok(q.lines.length > 0, what);
      q.lines.forEach(l => inside(l, what));
    } else if (q.kind === 'colour') {
      assert.ok(q.parts.length && q.parts.every(p => p.colours.length > 0), what);
      q.parts.forEach(p => inside(p.box, what));
    } else if (q.kind === 'match') {
      const ids = q.dots.map(d => d.id);
      for (const id of new Set(ids)) assert.equal(ids.filter(x => x === id).length, 2, `${what}: ${id} has one partner`);
    } else assert.fail(`${what}: unknown kind ${q.kind}`);
  }
});

test('the answers the book asks for', () => {
  const titled = (page, start) => questions[page].find(q => q.title.startsWith(start));
  const right = q => q.options.filter(o => o.correct).map(o => o.label);
  // find and circle: every printed 13, and nothing else
  assert.deepEqual(right(titled(73, 'Find and circle')), ['13', '13', '13', '13', '13']);
  // tick the group: counted from the pictures in the PDF
  assert.deepEqual(right(titled(67, 'Tick the group')), ['11 pictures']);
  // the 0 page: the empty basket
  assert.deepEqual(right(titled(56, 'Tick')), ['0 carrots']);
  // tick and cross get their own marks
  assert.equal(titled(7, 'Tick').mark, 'tick');
  assert.equal(titled(7, 'Cross').mark, 'cross');
  // cross out 7 jellyfish and 8 starfish
  assert.deepEqual(titled(46, 'Cross out').counts, { 7: 7, 8: 8 });
  // page 86 prints groups of 12 and 15 lemons for "16": that tick is left out, the rest of the page stays
  assert.equal(titled(86, 'Tick the group'), undefined);
  assert.ok(titled(86, 'Find and circle'));
});
