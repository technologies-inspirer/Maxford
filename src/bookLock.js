// The book password: the pages on the site are locked (tools/lock_books.py); this unlocks them in this browser.
// The password becomes the key (PBKDF2, as books/lock.json says), checked against the locked check text, then the
// key goes to the service worker (book-lock-sw.js) that opens each page, and stays in this browser (IndexedDB) so
// the reader is asked only once on this device.
const DB = 'maxford-book-lock', STORE = 'keys';
const base = import.meta.env.BASE_URL;
const fromB64 = text => Uint8Array.from(atob(text), c => c.charCodeAt(0));

const db = () => new Promise((resolve, reject) => {
  const open = indexedDB.open(DB, 1);
  open.onupgradeneeded = () => open.result.createObjectStore(STORE);
  open.onsuccess = () => resolve(open.result);
  open.onerror = () => reject(open.error);
});
const put = async value => {
  const d = await db();
  await new Promise((resolve, reject) => {
    const tx = d.transaction(STORE, 'readwrite');
    value ? tx.objectStore(STORE).put(value, 'page-key') : tx.objectStore(STORE).delete('page-key');
    tx.oncomplete = resolve; tx.onerror = () => reject(tx.error);
  });
};
const get = async () => {
  const d = await db();
  return new Promise(resolve => {
    const req = d.transaction(STORE).objectStore(STORE).get('page-key');
    req.onsuccess = () => resolve(req.result || null);
    req.onerror = () => resolve(null);
  });
};

let worker = null;
// Start the page opener; resolves once it controls this page (the first visit reloads once for that).
export async function startBookLock() {
  if (!('serviceWorker' in navigator)) return false;
  const registration = await navigator.serviceWorker.register(`${base}book-lock-sw.js`, { scope: base });
  await navigator.serviceWorker.ready;
  worker = navigator.serviceWorker.controller;
  if (!worker) {
    if (!sessionStorage.getItem('book-lock-reloaded')) { sessionStorage.setItem('book-lock-reloaded', '1'); location.reload(); return false; }
    worker = registration.active;
  }
  const raw = await get().catch(() => null);
  if (raw) worker?.postMessage({ type: 'book-key', raw });
  return true;
}

export async function isBookUnlocked() {
  return !!(await get().catch(() => null));
}

// Returns true when the password opens the books, false when it is wrong.
export async function unlockBooks(password) {
  const lock = await (await fetch(`${base}books/lock.json`, { cache: 'no-store' })).json();
  const material = await crypto.subtle.importKey('raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits({ name: 'PBKDF2', hash: 'SHA-256', salt: fromB64(lock.salt), iterations: lock.rounds }, material, 256);
  const key = await crypto.subtle.importKey('raw', bits, 'AES-GCM', false, ['decrypt']);
  const check = fromB64(lock.check);
  try {
    await crypto.subtle.decrypt({ name: 'AES-GCM', iv: check.slice(0, 12) }, key, check.slice(12));
  } catch {
    return false;
  }
  await put(bits);
  (navigator.serviceWorker?.controller || worker)?.postMessage({ type: 'book-key', raw: bits });
  return true;
}

export async function lockBooks() {
  await put(null);
  (navigator.serviceWorker?.controller || worker)?.postMessage({ type: 'book-key', raw: null });
}
