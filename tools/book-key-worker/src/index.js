// The key that opens the locked book pages (books/<id>/pNNN.jpg.enc), kept on Cloudflare and never on GitHub.
// The site (src/bookLock.js) asks for it when it starts and opens the pages with it, so readers see their books
// without a password. It answers only the site's own pages (their Origin), and is set as a secret:
//   npx wrangler secret put BOOK_KEY      (the base64 AES key, from tools/lock_books.py's password)
const SITES = ['https://technologies-inspirer.github.io', 'http://127.0.0.1:5175', 'http://localhost:5175', 'http://localhost:5173', 'http://127.0.0.1:5173'];

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const allowed = SITES.includes(origin);
    const headers = { 'Cache-Control': 'no-store', 'Vary': 'Origin', ...(allowed ? { 'Access-Control-Allow-Origin': origin } : {}) };
    if (request.method === 'OPTIONS') return new Response(null, { status: allowed ? 204 : 403, headers: { ...headers, 'Access-Control-Allow-Methods': 'GET' } });
    if (!allowed || request.method !== 'GET' || !env.BOOK_KEY) return new Response('Not here.', { status: 403, headers });
    return Response.json({ key: env.BOOK_KEY }, { headers });
  }
};
