"""Materialize the page-by-page palette audit for the bundled PDF books.

No palette is inferred from logos, backgrounds or printed illustrations. Existing
reviewed drawing lessons are retained; additional colouring tasks are listed here.
Other pages have one black pencil for tracing, matching, answers and annotation.
Run from the repository root after importing books.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Image numbers, not the often different page numbers printed in the books.
EXTRA = {
    # 'maxford-english-3': {
    #     13: ('red blue orange green', 'Colour a-d and the apple; match and write letters'),
    # },
}

def names(text):
    # Multi-word names use underscores in the compact review table.
    return [name.replace('_', ' ') for name in text.split()]

def main():
    path = ROOT / 'books/colour-palettes.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    reviewed = {}
    total = 0
    for meta_file in sorted((ROOT/'books').glob('*/meta.json')):
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
        book = meta['id']
        pages = {str(p): {'picture': 'No requested colouring: black pencil for reading notes, matching or writing',
                          'colours': ['black']} for p in range(1, meta['pages']+1)}
        pages.update(data['books'].get(book, {}))
        for page, (colours, note) in EXTRA.get(book, {}).items():
            pages[str(page)] = {'picture': note, 'colours': names(colours)}
        for page, entry in pages.items():
            assert 1 <= int(page) <= meta['pages']
            assert entry['colours'] and len(set(entry['colours'])) == len(entry['colours'])
            assert all(name in data['colours'] for name in entry['colours']), (book, page, entry)
        reviewed[book] = dict(sorted(pages.items(), key=lambda item: int(item[0])))
        total += len(pages)
    data['books'] = reviewed
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(f'Reviewed palettes for {total} pages in {len(reviewed)} books.')

if __name__ == '__main__':
    main()
