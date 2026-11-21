# Adding a Maxford book

Maxford Global has three classes: **Play Group** (3+ books), **Nursery** (4+) and **Prep** (5+).
Each book gets the same kinds of activities the Play Group, Nursery and Prep books of the Javed
Publishers project had. The generators, data and tests of those books are kept in `templates/` to copy from.

## The rule

The digital book mirrors the printed book. Add only what the page itself has:

- **Watch videos from the printed QR codes** (the "Watch this" button on that page).
- **A Play game only where the page has a natural one** (find or tap the printed pictures and words).
- **Tracing and colouring only where the page prints a tracing, writing or colouring task.**
- **The publisher's own videos** (Story, Vocabulary, Phonic Poem, Formation) when the publisher supplies the links.
- **No stories, narration or activities made up by us.**

## Activities the earlier books used

| Activity | What the child sees | Data | Used in (templates/) |
|---|---|---|---|
| QR videos | "Watch this" on the printed QR code; student, teacher and parent videos | `books/<book>/qr.json` -> `books/library.js` (`tools/link_videos.py`) | every book |
| Publisher videos | Story, Vocabulary, Phonic Poem, Formation ("How to write ...") buttons | `type: 'videos'` and `fill.video` | english3, english4, maths3, maths4, urdu3, urdu4, urdu5, computer0 |
| Picture game | "Play": find and tap the named pictures, with stars | `type: 'game'` (crop, targets) | all books |
| Tracing | dotted letters, numbers and lines: "Show me how", then the child traces from the start dot and earns a star | `type: 'fill'`, marks with `glyph` + `ink` (`tools/ink.py`, `tools/urdu_alif.py`) | all books |
| Colouring | crayons of the picture's real colours; a wrong colour says the right one | `fill.colours` from `books/colour-palettes.json`; part rules in `books/colour-regions.json` | all books |
| Exercise questions | colour / write / match / choose on practice pages | `books/questions.js` (`templates/books/questions.js` has the helpers) | english3, maths3, maths5, urdu3 |
| Checklists | the printed "I can ..." boxes become tick boxes | `books/checklists.js` (`tools/find_checklists.py`) | Play Group books |
| Letter lesson bar | a side button per letter or number: lesson page, its video, game and tracing | `src/englishLessons.js` (`LESSON_BOOKS`) | english3, english4, maths3, maths4, urdu3, urdu4, urdu5, computer0 |
| Rhymes | a Rhymes button listing the printed rhymes | `src/data/bookRhymes.js` | english3, urdu3 |
| Urdu books | right-to-left reading, Urdu prompts and colour names | `"rtl": true` in the book's `meta.json` | urdu3, urdu4, urdu5 |

## Steps for one book

1. **Pages.** Copy the PDF into `source-pdfs/` (not committed), named after the book, for example
   `source-pdfs/Maxford English 3.pdf`, and convert it: `python tools/import_pdf.py "source-pdfs/Maxford English 3.pdf"`.
   The file name gives the book id (`maxford-english-3`) and title; it writes `books/<book-id>/p001.jpg ...`,
   `cover.jpg` and `meta.json`. Name the files by age: 3 Play Group, 4 Nursery, 5 Prep.
   An Urdu book needs `"rtl": true` in its `meta.json`.
2. **QR videos.** `python tools/link_videos.py scan "source-pdfs/<file>.pdf" <book-id>`, then `python tools/link_videos.py`
   (reads every QR link, finds its YouTube videos and rebuilds `books/library.js`).
3. **Library place.** Add the book to `learningBookMetadata` in `src/data/learningCatalog.js`
   (`classId`: `play-group`, `nursery` or `prep`; `seriesId`: `maxford`; `subjectId`: `english`, `urdu`, `maths`, ...).
4. **Activities.** Copy the closest generator from `templates/tools/make_*.py` to `tools/make_<book>.py`, look at every page
   and set the games, tracing and videos the page really has. It writes `books/activities-<book>.js`.
   Import that file in `src/main.jsx`.
5. **Colours.** `python tools/review_page_palettes.py` gives every page a palette entry; set each colouring page's
   real colours in `books/colour-palettes.json` (black only where the picture has black), and add part rules
   to `books/colour-regions.json` where a part has one right colour.
6. **Lesson bar, rhymes, questions.** Add the book to `LESSON_BOOKS` in `src/englishLessons.js` when it teaches one
   letter or number per lesson; list printed rhymes in `src/data/bookRhymes.js`; add practice-page questions to
   `books/questions.js`.
7. **Test.** Copy the closest test from `templates/tests/` to `tests/<book>.test.js`. Then run
   `npm test`, `npm run prepare:pages`, `npm run check` and `npm run check:pages`, and open the book in the
   browser (`npm run dev`) to try each activity.

## Sign in (demo)

- Admin: `admin@maxford.example` / `AdminDemo!2026`
- Reader: `reader@maxford.example` / `ReaderDemo!2026`
