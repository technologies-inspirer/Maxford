import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import vm from 'node:vm';

// every book's activity file, so a new book is checked without changing this test
const files = ['activities', ...readdirSync(new URL('../books/', import.meta.url)).filter(name => /^activities-.+\.js$/.test(name)).map(name => name.slice(0, -3)), 'game-crops'];
const context = { window: { BOOK_ACTIVITIES: {} } };
vm.createContext(context);
for (const file of files) vm.runInContext(readFileSync(new URL(`../books/${file}.js`, import.meta.url), 'utf8'), context);
const { BOOK_ACTIVITIES: acts, GAME_FIXES: fixes } = JSON.parse(JSON.stringify(context.window));

test('every game fix belongs to a real game and keeps its crop on the page', () => {
  for (const [book, pages] of Object.entries(fixes)) for (const [page, games] of Object.entries(pages)) for (const [i, fix] of Object.entries(games)) {
    const game = [].concat(acts[book]?.[page] || [])[i];
    assert.equal(game?.type, 'game', `${book} ${page} ${i}`);
    const c = fix.crop;
    assert.ok(c.x >= 0 && c.y >= 0 && c.w > 5 && c.h > 5 && c.x + c.w <= 100.01 && c.y + c.h <= 100.01, `${book} ${page}`);
    // a fitted crop never moves far off the pictures the child taps
    for (const t of fix.targets || game.targets) {
      assert.ok(t.x + t.w > c.x && t.x < c.x + c.w && t.y + t.h > c.y && t.y < c.y + c.h, `${book} ${page} ${t.name}`);
    }
  }
});

test('every game has tap boxes inside its picture', () => {
  for (const [book, pages] of Object.entries(acts)) for (const [page, entries] of Object.entries(pages)) {
    for (const game of [].concat(entries).filter(item => item.type === 'game')) {
      const c = game.crop;
      assert.ok(game.targets.length >= 1, `${book} ${page}`);
      for (const t of game.targets) assert.ok(t.w > 0 && t.h > 0 && t.x + t.w > c.x && t.x < c.x + c.w && t.y + t.h > c.y && t.y < c.y + c.h, `${book} ${page} ${t.name}`);
    }
  }
});
