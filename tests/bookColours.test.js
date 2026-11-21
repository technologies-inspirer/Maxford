import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import vm from 'node:vm';
import { englishLessons } from '../src/englishLessons.js';

const read = path => readFileSync(new URL('../' + path, import.meta.url), 'utf8');
const reviewed = JSON.parse(read('books/colour-palettes.json'));
const regionRules = JSON.parse(read('books/colour-regions.json'));
const context = { window: {} };
vm.createContext(context);
// every book's activity file, so a new book is checked without changing this test
const files = ['activities', ...readdirSync(new URL('../books/', import.meta.url)).filter(name => /^activities-.+\.js$/.test(name)).map(name => name.slice(0, -3))];
for (const file of files) vm.runInContext(read(`books/${file}.js`), context);
vm.runInContext(read('books/library.js'), context);
const activities = JSON.parse(JSON.stringify(context.window.BOOK_ACTIVITIES || {}));
const library = context.window.PDF_BOOKS;
const fill = (book, page) => [].concat(activities[book]?.[page] || []).find(activity => activity.type === 'fill');

test('the shared colours are valid and named once', () => {
  const names = Object.keys(reviewed.colours);
  assert.ok(names.length >= 13);
  for (const name of names) assert.match(reviewed.colours[name], /^#[0-9a-f]{6}$/i, name);
  for (const name of ['red', 'green', 'leaf green', 'yellow', 'orange', 'blue', 'pink', 'purple', 'brown', 'light brown', 'grey', 'black']) assert.ok(reviewed.colours[name], name);
});

test('every book page has an explicit task palette with valid distinct colours', () => {
  for (const book of library) {
    const pages = reviewed.books[book.id];
    assert.ok(pages, `No palettes for ${book.id}: run tools/review_page_palettes.py`);
    assert.equal(Object.keys(pages).length, book.pages, book.id);
    for (let page = 1; page <= book.pages; page++) {
      const entry = pages[page];
      assert.ok(entry?.picture, `${book.id}/${page}`);
      assert.ok(entry.colours.length);
      assert.equal(new Set(entry.colours).size, entry.colours.length);
      for (const name of entry.colours) assert.match(reviewed.colours[name] || '', /^#[0-9a-f]{6}$/i, `${book.id}/${page}: ${name}`);
    }
  }
});

test('every drawing activity uses only the colours of its reviewed page palette', () => {
  for (const [book, pages] of Object.entries(activities)) {
    for (const [page, pageActivities] of Object.entries(pages)) {
      for (const activity of [].concat(pageActivities)) {
        if (activity.type !== 'fill') continue;
        const entry = reviewed.books[book]?.[page];
        assert.ok(entry, `Unreviewed activity: ${book} / ${page}`);
        const expected = entry.colours.map(name => reviewed.colours[name]);
        for (const colour of activity.colours || []) assert.ok(expected.includes(colour), `Authored colour unavailable: ${book}/${page}/${colour}`);
        for (const step of activity.steps || []) for (const mark of step.marks || []) {
          if (mark.scribble) assert.ok(expected.includes(mark.scribble), `Demo colour unavailable: ${book} / ${page}`);
        }
      }
    }
  }
});

test('part rules refer to real activities and colours available on their pages', () => {
  for (const [book, pages] of Object.entries(regionRules)) for (const [page, regions] of Object.entries(pages)) {
    const activity = fill(book, page);
    assert.ok(activity, `${book} / ${page}`);
    for (const region of regions) {
      if (!region.colour) assert.equal(activity.drawingMode, 'regions', 'Only reviewed drawing boundaries may omit a required colour');
      else assert.ok(activity.colours.includes(region.colour), `Unavailable part colour: ${book} / ${page} / ${region.part}`);
      const box = region.box || region.componentBox;
      if (box) {
        const [x, y, w, h] = box;
        assert.ok(x >= 0 && y >= 0 && w > 0 && h > 0 && x + w <= 100 && y + h <= 100);
      } else if (region.seed) {
        assert.ok(region.seed.every(n => n >= 0 && n <= 100));
        if (region.cut) assert.ok(region.cut.length === 2 && region.cut.every(point => point.every(n => n >= 0 && n <= 100)));
      } else {
        assert.ok(region.polygon.length >= 3);
        assert.ok(region.polygon.every(point => point.every(n => n >= 0 && n <= 100)));
      }
    }
  }
});

test('the letter lesson bar is off until a book is listed in src/englishLessons.js', () => {
  // A sample letter book: each letter page has Story and Vocabulary videos and a game, the next page its tracing.
  const page = (name, extra = []) => ({ acts: [
    { type: 'videos', label: 'Story', title: `Story of letter ${name}`, videos: [{ title: 'Story', src: 'https://youtu.be/7hpynjvzeS0' }] },
    { type: 'game', title: 'Find', targets: [{ name: 'apple' }] }, ...extra] });
  const book = { id: 'maxford-sample-3', pages: [{ acts: [] }, page('Aa'), { acts: [{ type: 'fill', steps: [] }] }, page('Bb'), { acts: [{ type: 'fill', steps: [] }] }] };
  assert.deepEqual(englishLessons(book), []);
});
