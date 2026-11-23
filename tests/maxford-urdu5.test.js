import test from 'node:test';
import assert from 'node:assert/strict';
import { statSync } from 'node:fs';
import { getLearningBooks } from '../src/data/learningCatalog.js';

const id = 'maxford-global-qaida-5-urdu';
globalThis.window = {};
await import('../books/library.js');
await import('../books/activities-maxford-urdu5.js');
await import('../books/questions-maxford-urdu5.js');
const [book] = getLearningBooks(window.PDF_BOOKS, { classId: 'prep', seriesId: 'maxford', subjectId: 'urdu' });
const questions = window.BOOK_QUESTIONS[id];
const games = window.BOOK_ACTIVITIES[id];

test('Prep Urdu has 110 reader pages and preserves right-to-left order', () => {
  assert.equal(book.id, id);
  assert.equal(book.rtl, true);
  assert.equal(book.pages, 110);
  const files = ['cover.jpg', ...Array.from({ length: book.pages }, (_, i) => `p${String(i + 1).padStart(3, '0')}.jpg`)];
  for (const file of files) assert.ok(statSync(new URL(`../${book.dir}/${file}`, import.meta.url)).size > 0, file);
});

test('printed exercises have their activities and reference-only pages stay clear', () => {
  const readOnly = new Set([1, 6, 8, 24]);
  for (let page = 1; page <= book.pages; page++) {
    assert.equal(Boolean(questions[page]?.length), !readOnly.has(page), `page ${page}`);
  }
  assert.deepEqual(Object.keys(games), ['10', '11']);
  assert.deepEqual(questions[60].find(item => item.kind === 'colour').parts.map(part => part.part),
    ['سیب', 'وہیل', 'کیلا', 'پتّا', 'مالٹا', 'کوّا']);
  assert.deepEqual(questions[102].find(item => item.kind === 'choose').options.filter(option => option.correct).map(option => option.label),
    ['باغ', 'تالاب', 'بطخیں', 'اچھا']);
});

test('writing, selection, matching and colouring controls fit their page crops', () => {
  const pageBounds = { x: 0, y: 0, w: 100, h: 100 };
  const inside = (item, crop, message) => {
    assert.ok(item.x >= crop.x - 0.01 && item.y >= crop.y - 0.01 &&
      item.x + (item.w ?? 0) <= crop.x + crop.w + 0.01 &&
      item.y + (item.h ?? 0) <= crop.y + crop.h + 0.01, message);
  };
  for (const [page, items] of [...Object.entries(questions), ...Object.entries(games)]) for (const item of items) {
    const label = `page ${page}, ${item.kind || item.type}`;
    assert.match(item.title, /[\u0600-\u06ff]/, label);
    inside(item.crop, pageBounds, label);
    inside({ ...item.button, w: 14.5, h: 3.5 }, pageBounds, label);
    for (const target of [
      ...(item.lines || []), ...(item.options || []), ...(item.dots || []), ...(item.targets || []),
      ...(item.parts || []).map(part => part.box)
    ]) inside(target, item.crop, label);
    if (item.kind === 'match') {
      for (const id of new Set(item.dots.map(dot => dot.id))) assert.equal(item.dots.filter(dot => dot.id === id).length, 2, label);
    }
  }
});
