// Reviewed against the printed pages. `page` is the reader's one-based image
// index; `printedPage` accounts for the English book's unnumbered front cover.
// A book with printed rhymes gets a Rhymes button that opens their pages, for example:
//   'book-id': [{ title: 'Twinkle, Twinkle', page: 60, printedPage: 59 }, { title: 'چندا ماموں', page: 31 }]
const rhymes = {};

export function bookRhymes(book) {
  return (rhymes[book.id] || []).filter(item => book.pages[item.page - 1]).map(item => ({ ...item, printedPage: item.printedPage || item.page }));
}

export function rhymeSpread(page) {
  return Math.floor((page - 1) / 2);
}
