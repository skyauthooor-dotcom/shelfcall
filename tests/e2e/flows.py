#!/usr/bin/env python3
"""
End-to-end flows across roles, each role in its own browser (= its own phone),
all talking to one local copy of the server.

    python3 tests/e2e/flows.py            # needs: pip install playwright
                                           #        python -m playwright install chromium
    python3 tests/e2e/flows.py -k pickup   # only flows whose name contains "pickup"

It starts tests/tools/devserver.js (Node, no packages), which serves public/
the way Vercel does and runs api/world.js against an in-memory Redis. Build
first: python3 build/build.py.
"""
import asyncio, json, os, random, socket, subprocess, sys, time, traceback, urllib.request
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p


class Run:
    def __init__(self, base, browser):
        self.base, self.browser, self.pages = base, browser, []
        self.space = 'main'

    def own_world(self):
        """A world of this flow's own, seeded fresh, for flows that use the sample
        data and would otherwise depend on what earlier flows did to main."""
        self.space = 'flow%d' % random.randint(100000, 999999)
        return '?world=' + self.space

    async def phone(self, path, w=390, h=844):
        ctx = await self.browser.new_context(viewport={'width': w, 'height': h})
        await ctx.route('**/fonts.g*/**', lambda r: r.abort())
        pg = await ctx.new_page()
        pg.errors = []
        pg.on('pageerror', lambda e: pg.errors.append(str(e)[:300]))
        await pg.goto(self.base + path)
        await self.until(lambda: pg.evaluate('() => !!document.querySelector("main h1")'), 8, 'page did not load: ' + path)
        self.pages.append(pg)
        return pg

    def _settle(self, sid):
        return next(x for x in self.world()['settles'] if x['id'] == sid)

    def world(self, space=None):
        with urllib.request.urlopen('%s/api/world?space=%s&v=-1' % (self.base, space or self.space)) as r:
            return json.load(r)['world']

    async def until(self, fn, secs=10, msg='timed out'):
        end = time.time() + secs
        while time.time() < end:
            v = fn()
            if asyncio.iscoroutine(v): v = await v
            if v: return v
            await asyncio.sleep(0.25)
        raise AssertionError(msg)

    # ---- driving a page by its own buttons --------------------------------
    @staticmethod
    async def go(pg, screen, p=None):
        await pg.evaluate('''([s, p]) => { const b = document.createElement('button');
            b.setAttribute('data-go', s); if (p != null) b.setAttribute('data-p', p);
            document.body.appendChild(b); b.click(); b.remove(); }''', [screen, p])
        await pg.wait_for_timeout(250)

    @staticmethod
    async def acts(pg):
        return await pg.evaluate('''() => [...document.querySelectorAll('main [data-act], main [data-ask], #dock [data-act], #dock [data-ask], #sheet [data-act]')]
            .map(e => e.getAttribute('data-act') || 'ask:' + e.getAttribute('data-ask'))''')

    async def press(self, pg, prefix, required=True):
        """Press the first button whose action starts with prefix. A button that
        asks first (data-ask) opens the sheet, which is then confirmed, picking
        the first reason when one is required."""
        found = await pg.evaluate('''(pre) => {
            const el = [...document.querySelectorAll('[data-act], [data-ask]')].find(e =>
              (e.getAttribute('data-act') || '').startsWith(pre) || (e.getAttribute('data-ask') || '').startsWith(pre));
            if (!el) return null;
            el.click(); return el.getAttribute('data-act') ? 'act' : 'ask'; }''', prefix)
        if not found:
            if required: raise AssertionError('no "%s" button; on screen: %s' % (prefix, await self.acts(pg)))
            return False
        await pg.wait_for_timeout(250)
        if found == 'ask':
            await pg.evaluate('''() => { const r = document.querySelector('#sheet [data-act^="sheetreason"]'); if (r) r.click(); }''')
            await pg.wait_for_timeout(200)
            await pg.evaluate('''() => { const g = document.querySelector('#sheet [data-act="sheetgo"]'); if (g) g.click(); }''')
            await pg.wait_for_timeout(250)
        return True

    @staticmethod
    async def fill(pg, sel, value):
        await pg.fill(sel, value)

    @staticmethod
    async def text(pg):
        return await pg.inner_text('main') + '\n' + await pg.inner_text('#dock')

    # ---- the steps every flow reuses ---------------------------------------
    async def reader_asks(self, reader, title):
        await self.go(reader, 'r.new')
        await self.press(reader, 'kind:concrete')
        await reader.fill('#f_title', title)
        await reader.locator('#f_title').blur()
        await reader.locator('main .btn, #dock .btn').last.click(); await reader.wait_for_timeout(250)
        await self.press(reader, 'publish')
        return await self.until(lambda: next((r['id'] for r in self.world()['requests'] if r.get('title') == title), None),
                                8, 'the request never reached the server')

    async def admin_passes_request(self, admin, rid):
        await self.until(lambda: self._has(admin, 'requests', rid), 8, 'admin never received the request')
        await self.go(admin, 'a.req', rid)
        await self.press(admin, 'reqpass:' + rid)
        await self.until(lambda: self._req(rid).get('review') == 'passed', 8, 'approval did not reach the server')

    async def shop_offers(self, shop, rid, title, price='3500', photo=True):
        await self.until(lambda: self._has(shop, 'requests', rid), 8, 'shop never received the request')
        await self.go(shop, 's.newoffer', rid)
        for _ in range(12):
            acts = await self.acts(shop)
            if any(a.startswith('sendoffer') for a in acts):
                await self.press(shop, 'sendoffer'); break
            if photo and await shop.locator('#photoIn').count() and await shop.locator('main img').count() == 0:
                await shop.set_input_files('#photoIn', os.path.join(HERE, 'book.jpg')); await shop.wait_for_timeout(900); continue
            for sel, val in [('#o_title', title), ('#o_author', 'Test Author'), ('#o_price', price), ('#o_year', '1999')]:
                if await shop.locator(sel).count() and not await shop.locator(sel).input_value():
                    await shop.fill(sel, val)
            if await shop.locator('#o_cond').count():
                await shop.select_option('#o_cond', index=1)
            if 'loc:mash' in acts: await self.press(shop, 'loc:mash')
            if any(a.startswith('toreview') for a in acts):
                await self.press(shop, 'toreview'); continue
            nxt = await shop.evaluate('''() => { const b = [...document.querySelectorAll('main button.btn[data-act^="step:"], #dock button.btn[data-act^="step:"]')]
                .filter(b => !/ghost|link|back/.test(b.className)); return b.length ? b[b.length - 1].getAttribute('data-act') : null }''')
            if not nxt and not photo:
                nxt = 'step:1'
            if nxt: await self.press(shop, nxt)
        return await self.until(lambda: next((o['id'] for o in self.world()['offers'] if o.get('req') == rid), None),
                                8, 'the offer never reached the server')

    async def admin_passes_offer(self, admin, oid):
        await self.until(lambda: self._has(admin, 'offers', oid), 8, 'admin never received the offer')
        await self.go(admin, 'a.offer', oid)
        await self.press(admin, 'offpass:' + oid)
        await self.until(lambda: self._off(oid).get('review') == 'passed', 8, 'offer approval did not reach the server')

    async def reader_buys(self, reader, rid, oid, mode):
        """mode: 'pickup' or 'courier'. Returns the new order id."""
        before = {o['id'] for o in self.world()['orders']}
        await self.until(lambda: self._field(reader, 'offers', oid, 'review', 'passed'), 10,
                         'the reader never received the approved offer')
        await self.go(reader, 'r.request', rid)
        await self.press(reader, 'add:' + oid)
        await self.go(reader, 'r.cart')
        await self.press(reader, 'delall:' + mode, required=False)
        await self.press(reader, 'checkout')
        seen, chose_time = [], False
        for _ in range(12):
            acts = await self.acts(reader)
            seen.append(((await reader.inner_text('main h1')) if await reader.locator('main h1').count() else '?', acts[:8]))
            if 'place' in acts:
                await self.press(reader, 'place'); break
            for sel, val in [('#p_name', 'Dina'), ('#p_phone', '+374 91 22 33 44'), ('#p_addr', 'Komitas 24, apt 7')]:
                if await reader.locator(sel).count() and not await reader.locator(sel).input_value():
                    await reader.fill(sel, val)
            order_of_steps = ['donewhen', 'donedetails', 'toReview', 'review', 'next']
            if not chose_time: order_of_steps.insert(0, 'setwhen:')
            for a in order_of_steps:
                hit = next((x for x in acts if x.startswith(a)), None)
                if hit:
                    if a == 'setwhen:': chose_time = True
                    await self.press(reader, hit); break
            else:
                btn = reader.locator('#toReview')
                if await btn.count(): await btn.click(); await reader.wait_for_timeout(250)
        return await self.until(lambda: next((o['id'] for o in self.world()['orders'] if o['id'] not in before), None),
                                8, 'the order never reached the server; checkout went: %s' % seen)

    # ---- what a page holds right now ---------------------------------------
    def _req(self, rid): return next(r for r in self.world()['requests'] if r['id'] == rid)
    def _off(self, oid): return next(o for o in self.world()['offers'] if o['id'] == oid)
    def _ord(self, oid): return next(o for o in self.world()['orders'] if o['id'] == oid)

    async def _has(self, pg, kind, id_):
        """Has this page received the record yet? Read through the page's own
        sync state, so a flow waits for the poll instead of guessing."""
        return await pg.evaluate('([k, id]) => window.SC_DEBUG.has(k, id)', [kind, id_])

    async def _field(self, pg, kind, id_, field, value):
        rec = await pg.evaluate('([k, id]) => window.SC_DEBUG.get(k, id)', [kind, id_])
        return bool(rec) and rec.get(field) == value


# =============================== the flows ===================================
FLOWS = []
def flow(fn): FLOWS.append(fn); return fn


@flow
async def request_reaches_the_shop_after_approval(t):
    """Reader asks, admin approves, the shop - whose page has been open all
    along - sees it without touching anything, and the approval survives the
    shop's page marking the request as seen."""
    shop = await t.phone('/seller')
    shop_desktop = await t.phone('/seller', 1280, 800)
    reader = await t.phone('/reader'); admin = await t.phone('/admin')
    title = 'Flow A ' + str(random.randint(1000, 9999))
    rid = await t.reader_asks(reader, title)
    assert title not in await t.text(shop), 'the shop saw a request nobody had approved'
    await t.admin_passes_request(admin, rid)
    for pg in (shop, shop_desktop):
        await t.until(lambda pg=pg: _contains(pg, title), 10, 'the open shop page never showed the approved request')
    await asyncio.sleep(6)                      # the shop page re-renders and marks it seen
    r = t._req(rid)
    assert r['review'] == 'passed', 'approval was overwritten: %s' % r['review']
    assert 'aram' in (r.get('seenBy') or {}), 'the shop opening it was not recorded'


@flow
async def request_sent_back_never_reaches_the_shop(t):
    reader = await t.phone('/reader'); admin = await t.phone('/admin'); shop = await t.phone('/seller')
    title = 'Flow B ' + str(random.randint(1000, 9999))
    rid = await t.reader_asks(reader, title)
    await t.until(lambda: t._has(admin, 'requests', rid), 8)
    await t.go(admin, 'a.req', rid)
    await t.press(admin, 'apreset:0')
    await t.press(admin, 'reqback:' + rid)
    await t.until(lambda: t._req(rid).get('review') == 'sent back', 8, 'send-back did not reach the server')
    assert t._req(rid).get('reviewWhy'), 'sent back without a reason'
    await t.go(reader, 'r.request', rid)
    await t.until(lambda: _contains(reader, t._req(rid)['reviewWhy'][:20]), 10, 'the reader never saw why it came back')
    await t.go(shop, 's.feed')
    await asyncio.sleep(4)
    assert title not in await t.text(shop), 'a sent-back request reached the shop'


@flow
async def offer_with_photo_reaches_the_reader_and_seen_reaches_the_shop(t):
    reader = await t.phone('/reader'); admin = await t.phone('/admin'); shop = await t.phone('/seller')
    title = 'Flow C ' + str(random.randint(1000, 9999))
    rid = await t.reader_asks(reader, title)
    await t.admin_passes_request(admin, rid)
    oid = await t.shop_offers(shop, rid, title)
    assert t._off(oid)['review'] == 'waiting'
    await t.go(reader, 'r.request', rid)
    await asyncio.sleep(4)
    assert not await reader.locator('[data-p="%s"]' % oid).count(), 'the reader saw an offer nobody had approved'
    await t.admin_passes_offer(admin, oid)
    await t.until(lambda: reader.locator('[data-p="%s"]' % oid).count(), 10, 'the offer never appeared for the reader')
    src = await reader.evaluate('() => { const i = document.querySelector("main img"); return i ? i.src.slice(0, 22) : null }')
    assert src == 'data:image/jpeg;base64', 'the photo did not travel: %s' % src
    await t.go(reader, 'r.offer', oid)
    await t.until(lambda: t._off(oid)['status'] == 'seen', 8, 'opening the offer did not mark it seen')
    await t.go(shop, 's.offers')
    await t.until(lambda: _contains(shop, title), 10, 'the shop does not list its own offer')


@flow
async def offer_sent_back_reaches_the_shop_not_the_reader(t):
    reader = await t.phone('/reader'); admin = await t.phone('/admin'); shop = await t.phone('/seller')
    title = 'Flow D ' + str(random.randint(1000, 9999))
    rid = await t.reader_asks(reader, title)
    await t.admin_passes_request(admin, rid)
    oid = await t.shop_offers(shop, rid, title)
    await t.until(lambda: t._has(admin, 'offers', oid), 8)
    await t.go(admin, 'a.offer', oid)
    await t.press(admin, 'apreset:0')
    await t.press(admin, 'offback:' + oid)
    await t.until(lambda: t._off(oid).get('review') == 'sent back', 8, 'offer send-back did not reach the server')
    await t.go(reader, 'r.request', rid)
    await asyncio.sleep(4)
    assert not await reader.locator('[data-p="%s"]' % oid).count(), 'a sent-back offer reached the reader'


@flow
async def pickup_order_from_cart_to_review(t):
    reader = await t.phone('/reader'); admin = await t.phone('/admin'); shop = await t.phone('/seller')
    title = 'Flow E ' + str(random.randint(1000, 9999))
    rid = await t.reader_asks(reader, title)
    await t.admin_passes_request(admin, rid)
    oid = await t.shop_offers(shop, rid, title)
    await t.admin_passes_offer(admin, oid)
    ordid = await t.reader_buys(reader, rid, oid, 'pickup')
    order = t._ord(ordid)
    sub = order['subs'][0]
    assert sub['delivery'] == 'pickup' and sub['status'] == 'placed', sub
    assert sub.get('code'), 'a pickup order has no handover code'
    # the shop sees the order and marks it ready
    await t.until(lambda: t._has(shop, 'orders', ordid), 10, 'the shop never received the order')
    await t.go(shop, 's.order', sub['no'])
    await t.press(shop, 'ready:%s:%s' % (ordid, sub['no']))
    await t.until(lambda: t._ord(ordid)['subs'][0]['status'] == 'shipped', 8, '"ready for pickup" did not reach the server')
    # the reader sees it is ready, comes to the shop, the shop types the code
    await t.go(reader, 'r.orders')
    await t.until(lambda: _contains(reader, sub['code']), 10, 'the reader never saw the handover code')
    await t.go(shop, 's.order', sub['no'])
    await shop.fill('#code_' + sub['no'], sub['code'])
    await t.press(shop, 'entercode:%s:%s' % (ordid, sub['no']))
    await t.until(lambda: t._ord(ordid)['subs'][0]['status'] == 'completed', 8, 'the handover did not complete')
    # the reader is asked to rate, and the shop gets the review
    await t.until(lambda: t._has(reader, 'orders', ordid), 8)
    await reader.evaluate('''([id, no]) => { const b = document.createElement('button'); b.setAttribute('data-act', 'rate:' + id + ':' + no);
        document.body.appendChild(b); b.click(); b.remove(); }''', [str(ordid), sub['no']])
    await reader.wait_for_timeout(300)
    await t.press(reader, 'star:5')
    await t.press(reader, 'postreview')
    await t.until(lambda: any(r.get('stars') == 5 and r.get('by') == 'Dina' for r in t.world()['sellers'][sub['seller']]['reviews']),
                  8, 'the review never reached the shop')


@flow
async def courier_order_from_cart_to_cash(t):
    reader = await t.phone('/reader'); admin = await t.phone('/admin')
    shop = await t.phone('/seller'); courier = await t.phone('/courier')
    title = 'Flow F ' + str(random.randint(1000, 9999))
    rid = await t.reader_asks(reader, title)
    await t.admin_passes_request(admin, rid)
    oid = await t.shop_offers(shop, rid, title)
    await t.admin_passes_offer(admin, oid)
    ordid = await t.reader_buys(reader, rid, oid, 'courier')
    sub = t._ord(ordid)['subs'][0]
    assert sub['delivery'] == 'courier', sub
    await t.until(lambda: t._has(shop, 'orders', ordid), 10, 'the shop never received the order')
    await t.go(shop, 's.order', sub['no'])
    await t.press(shop, 'ready:%s:%s' % (ordid, sub['no']))
    await t.until(lambda: t._ord(ordid)['subs'][0]['status'] == 'ready', 8, '"ready for delivery" did not reach the server')
    # the courier sees the job, collects, delivers and takes the cash
    await t.until(lambda: t._has(courier, 'orders', ordid), 10)
    await t.go(courier, 'c.jobs')
    await t.until(lambda: _contains(courier, '#%s' % ordid) or _contains(courier, str(ordid)), 10, 'the courier never saw the job')
    await t.go(courier, 'c.job', sub['no'])
    await t.press(courier, 'ccollect:%s:%s' % (ordid, sub['no']))
    await t.until(lambda: t._ord(ordid)['subs'][0]['status'] == 'shipped', 8, 'collection did not reach the server')
    await t.go(reader, 'r.orders')
    await t.until(lambda: _contains(reader, 'on the way') or _contains(reader, 'On the way'), 10, 'the reader was not told it is on the way')
    await t.go(courier, 'c.job', sub['no'])
    await t.press(courier, 'cdeliverorder:%s' % ordid)
    await t.until(lambda: t._ord(ordid)['subs'][0]['status'] == 'completed', 8, 'delivery did not reach the server')
    took = t._ord(ordid)['books'] + t._ord(ordid)['fee']
    assert any(l.get('sub') == '#%s' % ordid and l.get('amount') == took for l in t.world()['ledger']), 'the cash was not recorded'


@flow
async def closing_a_request_takes_it_out_of_the_feed(t):
    reader = await t.phone('/reader'); admin = await t.phone('/admin'); shop = await t.phone('/seller')
    title = 'Flow G ' + str(random.randint(1000, 9999))
    rid = await t.reader_asks(reader, title)
    await t.admin_passes_request(admin, rid)
    await t.go(shop, 's.feed')
    await t.until(lambda: _contains(shop, title), 10, 'the shop never saw the request')
    await t.go(reader, 'r.request', rid)
    await t.press(reader, 'closereq:' + rid)
    await t.until(lambda: t._req(rid)['status'] == 'closed', 8, 'closing did not reach the server')
    await t.until(lambda: _not_contains(shop, title), 10, 'the closed request stayed in the shop feed')


@flow
async def two_phones_at_once_and_typing_is_safe(t):
    a = await t.phone('/all-roles'); b = await t.phone('/reader')
    ta, tb = 'Race A ' + str(random.randint(1000, 9999)), 'Race B ' + str(random.randint(1000, 9999))
    await asyncio.gather(t.reader_asks(a, ta), t.reader_asks(b, tb))
    titles = [r.get('title') for r in t.world()['requests']]
    assert ta in titles and tb in titles, 'one of two simultaneous requests was lost'
    await t.go(a, 'r.new'); await t.press(a, 'kind:concrete')
    await a.click('#f_title'); await a.type('#f_title', 'Half typ')
    await t.reader_asks(b, 'Race C ' + str(random.randint(1000, 9999)))
    await asyncio.sleep(4)
    assert await a.input_value('#f_title') == 'Half typ', 'an update wiped what was being typed'
    assert await a.evaluate('() => document.activeElement.id') == 'f_title', 'an update stole the focus'


@flow
async def start_over_and_separate_worlds(t):
    a = await t.phone('/reader'); b = await t.phone('/all-roles')
    title = 'Reset ' + str(random.randint(1000, 9999))
    await t.reader_asks(a, title)
    e = await t.phone('/empty')
    assert t.world('empty')['requests'] == [], 'the empty world is not empty'
    assert title not in await t.text(e)
    g = await t.phone('/reader?world=group-x')
    assert not any(r.get('title') == title for r in t.world('group-x')['requests']), 'a ?world= leaked the main world'
    await t.press(b, 'worldreset')
    await t.until(lambda: not any(r.get('title') == title for r in t.world()['requests']), 8, 'start over did not clear the world')
    await t.go(a, 'r.requests')
    await t.until(lambda: _not_contains(a, title), 10, 'another phone still showed the cleared request')


@flow
async def pages_run_offline_without_the_server(t):
    ctx = await t.browser.new_context(viewport={'width': 390, 'height': 844})
    await ctx.route('**/fonts.g*/**', lambda r: r.abort())
    pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    for name in ['all-roles', 'reader', 'seller', 'courier', 'admin', 'empty']:
        await pg.goto('file://' + os.path.join(ROOT, 'public', name + '.html'))
        await pg.wait_for_timeout(700)
        assert await pg.locator('main h1').count(), name + ' did not render from disk'
        assert 'test it' in (await pg.inner_text('#proto')).lower(), name + ' did not fall back to this-tab-only'
    assert not errs, errs


@flow
async def reader_cancels_an_order_and_the_shop_sees_it(t):
    reader = await t.phone('/reader'); admin = await t.phone('/admin'); shop = await t.phone('/seller')
    title = 'Flow H ' + str(random.randint(1000, 9999))
    rid = await t.reader_asks(reader, title)
    await t.admin_passes_request(admin, rid)
    oid = await t.shop_offers(shop, rid, title)
    await t.admin_passes_offer(admin, oid)
    ordid = await t.reader_buys(reader, rid, oid, 'pickup')
    sub = t._ord(ordid)['subs'][0]
    await t.until(lambda: t._has(reader, 'orders', ordid), 8)
    await t.go(reader, 'r.orders')
    await reader.evaluate("""([id, no]) => { const b = document.createElement('button'); b.setAttribute('data-act', 'cancel:' + id + ':' + no);
        document.body.appendChild(b); b.click(); b.remove(); }""", [str(ordid), sub['no']])
    await t.until(lambda: t._ord(ordid)['subs'][0]['status'] != 'placed', 8, 'the cancellation did not reach the server')
    await t.until(lambda: t._req(rid)['status'] == 'open', 8, 'the request did not open again after cancelling')
    await t.until(lambda: t._field(shop, 'orders', ordid, 'id', ordid), 8)
    shop_sub = (await shop.evaluate('([id]) => window.SC_DEBUG.get("orders", id)', [ordid]))['subs'][0]
    assert shop_sub['status'] != 'placed', 'the shop still thinks the order is live'


@flow
async def shop_removes_its_offer_and_the_reader_cannot_buy_it(t):
    reader = await t.phone('/reader'); admin = await t.phone('/admin'); shop = await t.phone('/seller')
    title = 'Flow I ' + str(random.randint(1000, 9999))
    rid = await t.reader_asks(reader, title)
    await t.admin_passes_request(admin, rid)
    oid = await t.shop_offers(shop, rid, title)
    await t.admin_passes_offer(admin, oid)
    await t.go(reader, 'r.request', rid)
    await t.until(lambda: reader.locator('[data-p="%s"]' % oid).count(), 10, 'the reader never saw the offer')
    await shop.evaluate("""(id) => { const b = document.createElement('button'); b.setAttribute('data-act', 'removeoffer:' + id);
        document.body.appendChild(b); b.click(); b.remove(); }""", oid)
    await t.until(lambda: t._off(oid)['status'] == 'removed', 8, 'removing did not reach the server')
    # by design the reader keeps seeing it, crossed out, and cannot buy it
    await t.until(lambda: t._field(reader, 'offers', oid, 'status', 'removed'), 10, 'the reader never heard it was removed')
    await t.go(reader, 'r.request', rid)
    assert await reader.locator('[data-act="add:%s"]' % oid).count() == 0, 'a removed offer can still be added to the cart'
    await t.go(reader, 'r.offer', oid)
    assert 'removed this offer' in await t.text(reader), 'the offer page does not say it was removed'


@flow
async def courier_cannot_deliver_and_the_order_unwinds(t):
    reader = await t.phone('/reader'); admin = await t.phone('/admin')
    shop = await t.phone('/seller'); courier = await t.phone('/courier')
    title = 'Flow K ' + str(random.randint(1000, 9999))
    rid = await t.reader_asks(reader, title)
    await t.admin_passes_request(admin, rid)
    oid = await t.shop_offers(shop, rid, title)
    await t.admin_passes_offer(admin, oid)
    ordid = await t.reader_buys(reader, rid, oid, 'courier')
    sub = t._ord(ordid)['subs'][0]
    await t.until(lambda: t._has(shop, 'orders', ordid), 10)
    await t.go(shop, 's.order', sub['no'])
    await t.press(shop, 'ready:%s:%s' % (ordid, sub['no']))
    await t.until(lambda: t._field(courier, 'orders', ordid, 'id', ordid), 10)
    await t.until(lambda: courier.evaluate('([id]) => window.SC_DEBUG.get("orders", id).subs[0].status === "ready"', [ordid]), 10)
    await t.go(courier, 'c.job', sub['no'])
    await t.press(courier, 'ccollect:%s:%s' % (ordid, sub['no']))
    await t.until(lambda: t._ord(ordid)['subs'][0]['status'] == 'shipped', 8)
    await courier.evaluate("""([id]) => { const b = document.createElement('button'); b.setAttribute('data-act', 'cfailorder:' + id);
        document.body.appendChild(b); b.click(); b.remove(); }""", [str(ordid)])
    await t.until(lambda: t._ord(ordid)['subs'][0]['status'] not in ('ready', 'shipped'), 8, 'the failed delivery did not reach the server')
    await t.go(reader, 'r.orders')
    await t.until(lambda: reader.evaluate('([id]) => { const o = window.SC_DEBUG.get("orders", id); return o && !["ready","shipped"].includes(o.subs[0].status) }', [ordid]),
                  10, 'the reader still sees the order as on its way')


async def _gone(pg, sel):
    return await pg.locator(sel).count() == 0


@flow
async def a_shop_tab_left_in_the_background_still_gets_the_request(t):
    """A laptop with the reader's tab in front: the shop's tab is hidden, and
    still has the approved request when the shop comes back to it."""
    shop = await t.phone('/seller')
    await shop.evaluate("""() => { Object.defineProperty(document, 'hidden', { get: () => true, configurable: true });
        Object.defineProperty(document, 'visibilityState', { get: () => 'hidden', configurable: true }); }""")
    reader = await t.phone('/reader'); admin = await t.phone('/admin')
    title = 'Flow L ' + str(random.randint(1000, 9999))
    rid = await t.reader_asks(reader, title)
    await t.admin_passes_request(admin, rid)
    await t.until(lambda: t._field(shop, 'requests', rid, 'review', 'passed'), 25,
                  'a hidden shop tab never received the approved request')
    await t.until(lambda: _contains(shop, title), 5, 'the hidden shop tab received it but did not show it')


@flow
async def courier_pays_the_shop_and_both_screens_change(t):
    w = t.own_world()
    courier = await t.phone('/courier' + w); shop = await t.phone('/seller' + w)
    await t.go(shop, 's.feed')
    await t.go(courier, 'c.done')
    await t.press(courier, 'csettlestart:aram')
    st = await t.until(lambda: next((x for x in t.world().get('settles', []) if x['seller'] == 'aram' and x['state'] == 'open'), None),
                       8, 'the handover never reached the server')
    # the shop, on another screen, is told: a badge on Billing and a notification
    await t.until(lambda: shop.evaluate('() => !!document.querySelector(\'#tabbar [data-go="s.billing"] .count\')'), 10,
                  'the shop tab bar never showed the handover')
    await t.go(shop, 's.billing')
    await t.until(lambda: _contains(shop, 'is handing you'), 10, 'the shop billing page never showed the handover')
    # the code is the shop's: it is on the shop's screen, not the courier's
    assert await _contains(shop, st['code']), 'the shop does not show the code to give'
    assert not await _contains(courier, st['code']), 'the courier can see the code without asking the shop'
    wrong = '1111' if st['code'] != '1111' else '2222'
    await courier.fill('#c_code', wrong)
    await t.press(courier, 'csettledone:' + st['id'])
    assert await _contains(courier, 'not the code'), 'a wrong code was accepted'
    assert t._settle(st['id'])['state'] == 'open'
    await courier.fill('#c_code', st['code'])
    await t.press(courier, 'csettledone:' + st['id'])
    await t.until(lambda: t._settle(st['id'])['state'] == 'done', 8, 'the confirmed handover did not reach the server')
    led = [l for l in t.world()['ledger'] if l.get('from') == 'courier' and l.get('to') == 'shop' and l.get('sub') in st['subs']]
    assert sum(l['amount'] for l in led) == st['amount'], (led, st)
    # the shop's screen, untouched, drops the code once the courier has typed it
    await t.until(lambda: _not_contains(shop, 'is handing you'), 10, 'the shop still shows the handover after it was recorded')
    await t.until(lambda: courier.evaluate('() => !document.querySelector(\'[data-act="csettlestart:aram"]\')'), 5,
                  'the courier is offered to hand over the same money again')


@flow
async def a_handover_where_the_counts_differ_records_no_money(t):
    w = t.own_world()
    courier = await t.phone('/courier' + w); shop = await t.phone('/seller' + w)
    await t.go(shop, 's.billing')
    before = len(t.world()['ledger'])
    await t.go(courier, 'c.done')
    await t.press(courier, 'csettlestart:aram')
    st = await t.until(lambda: next((x for x in t.world().get('settles', []) if x['seller'] == 'aram' and x['state'] == 'open'), None), 8)
    await t.until(lambda: _contains(shop, 'is handing you'), 10, 'the open billing page never showed the handover')
    await shop.fill('#cash_got', str(st['amount'] - 1000))
    await t.press(shop, 'cashodd:' + st['id'])
    await t.until(lambda: t._settle(st['id'])['state'] == 'mismatch', 8, 'the disagreement did not reach the server')
    assert len(t.world()['ledger']) == before, 'money was recorded for a disputed handover'
    await t.until(lambda: courier.evaluate("() => !document.querySelector('#c_code')"), 10, 'the courier still has the code box open')
    await t.until(lambda: _contains(courier, 'The office has both numbers'), 10, 'the courier was not told the counts differ')
    # and a cancelled one, from the courier's side, disappears from the shop
    await t.press(courier, 'csettlestart:aram')
    st2 = await t.until(lambda: next((x for x in t.world().get('settles', []) if x['seller'] == 'aram' and x['state'] == 'open'), None), 8)
    await t.until(lambda: _contains(shop, 'is handing you'), 10)
    await t.press(courier, 'csettlestop:' + st2['id'])
    await t.until(lambda: _not_contains(shop, 'is handing you'), 10, 'a cancelled handover stayed on the shop page')


@flow
async def the_main_button_stays_at_the_bottom_of_the_phone(t):
    w = t.own_world()
    reader = await t.phone('/reader' + w, h=844)
    async def dock(pg):
        return await pg.evaluate("""() => { const d = document.getElementById('dock'), b = d.querySelector('.btn'),
            tb = document.getElementById('tabbar'); if (!b || !d.classList.contains('on')) return null;
            const r = b.getBoundingClientRect(), tr = tb && getComputedStyle(tb).display !== 'none' && !tb.hidden ? tb.getBoundingClientRect() : null;
            return { text: b.innerText, bottom: Math.round(r.bottom), top: Math.round(r.top), tab: tr ? Math.round(tr.top) : null, vh: innerHeight }; }""")
    await t.go(reader, 'r.requests')
    a = await dock(reader)
    assert a and a['text'] == 'Ask for a book', a
    assert a['tab'] and a['bottom'] <= a['tab'] and a['tab'] - a['bottom'] < 24, ('not just above the tab bar', a)
    await reader.mouse.wheel(0, 800); await reader.wait_for_timeout(200)
    assert (await dock(reader))['top'] == a['top'], 'the button moved when the page scrolled'
    # a flow screen has no tab bar: the button sits at the bottom edge
    await t.go(reader, 'r.request', 'r2')
    await t.press(reader, 'add:')
    await t.go(reader, 'r.cart'); await t.press(reader, 'checkout')
    c = await dock(reader)
    assert c and c['tab'] is None and c['vh'] - c['bottom'] < 24, c
    # a tall phone: same place relative to the bottom, not halfway up
    tall = await t.phone('/reader' + w, h=1100)
    await t.go(tall, 'r.requests')
    b = await dock(tall)
    assert b['vh'] - b['bottom'] == a['vh'] - a['bottom'], (a, b)
    # nothing hides under the dock: the end of the page scrolls clear of it
    await tall.evaluate('() => window.scrollTo(0, document.body.scrollHeight)'); await tall.wait_for_timeout(150)
    last = await tall.evaluate("() => Math.round(document.querySelector('main').lastElementChild.getBoundingClientRect().bottom)")
    assert last <= b['top'], ('content ends under the button', last, b)


@flow
async def offer_card_opens_the_book_and_buy_goes_to_checkout(t):
    reader = await t.phone('/reader' + t.own_world())
    await t.go(reader, 'r.request', 'r2')
    acts = await t.acts(reader)
    buy = next(a for a in acts if a.startswith('buy:'))
    oid = buy.split(':')[1]
    assert await reader.evaluate("(o) => document.querySelector('[data-act=\"buy:' + o + '\"]').innerText.trim()", oid) == 'Buy'
    await reader.evaluate("() => document.querySelector('.row.tap .grow, .row.tap h3, .row.tap').click()")
    await reader.wait_for_timeout(250)
    assert await reader.evaluate('() => SC_DEBUG.screen()') == 'r.offer', 'tapping the card did not open the book'
    await t.go(reader, 'r.request', 'r2')
    await t.press(reader, 'buy:' + oid)
    scr = await reader.evaluate('() => SC_DEBUG.screen()')
    assert scr != 'r.request' and scr != 'r.offer', 'Buy did not move on to checkout: ' + scr


@flow
async def the_reader_sees_their_own_phone_when_editing(t):
    reader = await t.phone('/reader' + t.own_world())
    await t.go(reader, 'x.settings')
    v = await reader.input_value('#p_phone')
    assert v and '*' not in v and sum(ch.isdigit() for ch in v) >= 11, v


@flow
async def reader_edits_a_sent_back_request_and_it_goes_to_the_office_again(t):
    reader = await t.phone('/reader'); admin = await t.phone('/admin')
    title = 'Flow R ' + str(random.randint(1000, 9999))
    rid = await t.reader_asks(reader, title)
    await t.until(lambda: t._has(admin, 'requests', rid), 8)
    await t.go(admin, 'a.req', rid)
    await t.press(admin, 'apreset:0')
    await t.press(admin, 'reqback:' + rid)
    await t.until(lambda: t._req(rid).get('review') == 'sent back', 8)
    await t.until(lambda: t._field(reader, 'requests', rid, 'review', 'sent back'), 10)
    await t.go(reader, 'r.request', rid)
    await t.press(reader, 'editreq:' + rid)
    assert await reader.input_value('#f_title') == title, 'the edit form did not open with the request in it'
    await reader.fill('#f_title', title + ' fixed'); await reader.locator('#f_title').blur()
    await t.press(reader, 'rstep:3')
    await t.press(reader, 'publish')
    await t.until(lambda: t._req(rid).get('review') == 'waiting' and t._req(rid).get('title') == title + ' fixed', 8,
                  'the edited request did not go back to the office')
    assert sum(1 for r in t.world()['requests'] if (r.get('title') or '').startswith(title)) == 1, 'editing made a second request'
    await t.until(lambda: t._field(admin, 'requests', rid, 'review', 'waiting'), 10, 'the office never saw it come back')


@flow
async def shop_answers_a_review_and_the_reader_sees_it(t):
    w = t.own_world()
    shop = await t.phone('/seller' + w); reader = await t.phone('/reader' + w)
    await t.go(shop, 's.reviews')
    await t.press(shop, 'revopen:0')
    await shop.fill('#rp_text', 'Thank you, Dina')
    await t.press(shop, 'revpost:0')
    await t.until(lambda: any((v.get('reply') or {}).get('text') == 'Thank you, Dina' for v in t.world()['sellers']['aram']['reviews']), 8,
                  'the answer did not reach the server')
    await t.go(reader, 'r.seller', 'aram')
    await t.until(lambda: _contains(reader, 'Thank you, Dina'), 10, 'the reader never saw the answer')


@flow
async def office_opens_a_shop_and_a_second_phone_answers_as_it(t):
    w = t.own_world()
    admin = await t.phone('/admin' + w); shop2 = await t.phone('/seller' + w); reader = await t.phone('/reader' + w)
    await t.go(admin, 'a.newshop')
    await admin.fill('#ns_name', 'Flow Shop'); await admin.fill('#ns_email', 'flow@example.am')
    await t.press(admin, 'nsstep:2')
    await admin.fill('#ns_addr', 'Abovyan 3')
    await t.press(admin, 'opsnewshop')
    sid = await t.until(lambda: next((k for k, v in t.world()['sellers'].items() if v.get('name') == 'Flow Shop'), None), 8,
                        'the new shop did not reach the server')
    await t.go(shop2, 'x.settings')
    await t.until(lambda: shop2.evaluate("(k) => !!document.querySelector('#shopSel option[value=\"' + k + '\"]')", sid), 10,
                  'the second phone cannot pick the new shop')
    await shop2.select_option('#shopSel', sid); await shop2.wait_for_timeout(300)
    title = 'Flow S ' + str(random.randint(1000, 9999))
    rid = await t.reader_asks(reader, title)
    await t.admin_passes_request(admin, rid)
    oid = await t.shop_offers(shop2, rid, title)
    assert t._off(oid)['seller'] == sid, 'the offer was sent as the wrong shop'
    # and after a reload the phone is still that shop
    await shop2.reload(); await shop2.wait_for_timeout(1500)
    await t.go(shop2, 'x.settings')
    assert await shop2.input_value('#shopSel') == sid


@flow
async def shop_registers_and_the_office_opens_it(t):
    w = t.own_world()
    shop = await t.phone('/seller' + w); admin = await t.phone('/admin' + w)
    await t.go(shop, 'x.settings')
    await t.press(shop, 'newshop')
    await shop.fill('#g_shop', 'Reg Shop'); await t.press(shop, 'gstep:2')
    await shop.fill('#g_bio', 'Old maps and atlases.'); await t.press(shop, 'gstep:3')
    await shop.fill('#g_label', 'Stall'); await shop.fill('#g_addr', 'Tumanyan 5'); await shop.fill('#g_hours', 'Sat 11-19')
    await t.press(shop, 'gstep:4')
    await t.press(shop, 'finishreg')
    ap = await t.until(lambda: next((a for a in t.world()['shopApps'] if a.get('name') == 'Reg Shop'), None), 8, 'the application never reached the office')
    assert t.world()['sellers'][ap['owner']].get('pending'), 'a shop that is not checked yet is already open'
    await t.until(lambda: _contains(shop, 'checking'), 8)
    await t.until(lambda: t._has(admin, 'shopApps', ap['id']), 10)
    await t.go(admin, 'a.app', ap['id'])
    await t.press(admin, 'aset:dec:open')
    await t.press(admin, 'shopopen:' + ap['id'])
    await t.until(lambda: not t.world()['sellers'][ap['owner']].get('pending'), 8, 'opening did not reach the server')
    await t.until(lambda: t._field(shop, 'shopApps', ap['id'], 'state', 'open'), 10, 'the shop phone never heard it was opened')
    await t.go(shop, 's.feed')
    assert await shop.evaluate("() => SC_DEBUG.screen()") == 's.feed', 'the opened shop is still held on its application'


@flow
async def shop_pays_its_commission_with_a_receipt_photo(t):
    w = t.own_world()
    shop = await t.phone('/seller' + w); admin = await t.phone('/admin' + w)
    await t.go(shop, 's.billing')
    await t.press(shop, 'setstate:due')
    await t.go(shop, 's.pay')
    assert await _contains(shop, '1570 0453 2189 0100'), 'the bank account is not shown in full'
    await t.press(shop, 'sendclaim')
    assert await _contains(shop, 'photo of the receipt'), 'a claim without a receipt was accepted'
    await shop.set_input_files('#rcptIn', os.path.join(HERE, 'book.jpg')); await shop.wait_for_timeout(900)
    await t.press(shop, 'sendclaim')
    await t.until(lambda: (t.world()['account'].get('claim') or {}).get('photo', '').startswith('data:image'), 8, 'the claim with its photo did not reach the server')
    await t.go(admin, 'a.claim', 'aram')
    await t.until(lambda: admin.evaluate("() => !!document.querySelector('main img.thumb')"), 10, 'the office does not see the receipt')
    await admin.fill('#op_why', 'Found it')
    await t.press(admin, 'opsclaimok')
    await t.until(lambda: not t.world()['account'].get('claim') and t.world()['account']['state'] == 'good', 8)


@flow
async def billing_counts_every_order_on_the_day_it_was_placed(t):
    w = t.own_world()
    shop = await t.phone('/seller' + w)
    await t.go(shop, 's.billing')
    assert not await shop.evaluate("() => !!document.querySelector('[data-act=\"aset:bd:14\"]')"), 'the 14/30 day chips are back'
    assert await shop.evaluate("() => !!document.querySelector('.chart.bare svg')"), 'no chart'
    assert await shop.evaluate("() => !document.querySelector('.chart.bare .grid')"), 'the chart has grid lines'
    # the headline is every order of this period, paid or not, by order day
    assert await _contains(shop, 'still coming') or await _contains(shop, 'all in your till')
    await t.press(shop, 'earn:all')
    assert await _contains(shop, 'All periods together')
    assert not await shop.evaluate("() => [...document.querySelectorAll('#tabbar [data-go]')].some(b => b.getAttribute('data-go') === 's.stats')"), 'Results is still in the tab bar'


async def _contains(pg, s):
    return s in await Run.text(pg)


async def _not_contains(pg, s):
    return s not in await Run.text(pg)


# ================================ runner =====================================
async def main(only):
    if not os.path.exists(os.path.join(HERE, 'book.jpg')):
        sys.exit('tests/e2e/book.jpg is missing')
    port = free_port()
    srv = subprocess.Popen(['node', os.path.join(ROOT, 'tests', 'tools', 'devserver.js'), ROOT, str(port)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = 'http://127.0.0.1:%d' % port
    try:
        for _ in range(40):
            try: urllib.request.urlopen(base + '/api/world?space=main&v=0'); break
            except Exception: time.sleep(0.1)
        results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            for fn in FLOWS:
                if only and only not in fn.__name__: continue
                t = Run(base, browser)
                started = time.time()
                try:
                    await fn(t)
                    errs = [e for pg in t.pages for e in pg.errors]
                    if errs: raise AssertionError('page errors: %s' % errs[:3])
                    results.append((fn.__name__, None, time.time() - started))
                    print('PASS  %-62s %5.1fs' % (fn.__name__, time.time() - started))
                except Exception as e:
                    results.append((fn.__name__, e, time.time() - started))
                    print('FAIL  %-62s %5.1fs\n      %s' % (fn.__name__, time.time() - started,
                          (str(e) or traceback.format_exc().splitlines()[-1])[:400]))
                for pg in t.pages:
                    await pg.context.close()
            await browser.close()
        bad = [r for r in results if r[1]]
        print('\n%d passed, %d failed' % (len(results) - len(bad), len(bad)))
        return 1 if bad else 0
    finally:
        srv.terminate()


if __name__ == '__main__':
    only = sys.argv[sys.argv.index('-k') + 1] if '-k' in sys.argv else None
    sys.exit(asyncio.run(main(only)))
