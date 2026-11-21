import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { bookRhymes, rhymeSpread } from '../src/data/bookRhymes.js';

globalThis.window = {};
await import('../books/library.js');

test('a rhyme opens the spread that holds its page', () => {
  assert.deepEqual([1, 2, 3, 16, 38, 60].map(rhymeSpread), [0, 0, 1, 7, 18, 29]);
});

test('every listed rhyme points at a real page image of its book', () => {
  for (const book of window.PDF_BOOKS) {
    const pages = Array.from({ length: book.pages }, () => ({}));
    for (const item of bookRhymes({ id: book.id, pages })) {
      assert.ok(item.title.trim());
      assert.ok(existsSync(`${book.dir}/p${String(item.page).padStart(3, '0')}.jpg`), `${book.id} page ${item.page}`);
    }
  }
});

test('the rhyme shortcut does not leak into books without rhymes or with missing pages', () => {
  assert.deepEqual(bookRhymes({ id: 'a-book-without-rhymes', pages: Array(100).fill({}) }), []);
  assert.deepEqual(bookRhymes({ id: 'a-book-without-rhymes', pages: [] }), []);
});
