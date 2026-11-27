"""Lock the books' page pictures with a password, so the copies on GitHub cannot be looked at without it.

    set BOOK_PASSWORD=...   (PowerShell: $env:BOOK_PASSWORD = '...')
    python tools/lock_books.py              # writes books/<id>/pNNN.jpg.enc and books/lock.json

Each page picture (books/<id>/pNNN.jpg, kept on this PC and left out of git) is encrypted with AES-256-GCM. The key
comes from the password with PBKDF2-SHA256 (books/lock.json keeps the salt and the number of rounds, and a short
check text locked with the key, so the site can tell a wrong password; it never keeps the password or the key).
A file's IV is derived from its own contents, so locking an unchanged picture again gives the same file and git sees
no change. The site opens the files in the browser (book-lock-sw.js) once the password is given.

Changing the password: run again with the new one (books/lock.json gets a new salt, every file is locked again).
Covers (cover.jpg) and the trace shapes stay open: the sign-in page and the dashboard show them before sign-in.
"""
import base64
import glob
import hashlib
import hmac
import json
import os
import re
import sys

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
LOCK = os.path.join(ROOT, 'books', 'lock.json')
ROUNDS = 250_000
CHECK = b'Maxford Global books'
PAGE = re.compile(r'p\d{3}\.jpg$')


def key_of(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, ROUNDS, 32)


def lock(key, data):
    iv = hmac.new(key, b'iv' + data, hashlib.sha256).digest()[:12]
    return iv + AESGCM(key).encrypt(iv, data, None)


def main():
    password = os.environ.get('BOOK_PASSWORD', '')
    if len(password) < 8:
        sys.exit('Set BOOK_PASSWORD (at least 8 characters) first.')
    old = json.load(open(LOCK, encoding='utf-8')) if os.path.exists(LOCK) else None
    # keep the salt while the password is the same (so files do not change); a new password gets a new salt
    salt = base64.b64decode(old['salt']) if old else os.urandom(16)
    key = key_of(password, salt)
    if old:
        check = base64.b64decode(old['check'])
        try:
            same = AESGCM(key).decrypt(check[:12], check[12:], None) == CHECK
        except Exception:
            same = False
        if not same:
            salt = os.urandom(16)
            key = key_of(password, salt)
            print('A new password: every page is locked again.')
    with open(LOCK, 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'cipher': 'AES-256-GCM', 'kdf': 'PBKDF2-SHA256', 'rounds': ROUNDS,
                   'salt': base64.b64encode(salt).decode(), 'check': base64.b64encode(lock(key, CHECK)).decode()}, f, indent=1)
        f.write('\n')
    done = changed = 0
    for path in sorted(glob.glob(os.path.join(ROOT, 'books', '*', 'p*.jpg'))):
        if not PAGE.search(path):
            continue
        data = open(path, 'rb').read()
        out = lock(key, data)
        target = path + '.enc'
        if not (os.path.exists(target) and open(target, 'rb').read() == out):
            open(target, 'wb').write(out)
            changed += 1
        done += 1
    print(f'{done} pages locked ({changed} written).')
    # (for tools/book-key.ps1: where to write the key, base64, to put it on Cloudflare; never inside the project)
    key_out = os.environ.get('BOOK_KEY_OUT')
    if key_out:
        with open(key_out, 'w', encoding='ascii', newline='') as f:
            f.write(base64.b64encode(key).decode())


if __name__ == '__main__':
    main()
