import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import vm from 'node:vm';
import { getLearningBooks } from '../src/data/learningCatalog.js';

const ID = 'maxford-global-qaida-3-english';
const read = path => readFileSync(new URL('../' + path, import.meta.url), 'utf8');
const exists = path => existsSync(new URL('../' + path, import.meta.url));
const context = { window: { BOOK_ACTIVITIES: {} } };
vm.createContext(context);
for (const file of ['books/library.js', 'books/activities-maxford.js', 'books/game-crops.js']) vm.runInContext(read(file), context);
const { PDF_BOOKS, BOOK_ACTIVITIES, GAME_FIXES } = JSON.parse(JSON.stringify(context.window));
const book = PDF_BOOKS.find(item => item.id === ID);
const acts = BOOK_ACTIVITIES[ID];
const list = page => [].concat(acts[page] || []);
const palettes = JSON.parse(read('books/colour-palettes.json'));

// a to z: each Sound page, its "Trace and say the sound" page is the next one
const SOUND_PAGES = [11, 15, 19, 23, 31, 35, 39, 43, 49, 53, 57, 61, 69, 73, 77, 81, 87, 91, 95, 99, 107, 111, 115, 119, 125, 129];

test('the 2026-27 Qaida 3+ English has its 135 printed pages (the PDF\'s empty first page left out) in Play Group English', () => {
  assert.equal(book.pages, 135);
  assert.ok(exists(`${book.dir}/cover.jpg`));
  for (let page = 1; page <= 135; page++) assert.ok(exists(`${book.dir}/p${String(page).padStart(3, '0')}.jpg`), `page ${page}`);
  assert.deepEqual(getLearningBooks(PDF_BOOKS, { classId: 'play-group', seriesId: 'maxford', subjectId: 'english' }).map(item => item.id), [ID]);
});

test('every letter has its picture game on the Sound page and tracing on the next page; no home-made animations', () => {
  assert.equal(SOUND_PAGES.length, 26);
  for (const [k, page] of SOUND_PAGES.entries()) {
    const letter = String.fromCharCode(97 + k);
    const game = list(page).find(item => item.type === 'game');
    assert.equal(game.title, `Find the ${letter} words!`);
    assert.equal(game.targets.length, 3);
    const fill = list(page + 1).find(item => item.type === 'fill');
    assert.ok(fill, `trace ${letter}`);
    assert.equal(fill.steps.filter(step => step.marks.some(mark => mark.glyph === letter)).length, 5, `${letter}: two big letters and three rows`);
    for (const step of fill.steps) for (const mark of step.marks) if (mark.ink) assert.ok(exists(mark.ink.src), mark.ink.src);
    const named = palettes.books[ID][page + 1].colours.map(name => palettes.colours[name]);
    assert.deepEqual(fill.colours, named, `${letter}: the reviewed colours of its picture`);
  }
  for (const entries of Object.values(acts)) for (const item of [].concat(entries)) {
    assert.notEqual(item.type, 'story', 'No home-made animations');
    if (item.type === 'videos') for (const video of item.videos) assert.ok(exists(video.src.split('#')[0]), video.src);
  }
});

test('every letter\'s "Trace, write and say the sound" page, the pre-writing pages and the a to z chart can be written on', () => {
  for (const [k, page] of SOUND_PAGES.entries()) {
    const letter = String.fromCharCode(97 + k);
    const fill = list(page + 2).find(item => item.type === 'fill' && item.title === 'Trace, write and say the sound');
    assert.ok(fill, `write ${letter} on page ${page + 2}`);
    assert.ok(fill.steps.length >= 6, `${letter}: big letter, small letter and four rows`);
  }
  for (const page of [7, 8, 9, 10]) assert.ok(list(page).some(item => item.type === 'fill'), `pre-writing page ${page}`);
  const chart = list(133).find(item => item.type === 'fill');
  assert.deepEqual([...new Set(chart.steps.flatMap(step => step.marks.map(mark => mark.glyph)))].sort().join(''), 'abcdefghijklmnopqrstuvwxyz');
});

test('every printed exercise is a question at its place on the page', () => {
  const qc = { window: { BOOK_QUESTIONS: {} } };
  vm.createContext(qc);
  vm.runInContext(read('books/questions-maxford.js'), qc);
  const questions = JSON.parse(JSON.stringify(qc.window.BOOK_QUESTIONS[ID]));
  const EXERCISE_PAGES = [3, 4, 5, 6, 14, 18, 22, 26, 27, 28, 29, 34, 38, 42, 46, 47, 48, 52, 56, 60, 64, 65, 66, 67, 72, 76, 80, 84, 85, 86,
    90, 94, 98, 102, 103, 104, 110, 114, 118, 122, 123, 124, 128, 132, 134, 135];
  assert.deepEqual(Object.keys(questions).map(Number).sort((a, b) => a - b), EXERCISE_PAGES);
  const inside = (b, what) => assert.ok(b.x >= 0 && b.y >= 0 && b.x + b.w <= 100 && b.y + b.h <= 100, what);
  for (const [page, items] of Object.entries(questions)) for (const q of items) {
    const what = `page ${page}: ${q.title}`;
    assert.equal(q.type, 'question');
    inside(q.crop, what);
    // the button is a pill drawn from this corner, about 14.5% of the page wide and 3.5% high: all of it on the page
    assert.ok(q.button.x >= 0 && q.button.x + 14.5 <= 99.5 && q.button.y >= 0 && q.button.y + 3.5 <= 100, `${what}: button on the page`);
    if (q.kind === 'choose') {
      assert.ok(q.options.some(o => o.correct) && q.options.some(o => !o.correct), what);
      q.options.forEach(o => inside(o, what));
    } else if (q.kind === 'write') {
      assert.ok(q.lines.length > 0, what);
      q.lines.forEach(l => inside(l, what));
    } else if (q.kind === 'colour') {
      assert.ok(q.parts.every(p => p.colours.length > 0), what);
    } else if (q.kind === 'match') {
      const ids = q.dots.map(d => d.id);
      for (const id of new Set(ids)) assert.ok(ids.filter(x => x === id).length >= 2, `${what}: ${id} has a partner`);
    } else assert.fail(`${what}: unknown kind ${q.kind}`);
  }
});

test('printed QR codes open the publisher\'s videos, and game fixes point at the games', () => {
  assert.deepEqual(Object.keys(book.qr), ['11']);
  assert.equal(book.qr[11].videos[0].id, 'fSS9i-9nBeI');
  assert.equal(Object.keys(GAME_FIXES[ID]).length, 26);
  for (const [page, games] of Object.entries(GAME_FIXES[ID])) for (const index of Object.keys(games)) assert.equal(list(page)[index]?.type, 'game', `page ${page}`);
});
