// Local stand-in for Vercel: serves public/ with clean URLs and runs api/world.js
// against an in-memory imitation of Upstash's REST API (GET, SET, EVAL-CAS).
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = process.argv[2], PORT = +process.argv[3] || 8787;
const store = new Map(); let calls = 0;
const redisSrv = http.createServer((req, res) => {
  let b = ''; req.on('data', c => b += c); req.on('end', () => {
    calls++;
    const cmd = JSON.parse(b); let result = null;
    if (cmd[0] === 'GET') result = store.has(cmd[1]) ? store.get(cmd[1]) : null;
    else if (cmd[0] === 'SET') { store.set(cmd[1], cmd[2]); result = 'OK'; }
    else if (cmd[0] === 'EVAL') {
      const [, , , kV, kW, expect, nv, raw] = cmd;
      const cur = store.has(kV) ? store.get(kV) : '0';
      if (cur !== expect) result = 0; else { store.set(kW, raw); store.set(kV, nv); result = 1; }
    }
    res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify({ result }));
  });
}).listen(PORT + 1);
process.env.KV_REST_API_URL = `http://127.0.0.1:${PORT + 1}`;
process.env.KV_REST_API_TOKEN = 'test';
const handler = require(path.join(ROOT, 'api', 'world.js'));
const types = { '.html': 'text/html; charset=utf-8', '.txt': 'text/plain' };
http.createServer((req, res) => {
  const u = new URL(req.url, 'http://x');
  if (u.pathname === '/api/world') {
    let b = ''; req.on('data', c => b += c); req.on('end', async () => {
      req.query = Object.fromEntries(u.searchParams);
      try { req.body = b ? JSON.parse(b) : undefined; } catch { req.body = b; }
      res.status = (c) => { res.statusCode = c; return res; };
      res.json = (o) => { res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify(o)); };
      await handler(req, res);
    });
    return;
  }
  let f = path.join(ROOT, 'public', u.pathname === '/' ? 'index.html' : u.pathname);
  if (!path.extname(f)) f += '.html';
  fs.readFile(f, (e, d) => { if (e) { res.statusCode = 404; return res.end('nf'); }
    res.setHeader('Content-Type', types[path.extname(f)] || 'application/octet-stream'); res.end(d); });
}).listen(PORT, () => console.log('up', PORT));
process.on('SIGTERM', () => { console.error('redis calls', calls); process.exit(0); });
