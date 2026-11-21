# Maxford Global — Interactive Books

Books that open like real ones: the publisher's videos, picture games, tracing with stars and colouring
with each picture's real colours, for **Play Group**, **Nursery** and **Prep**.

This project was made from the Javed Publishers interactive-books project (the same reader, portals and
activities) and starts with no books. `docs/adding-a-book.md` explains how to add a Maxford book with the
same activities as the earlier Play Group, Nursery and Prep books; their generators, data and tests are in
`templates/` to copy from.

## Run locally

Install Node.js 22.13 or newer, then from this folder:

```sh
npm install
npm run dev
```

Open http://localhost:5173/Maxford-Global/ (the URL Vite prints). On Windows you can double-click `start.bat`.
If PowerShell blocks `npm.ps1`, use `npm.cmd`.

Demo sign in:

- Admin: `admin@maxford.example` / `AdminDemo!2026`
- Reader: `reader@maxford.example` / `ReaderDemo!2026`

## Check and build

```sh
npm test               # unit tests
npm run prepare:pages  # production build, copied to index.html and site-assets/ for GitHub Pages
npm run check          # every book's pages, activities, QR links and assets are in the build
npm run check:pages    # the published index.html is the current build
```

The site is built for the `/Maxford-Global/` path, for a GitHub Pages repository named `Maxford-Global`.
To use another repository name, change `base` in `vite.config.js` and the same path in `tools/prepare-pages.mjs`,
`tools/check-pages.mjs` and `tools/check-migration.mjs`.

## Layout

| Path | What it holds |
|---|---|
| `app.html`, `src/`, `app.js`, `styles.css` | the reader and the admin and user portals |
| `books/` | `library.js` (books and their QR videos), one `activities-<book>.js` per book, palettes and colour rules, questions, checklists |
| `tools/` | shared tools: PDF import, QR video linking, tracing ink, palettes, game crops, checks |
| `templates/` | the earlier Play Group, Nursery and Prep books' generators, activity data and tests, as examples |
| `docs/` | how to add a book, colour palettes, PDF authoring, loading animation, mobile testing |
| `assets/` | logos and portal artwork (the Javed Publishers logo is still in place until a Maxford logo is supplied) |
