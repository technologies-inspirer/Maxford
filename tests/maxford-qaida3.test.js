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

test('printed QR codes open the publisher\'s videos, and game fixes point at the games', () => {
  assert.deepEqual(Object.keys(book.qr), ['11']);
  assert.equal(book.qr[11].videos[0].id, 'fSS9i-9nBeI');
  assert.equal(Object.keys(GAME_FIXES[ID]).length, 26);
  for (const [page, games] of Object.entries(GAME_FIXES[ID])) for (const index of Object.keys(games)) assert.equal(list(page)[index]?.type, 'game', `page ${page}`);
});
