// Unit tests for the merge rules of the shared test world.
// Run: node --test tests/
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const SyncCore = require('../api/_sync-core.js');

const ROOT = path.join(__dirname, '..');
const clone = (x) => JSON.parse(JSON.stringify(x));
const fixture = () => clone(require('./fixtures/world-main.json'));

/* Three phones, one server: each phone holds `base` (what the server last
   confirmed) and its own edited copy; the server applies each phone's ops in
   the order they arrive. This is exactly what the page and api/world.js do. */
function sendFrom(server, base, mine) {
  return SyncCore.apply(server, SyncCore.diff(base, mine));
}

test('the page carries an identical copy of the merge rules', () => {
  const grab = (file) => {
    const s = fs.readFileSync(path.join(ROOT, file), 'utf8');
    const a = s.indexOf('/* ==== sync-core:begin');
    const b = s.indexOf('/* ==== sync-core:end');
    assert.ok(a >= 0 && b > a, `markers missing in ${file}`);
    return s.slice(a, b).split('\n').map((l) => l.trim()).join('\n');
  };
  assert.equal(grab('prototype/shelfcall-all-roles.html'), grab('api/_sync-core.js'));
});

test('applying the diff of two worlds turns the first into the second', () => {
  const a = fixture();
  const b = fixture();
  b.requests[0].status = 'closed';
  b.requests.push({ id: 'r99-abcd', title: 'New', review: 'waiting', seenBy: {} });
  b.offers.splice(2, 1);
  b.sellers.aram.bio = 'Changed';
  delete b.sellers.nairi.avatar;
  b.ledger.push({ at: 1, amount: 500, from: 'buyer', to: 'courier', sub: '#1', note: 'x', pending: false });
  b.orders[0].subs[0].status = 'ready';
  b.seq.r = 100;
  const out = SyncCore.apply(a, SyncCore.diff(a, b));
  assert.deepEqual(out, b);
});

test('no change, no operations', () => {
  const a = fixture();
  assert.deepEqual(SyncCore.diff(a, clone(a)), []);
});

test('an approval survives a shop marking the same request as seen (the bug from 8 October)', () => {
  let server = fixture();
  const id = server.requests[0].id;
  server.requests[0].review = 'waiting';
  server.requests[0].seenBy = {};
  const shopBase = clone(server);              // the shop loaded before the approval

  const adminBase = clone(server);
  const admin = clone(server);
  admin.requests[0].review = 'passed';
  admin.requests[0].passedAt = 1000;
  server = sendFrom(server, adminBase, admin);

  const shop = clone(shopBase);                // stale: still says "waiting"
  shop.requests[0].seenBy.aram = 2000;
  server = sendFrom(server, shopBase, shop);

  const r = server.requests.find((x) => x.id === id);
  assert.equal(r.review, 'passed');
  assert.equal(r.passedAt, 1000);
  assert.equal(r.seenBy.aram, 2000);
});

test('two phones changing the same field: the later one wins', () => {
  let server = fixture();
  const base = clone(server);
  const a = clone(base); a.requests[1].title = 'From A';
  const b = clone(base); b.requests[1].title = 'From B';
  server = sendFrom(server, base, a);
  server = sendFrom(server, base, b);
  assert.equal(server.requests[1].title, 'From B');
});

test('two new requests made at the same time are both kept', () => {
  let server = fixture();
  const base = clone(server);
  const a = clone(base); a.requests.push({ id: 'r8-aaaa', title: 'A' });
  const b = clone(base); b.requests.push({ id: 'r8-bbbb', title: 'B' });
  server = sendFrom(server, base, a);
  server = sendFrom(server, base, b);
  const titles = server.requests.map((r) => r.title);
  assert.ok(titles.includes('A') && titles.includes('B'));
  assert.equal(server.requests.length, base.requests.length + 2);
});

test('a record deleted on one phone is not brought back by an edit on another', () => {
  let server = fixture();
  const base = clone(server);
  const id = base.offers[0].id;
  const a = clone(base); a.offers = a.offers.filter((o) => o.id !== id);
  const b = clone(base); b.offers[0].price = 1;
  server = sendFrom(server, base, a);
  server = sendFrom(server, base, b);
  assert.equal(server.offers.find((o) => o.id === id), undefined);
});

test('the shop and the courier changing two parts of one order both stick', () => {
  let server = fixture();
  const order = server.orders.find((o) => o.subs.length > 1) || server.orders[0];
  if (order.subs.length < 2) order.subs.push({ ...clone(order.subs[0]), no: order.id + '-B', status: 'placed' });
  order.subs[0].status = 'placed';
  order.subs[1].status = 'placed';
  const base = clone(server);
  const shop = clone(base);
  shop.orders.find((o) => o.id === order.id).subs[0].status = 'ready';
  const courier = clone(base);
  courier.orders.find((o) => o.id === order.id).subs[1].status = 'shipped';
  server = sendFrom(server, base, shop);
  server = sendFrom(server, base, courier);
  const subs = server.orders.find((o) => o.id === order.id).subs;
  assert.equal(subs[0].status, 'ready');
  assert.equal(subs[1].status, 'shipped');
});

test('log lines without ids are merged as a set: both added, none doubled', () => {
  let server = { ledger: [{ at: 1, amount: 1 }] };
  const base = clone(server);
  const a = clone(base); a.ledger.push({ at: 2, amount: 2 });
  const b = clone(base); b.ledger.push({ at: 3, amount: 3 });
  server = sendFrom(server, base, a);
  server = sendFrom(server, base, b);
  server = sendFrom(server, base, a);          // a retry must not double the line
  assert.deepEqual(server.ledger.map((x) => x.at).sort(), [1, 2, 3]);
});

test('operations are safe to apply twice (a retried request changes nothing)', () => {
  const a = fixture();
  const b = clone(a);
  b.requests[0].review = 'passed';
  b.cart = [{ id: b.offers[0].id }];
  b.ledger.push({ at: 9, amount: 9 });
  const ops = SyncCore.diff(a, b);
  assert.deepEqual(SyncCore.apply(SyncCore.apply(a, ops), ops), b);
});

test('a list emptied on one phone and filled on another', () => {
  let server = { cart: [{ id: 'o1' }] };
  const base = clone(server);
  const a = clone(base); a.cart = [];
  server = sendFrom(server, base, a);
  assert.deepEqual(server.cart, []);
  const base2 = clone(server);
  const b = clone(base2); b.cart.push({ id: 'o2' });
  server = sendFrom(server, base2, b);
  assert.deepEqual(server.cart, [{ id: 'o2' }]);
});

test('bad operations are ignored, not thrown', () => {
  const w = { a: { b: 1 }, list: [{ id: 1 }] };
  const out = SyncCore.apply(w, [
    null, {}, { p: [] }, { p: 'x' },
    { p: ['a', 'b', 'c'], v: 1 },               // through a number
    { p: ['list', { k: 'id', v: 7 }, 'x'], v: 1 },  // a record that is not there
    { p: ['a', { k: 'id', v: 1 }], v: 1 },      // keyed step into an object
  ]);
  assert.deepEqual(out, w);
});

test('a phone holding an older world keeps its unsent changes on top of the newer one', () => {
  // what syncTake does: newer server world + this phone's unsent ops
  const base = fixture();
  const mine = clone(base); mine.requests[2].title = 'mine';
  const server = clone(base); server.requests[3].title = 'theirs';
  const merged = SyncCore.apply(server, SyncCore.diff(base, mine));
  assert.equal(merged.requests[2].title, 'mine');
  assert.equal(merged.requests[3].title, 'theirs');
});

test('two readers reviewing the same shop at once: both reviews kept, newest on top everywhere', () => {
  let server = fixture();
  const shop = Object.keys(server.sellers)[0];
  server.sellers[shop].reviews = [{ by: 'Old', stars: 4, when: 'last week', text: '' }];
  const base = clone(server);
  const a = clone(base); a.sellers[shop].reviews.unshift({ by: 'Anna', stars: 5, when: 'just now', text: 'a' });
  const b = clone(base); b.sellers[shop].reviews.unshift({ by: 'Dina', stars: 3, when: 'just now', text: 'b' });
  server = sendFrom(server, base, a);
  server = sendFrom(server, base, b);
  const by = server.sellers[shop].reviews.map((r) => r.by);
  assert.deepEqual(by.sort(), ['Anna', 'Dina', 'Old']);
  assert.equal(server.sellers[shop].reviews[server.sellers[shop].reviews.length - 1].by, 'Old');
});

test('a new record put at the front of a list is at the front for everyone', () => {
  const a = { list: [{ id: 1 }, { id: 2 }] };
  const b = { list: [{ id: 0 }, { id: 1 }, { id: 2 }] };
  assert.deepEqual(SyncCore.apply(a, SyncCore.diff(a, b)), b);
});
