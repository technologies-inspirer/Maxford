// The book password the site opens the locked pages with by itself, so readers are not asked for it.
// The pages are locked on GitHub (tools/lock_books.py), so browsing the repository shows no book pictures; but this
// key is in the site's code too, so it hides the pictures from casual looking, it does not protect them. To ask the
// reader instead, empty this and the site shows its Book password page (src/portal/BookUnlock.jsx).
export const BOOK_KEY = ['Maxford', 'Parrot', '5148', 'Mango'].join('-');
