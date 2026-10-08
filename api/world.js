/* /api/world - the shared test world.
 *
 * The prototype keeps its whole state in one object. On the deployed site
 * every tab joins a "world" (main, empty, or any ?world=name) held here, so a
 * reader on one phone and a bookshop on another see the same requests,
 * offers and orders.
 *
 *   GET  /api/world?space=main&v=12      -> { v, same:true } or { v, world }
 *   POST /api/world?space=main  { op:'init',  world }   create it if nobody has
 *                               { op:'patch', patch }   merge record by record
 *                               { op:'reset', world }   start over for everyone
 *
 * Storage is Redis over Upstash's REST API: no npm packages, nothing to
 * build. Add "Upstash for Redis" (Vercel -> Storage / Marketplace) to the
 * project and its environment variables appear on their own.
 *
 * This is a test harness, not the product: there is no sign-in, anyone with
 * the link can change the world, and the later of two edits to the same
 * record wins. Nothing here should be carried into production.
 */

const URL_ = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;
const MAX_BYTES = 4 * 1024 * 1024;           // Vercel's request limit is 4.5 MB
const TTL_SECONDS = 60 * 60 * 24 * 30;       // an untouched world expires after 30 days

async function redis(cmd) {
  const r = await fetch(URL_, {
    method: 'POST',
    headers: { Authorization: `Bearer ${TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(cmd),
  });
  const j = await r.json();
  if (!r.ok || j.error) throw new Error(j.error || `redis ${r.status}`);
  return j.result;
}

/* Write a new world only if nobody else wrote one since we read it. */
const CAS = `
local cur = redis.call('GET', KEYS[1]) or '0'
if cur ~= ARGV[1] then return 0 end
redis.call('SET', KEYS[2], ARGV[3], 'EX', ARGV[4])
redis.call('SET', KEYS[1], ARGV[2], 'EX', ARGV[4])
return 1`;

/* ---- the same merge rules the page uses ---------------------------------- */
const isMap = (x) => x && typeof x === 'object' && !Array.isArray(x);
const keyOf = (x) => (isMap(x) && x.id != null ? 'i:' + x.id : 'j:' + JSON.stringify(x));

function applyPatch(world, patch) {
  const w = world ? JSON.parse(JSON.stringify(world)) : {};
  for (const k of Object.keys(patch || {})) {
    const c = patch[k];
    if (!c || typeof c !== 'object') continue;
    if (c.t === 'set') w[k] = c.v;
    else if (c.t === 'del') delete w[k];
    else if (c.t === 'map') {
      const m = isMap(w[k]) ? w[k] : {};
      for (const kk of c.rm || []) delete m[kk];
      for (const kk of Object.keys(c.up || {})) m[kk] = c.up[kk];
      w[k] = m;
    } else if (c.t === 'list') {
      const gone = new Set(c.rm || []);
      const arr = (Array.isArray(w[k]) ? w[k] : []).filter((x) => !gone.has(keyOf(x)));
      for (const x of c.up || []) {
        const key = keyOf(x);
        const at = arr.findIndex((y) => keyOf(y) === key);
        if (at >= 0) arr[at] = x; else arr.push(x);
      }
      w[k] = arr;
    }
  }
  return w;
}

function send(res, status, body) {
  res.setHeader('Cache-Control', 'no-store');
  res.status(status).json(body);
}

module.exports = async function handler(req, res) {
  if (!URL_ || !TOKEN) {
    return send(res, 503, { error: 'The shared test needs a Redis database. Add Upstash for Redis to this Vercel project.' });
  }
  const space = String((req.query && req.query.space) || 'main').toLowerCase();
  if (!/^[a-z0-9-]{1,32}$/.test(space)) return send(res, 400, { error: 'Bad world name' });
  const kV = `sc:world:${space}:v`;
  const kW = `sc:world:${space}:db`;

  try {
    if (req.method === 'GET') {
      const v = Number(await redis(['GET', kV])) || 0;
      if (req.query && String(req.query.v) === String(v)) return send(res, 200, { v, same: true });
      const raw = v ? await redis(['GET', kW]) : null;
      return send(res, 200, { v, world: raw ? JSON.parse(raw) : null });
    }

    if (req.method !== 'POST') return send(res, 405, { error: 'GET or POST' });
    const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
    const op = body.op;

    if (op === 'init' || op === 'reset') {
      if (!isMap(body.world)) return send(res, 400, { error: 'world missing' });
      const raw = JSON.stringify(body.world);
      if (raw.length > MAX_BYTES) return send(res, 413, { error: 'World too large' });
      for (let i = 0; i < 8; i++) {
        const v = Number(await redis(['GET', kV])) || 0;
        if (op === 'init' && v) {           // somebody got there first: join theirs
          return send(res, 200, { v, world: JSON.parse(await redis(['GET', kW])) });
        }
        const ok = await redis(['EVAL', CAS, '2', kV, kW, String(v), String(v + 1), raw, String(TTL_SECONDS)]);
        if (ok === 1) return send(res, 200, { v: v + 1, world: body.world });
      }
      return send(res, 409, { error: 'Busy, try again' });
    }

    if (op === 'patch') {
      if (!isMap(body.patch)) return send(res, 400, { error: 'patch missing' });
      for (let i = 0; i < 8; i++) {
        const v = Number(await redis(['GET', kV])) || 0;
        const raw = v ? await redis(['GET', kW]) : null;
        const world = applyPatch(raw ? JSON.parse(raw) : {}, body.patch);
        const out = JSON.stringify(world);
        if (out.length > MAX_BYTES) return send(res, 413, { error: 'World too large' });
        const ok = await redis(['EVAL', CAS, '2', kV, kW, String(v), String(v + 1), out, String(TTL_SECONDS)]);
        if (ok === 1) return send(res, 200, { v: v + 1, world });
      }
      return send(res, 409, { error: 'Busy, try again' });
    }

    return send(res, 400, { error: 'Unknown op' });
  } catch (err) {
    console.error('world', space, err && err.message);   // no world contents in logs
    return send(res, 500, { error: 'Server error' });
  }
};

module.exports.applyPatch = applyPatch;   // for the local test
