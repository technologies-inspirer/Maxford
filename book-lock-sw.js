// The book pages on the site are locked (books/<id>/pNNN.jpg.enc, made by tools/lock_books.py). This service worker
// answers the app's requests for books/<id>/pNNN.jpg: it fetches the locked file and opens it with the key the reader
// unlocked with their book password (src/bookLock.js sends it here and keeps it in this browser's IndexedDB).
// Without the key a page answers 403, so the pictures cannot be seen by opening their links either.
const DB = 'maxford-book-lock', STORE = 'keys';
let key = null;

const db = () => new Promise((resolve, reject) => {
  const open = indexedDB.open(DB, 1);
  open.onupgradeneeded = () => open.result.createObjectStore(STORE);
  open.onsuccess = () => resolve(open.result);
  open.onerror = () => reject(open.error);
});
const saved = async () => {
  const d = await db();
  return new Promise(resolve => {
    const get = d.transaction(STORE).objectStore(STORE).get('page-key');
    get.onsuccess = () => resolve(get.result || null);
    get.onerror = () => resolve(null);
  });
};
const importKey = raw => crypto.subtle.importKey('raw', raw, 'AES-GCM', false, ['decrypt']);

self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', event => event.waitUntil(self.clients.claim()));
self.addEventListener('message', event => {
  if (event.data?.type === 'book-key') event.waitUntil((async () => { key = event.data.raw ? await importKey(event.data.raw) : null; })());
});

const PAGE = /\/books\/[^/]+\/p\d{3}\.jpg$/;
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (url.origin !== location.origin || !PAGE.test(url.pathname)) return;
  event.respondWith((async () => {
    if (!key) {
      const raw = await saved().catch(() => null);
      if (raw) key = await importKey(raw);
    }
    if (!key) return new Response('This book is locked.', { status: 403 });
    // (checked with the server each time: after the pages are locked again, an old copy would not open)
    const locked = await fetch(url.pathname + '.enc', { cache: 'no-cache' });
    if (!locked.ok) return new Response('Page not found.', { status: 404 });
    const data = await locked.arrayBuffer();
    try {
      const open = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: data.slice(0, 12) }, key, data.slice(12));
      return new Response(open, { headers: { 'Content-Type': 'image/jpeg', 'Cache-Control': 'private, max-age=86400' } });
    } catch {
      return new Response('This book is locked.', { status: 403 });
    }
  })());
});
