// Unit tests for api/world.js with an in-memory Redis.
// Run: node --test tests/
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');

process.env.KV_REST_API_URL = 'http://fake';
process.env.KV_REST_API_TOKEN = 'fake';
const handler = require('../api/world.js');
const SyncCore = require('../api/_sync-core.js');

/* the four commands the function uses: GET, SET, EVAL (compare and set) */
function fakeRedis({ failFirstEvals = 0 } = {}) {
  const store = new Map();
  let fails = failFirstEvals;
  const fn = async (cmd) => {
    const [name] = cmd;
    if (name === 'GET') return store.has(cmd[1]) ? store.get(cmd[1]) : null;
    if (name === 'SET') { store.set(cmd[1], cmd[2]); return 'OK'; }
    if (name === 'EVAL') {
      const [, , , kV, kW, expect, next, raw] = cmd;
      if (fails > 0) { fails--; store.set(kV, String(Number(store.get(kV) || 0) + 1)); return 0; }
      if ((store.get(kV) || '0') !== expect) return 0;
      store.set(kW, raw); store.set(kV, next); return 1;
    }
    throw new Error('unexpected ' + name);
  };
  fn.store = store;
  return fn;
}

async function call(method, query, body) {
  const req = { method, query, body };
  const res = {
    statusCode: 0, headers: {}, body: null,
    setHeader(k, v) { this.headers[k] = v; },
    status(c) { this.statusCode = c; return this; },
    json(o) { this.body = o; return this; },
  };
  await handler(req, res);
  return res;
}

test('an unused world is empty', async () => {
  handler.redis(fakeRedis());
  const r = await call('GET', { space: 'main', v: '-1' });
  assert.equal(r.statusCode, 200);
  assert.deepEqual(r.body, { v: 0, world: null });
});

test('the first page to arrive creates the world; the second joins it', async () => {
  handler.redis(fakeRedis());
  const a = await call('POST', { space: 'main' }, { op: 'init', world: { who: 'first' } });
  const b = await call('POST', { space: 'main' }, { op: 'init', world: { who: 'second' } });
  assert.deepEqual(a.body, { v: 1, world: { who: 'first' } });
  assert.deepEqual(b.body, { v: 1, world: { who: 'first' } });
});

test('a tab that is up to date gets "same" instead of the whole world', async () => {
  handler.redis(fakeRedis());
  await call('POST', { space: 'main' }, { op: 'init', world: { x: 1 } });
  const r = await call('GET', { space: 'main', v: '1' });
  assert.deepEqual(r.body, { v: 1, same: true });
  assert.equal(r.headers['Cache-Control'], 'no-store');
});

test('field-level patches from two phones both land', async () => {
  handler.redis(fakeRedis());
  const base = { requests: [{ id: 'r1', review: 'waiting', seenBy: {} }] };
  await call('POST', { space: 'main' }, { op: 'init', world: base });
  const admin = JSON.parse(JSON.stringify(base)); admin.requests[0].review = 'passed';
  const shop = JSON.parse(JSON.stringify(base)); shop.requests[0].seenBy.aram = 5;
  await call('POST', { space: 'main' }, { op: 'patch', ops: SyncCore.diff(base, admin) });
  const r = await call('POST', { space: 'main' }, { op: 'patch', ops: SyncCore.diff(base, shop) });
  assert.equal(r.body.v, 3);
  assert.deepEqual(r.body.world.requests[0], { id: 'r1', review: 'passed', seenBy: { aram: 5 } });
});

test('a patch retries when another write lands between its read and its write', async () => {
  const redis = fakeRedis({ failFirstEvals: 2 });
  handler.redis(redis);
  const r = await call('POST', { space: 'main' }, { op: 'patch', ops: [{ p: ['a'], v: 1 }] });
  assert.equal(r.statusCode, 200);
  assert.equal(r.body.world.a, 1);
});

test('a tab from before the update (whole-record patch) still works', async () => {
  handler.redis(fakeRedis());
  await call('POST', { space: 'main' }, { op: 'init', world: { requests: [{ id: 'r1', t: 'a' }] } });
  const r = await call('POST', { space: 'main' }, { op: 'patch',
    patch: { requests: { t: 'list', up: [{ id: 'r1', t: 'b' }], rm: [] } } });
  assert.deepEqual(r.body.world.requests, [{ id: 'r1', t: 'b' }]);
});

test('start over replaces the world for everyone', async () => {
  handler.redis(fakeRedis());
  await call('POST', { space: 'main' }, { op: 'init', world: { requests: [1, 2, 3] } });
  const r = await call('POST', { space: 'main' }, { op: 'reset', world: { requests: [] } });
  assert.deepEqual(r.body, { v: 2, world: { requests: [] } });
});

test('worlds are separate', async () => {
  handler.redis(fakeRedis());
  await call('POST', { space: 'main' }, { op: 'init', world: { w: 'main' } });
  await call('POST', { space: 'class-a' }, { op: 'init', world: { w: 'class-a' } });
  assert.equal((await call('GET', { space: 'main', v: '-1' })).body.world.w, 'main');
  assert.equal((await call('GET', { space: 'class-a', v: '-1' })).body.world.w, 'class-a');
});

test('refuses bad input with a reason', async () => {
  handler.redis(fakeRedis());
  assert.equal((await call('GET', { space: '../etc' })).statusCode, 400);
  assert.equal((await call('POST', { space: 'main' }, { op: 'nope' })).statusCode, 400);
  assert.equal((await call('POST', { space: 'main' }, { op: 'patch' })).statusCode, 400);
  assert.equal((await call('POST', { space: 'main' }, { op: 'init' })).statusCode, 400);
  assert.equal((await call('PUT', { space: 'main' })).statusCode, 405);
  const many = Array.from({ length: 20001 }, (_, i) => ({ p: ['k' + i], v: i }));
  assert.equal((await call('POST', { space: 'main' }, { op: 'patch', ops: many })).statusCode, 413);
});

test('a database error is a 500 without the world in the message', async () => {
  handler.redis(async () => { throw new Error('boom'); });
  const r = await call('GET', { space: 'main', v: '0' });
  assert.equal(r.statusCode, 500);
  assert.deepEqual(r.body, { error: 'Server error' });
});
