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
import asyncio, json, os, random, re, socket, subprocess, sys, time, traceback, urllib.request
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
        pg.errors, pg.console = [], []
        pg.on('pageerror', lambda e: pg.errors.append(str(e)[:300]))
        pg.on('console', lambda m: pg.console.append(m.text))
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
            if (el.click) el.click(); else el.dispatchEvent(new MouseEvent('click', { bubbles: true }));
            return el.getAttribute('data-act') ? 'act' : 'ask'; }''', prefix)
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
    # every day of the period has its column and its date
    n_days, n_labels = await shop.evaluate("""() => [document.querySelectorAll('.chart.bare .bar').length,
        document.querySelectorAll('.chart.bare text.dnum').length]""")
    assert n_days >= 28 and n_labels == n_days, (n_days, n_labels)
    # as many columns as the screen holds, the rest a sideways scroll in the chart
    assert await shop.evaluate("() => { const w = document.querySelector('.chart.scroll .cwrap'); return w.scrollWidth > w.clientWidth }")
    assert await shop.evaluate("() => document.documentElement.scrollWidth <= innerWidth")
    await t.press(shop, 'earn:all')
    assert await _contains(shop, 'All periods together')
    # all of time scrolls sideways inside the chart, never the page
    assert await shop.evaluate("() => { const w = document.querySelector('.chart.scroll .cwrap'); return w.scrollWidth > w.clientWidth }")
    assert await shop.evaluate("() => document.documentElement.scrollWidth <= innerWidth")
    total = await shop.evaluate("() => document.querySelectorAll('main .rowlist')[0].querySelectorAll('[data-go=\"s.order\"]').length")
    day = await shop.evaluate("""() => { const g = [...document.querySelectorAll('.chart.scroll .bar')].filter(g => g.querySelector('.b'));
        return g[g.length - 1].getAttribute('data-act') }""")
    await t.press(shop, day)
    one = await shop.evaluate("() => document.querySelectorAll('main .rowlist')[0].querySelectorAll('[data-go=\"s.order\"]').length")
    assert 0 < one < total or total == one == 1, ('a picked day did not narrow the list', one, total)
    await t.press(shop, day)
    again = await shop.evaluate("() => document.querySelectorAll('main .rowlist')[0].querySelectorAll('[data-go=\"s.order\"]').length")
    assert again == total, 'the same day again did not bring every order back'
    assert not await shop.evaluate("() => [...document.querySelectorAll('#tabbar [data-go]')].some(b => b.getAttribute('data-go') === 's.stats')"), 'Results is still in the tab bar'


@flow
async def office_sees_everything_about_an_order(t):
    admin = await t.phone('/admin' + t.own_world())
    await t.go(admin, 'a.order', '1040-A')
    txt = await t.text(admin)
    for need in ['+374 10 52 18 40', 'accounts@arambooks.am', 'Tumanyan 12', '+374 95 65 43 21', 'Komitas 3',
                 '+374 77 18 42 06', 'The Chrysalids', '4 300', '5 300', 'Placed', 'Ready', 'Collected by the courier', 'Delivered']:
        assert need.replace(' ', '\u00a0') in txt or need in txt, 'the office order page does not show ' + need
    assert await admin.evaluate("() => !!document.querySelector('main .cover')"), 'no book picture'


@flow
async def courier_paying_at_the_counter_needs_the_shops_code(t):
    reader = await t.phone('/reader'); admin = await t.phone('/admin')
    shop = await t.phone('/seller'); courier = await t.phone('/courier')
    title = 'Flow P ' + str(random.randint(1000, 9999))
    rid = await t.reader_asks(reader, title)
    await t.admin_passes_request(admin, rid)
    oid = await t.shop_offers(shop, rid, title)
    await t.admin_passes_offer(admin, oid)
    ordid = await t.reader_buys(reader, rid, oid, 'courier')
    sub = t._ord(ordid)['subs'][0]
    await t.until(lambda: t._has(shop, 'orders', ordid), 10)
    await t.go(shop, 's.order', sub['no'])
    await t.press(shop, 'ready:%s:%s' % (ordid, sub['no']))
    await t.until(lambda: t._ord(ordid)['subs'][0]['status'] == 'ready', 8)
    await t.until(lambda: t._has(courier, 'orders', ordid), 10)
    await t.until(lambda: courier.evaluate("(o) => { const x = SC_DEBUG.get('orders', o); return !!x && x.subs[0].status === 'ready' }", ordid), 10)
    await t.go(courier, 'c.job', sub['no'])
    await t.press(courier, 'cmode:%s:%s' % (ordid, sub['no']))           # pay the shop at the counter
    await t.until(lambda: t._ord(ordid)['subs'][0].get('payMode') == 'onpickup' and t._ord(ordid)['subs'][0].get('payCode'), 8)
    code = t._ord(ordid)['subs'][0]['payCode']
    assert not await _contains(courier, code), 'the courier sees the shop code'
    await t.until(lambda: _contains(shop, code), 10, 'the shop never got a code to give')
    pc = '#pc_' + sub['no']
    await courier.fill(pc, '1111' if code != '1111' else '2222')
    await t.press(courier, 'ccollect:%s:%s' % (ordid, sub['no']))
    assert t._ord(ordid)['subs'][0]['status'] == 'ready', 'collected and paid without the shop code'
    assert await _contains(courier, 'not the shop'), 'no word about the wrong code'
    await courier.fill(pc, code)
    await t.press(courier, 'ccollect:%s:%s' % (ordid, sub['no']))
    await t.until(lambda: t._ord(ordid)['subs'][0]['status'] == 'shipped', 8, 'the right code did not record the collection')
    assert any(l.get('sub') == sub['no'] and l.get('from') == 'courier' and l.get('to') == 'shop' for l in t.world()['ledger'])


@flow
async def back_goes_to_the_screen_you_came_from(t):
    shop = await t.phone('/seller' + t.own_world())
    await t.go(shop, 's.billing')
    await t.press(shop, 'earn:all')
    no = await shop.evaluate("() => document.querySelector('main [data-go=\"s.order\"]').getAttribute('data-p')")
    await t.go(shop, 's.order', no)
    await t.press(shop, 'goback')
    assert await shop.evaluate('() => SC_DEBUG.screen()') == 's.earn', 'back from an order did not return to the history'
    assert await _contains(shop, 'All periods together')
    await t.press(shop, 'goback')
    assert await shop.evaluate('() => SC_DEBUG.screen()') == 's.billing'
    # the same order opened from Orders goes back to Orders
    await t.go(shop, 's.orders')
    await t.go(shop, 's.order', no)
    await t.press(shop, 'goback')
    assert await shop.evaluate('() => SC_DEBUG.screen()') == 's.orders'


# ============================ user stories: reader ===========================
# Each flow is named after its story in user-stories.md (shelfcall-prototype-testing).
# An assertion message names the rule it checks; a failing one is a finding.

async def _order_in_own_world(t, mode):
    """A fresh world, a request, an approved offer and an order in `mode`."""
    w = t.own_world()
    reader = await t.phone('/reader' + w); admin = await t.phone('/admin' + w); shop = await t.phone('/seller' + w)
    title = 'Story ' + str(random.randint(1000, 9999))
    rid = await t.reader_asks(reader, title)
    await t.admin_passes_request(admin, rid)
    oid = await t.shop_offers(shop, rid, title)
    await t.admin_passes_offer(admin, oid)
    ordid = await t.reader_buys(reader, rid, oid, mode)
    return w, reader, admin, shop, rid, oid, ordid


async def _visible_fields(pg):
    return await pg.evaluate("""() => [...document.querySelectorAll('#app input, #app textarea, #app select')]
        .filter(e => e.type !== 'file' && e.type !== 'hidden' && e.offsetParent !== null && !e.disabled).length""")


async def _tabbar_shown(pg):
    return await pg.evaluate("() => { const t = document.getElementById('tabbar'); return !!t && !t.hidden && getComputedStyle(t).display !== 'none' }")


@flow
async def r01_the_reader_door_is_google_only(t):
    reader = await t.phone('/reader' + t.own_world())
    await t.go(reader, 'x.auth')
    txt = await t.text(reader)
    assert 'Google' in txt, 'R-01 §2: the reader door does not offer Google'
    n = await reader.evaluate("() => document.querySelectorAll('#app input[type=password], #app input[type=email]').length")
    assert n == 0, 'R-01 §2: the reader door offers another sign-in method (%d password/email fields)' % n


@flow
async def r02_asking_follows_the_form_rules(t):
    reader = await t.phone('/reader' + t.own_world())
    await t.go(reader, 'r.new')
    assert ('step 1 of 3' in (await t.text(reader)).lower()), 'R-02 §10: step 1 does not say "Step 1 of 3"'
    assert not await _tabbar_shown(reader), 'R-02 §10: tab bar on a flow screen (step 1)'
    await t.press(reader, 'kind:concrete')
    assert ('step 2 of 3' in (await t.text(reader)).lower()), 'R-02 §10: step 2 does not say "Step 2 of 3"'
    assert not await _tabbar_shown(reader), 'R-02 §10: tab bar on a flow screen (step 2)'
    back = await reader.evaluate("() => (document.querySelector('#app .back') || {}).textContent || ''")
    assert re.search(r'\w', back.replace('←', '')) and back.strip() not in ('← Back', 'Back'), 'R-02 §10: the back link does not name where it goes: %r' % back
    n = await _visible_fields(reader)
    assert n <= 4, 'R-02 §10: step 2 has %d fields (a heading plus four is the ceiling)' % n
    await reader.fill('#f_title', 'Story title'); await reader.locator('#f_title').blur()
    await t.press(reader, 'rstep:3')
    assert ('step 3 of 3' in (await t.text(reader)).lower()), 'R-02 §10: step 3 does not say "Step 3 of 3"'
    opts = await reader.evaluate("() => [...document.querySelectorAll('#f_cond option')].map(o => o.value || o.textContent)")
    assert 'any' in opts, 'R-02 §5: a request cannot say condition "any": %s' % opts
    n = await _visible_fields(reader)
    assert n <= 4, 'R-02 §10: step 3 has %d fields' % n


@flow
async def r03_offer_rows_open_pages_and_nothing_asks_to_tidy_up(t):
    reader = await t.phone('/reader' + t.own_world())
    await t.go(reader, 'r.request', 'r2')
    per_row = await reader.evaluate("() => [...document.querySelectorAll('#app .row.tap')].map(r => r.querySelectorAll('button[data-act]').length)")
    assert per_row, 'R-03: no offer rows on r2'
    assert max(per_row) <= 1, 'R-03 §7: an offer in a list has one Button; rows have %s action buttons (Add to cart and Buy)' % per_row
    acts = ' '.join(await t.acts(reader))
    for word in ('decline', 'dismiss', 'archive', 'markread'):
        assert word not in acts, 'R-03 §7: the reader is asked to tidy up offers (%s)' % word
    sent = await reader.evaluate("() => [...document.querySelectorAll('#app .row.tap')].map(r => r.getAttribute('data-p'))")
    oid = sent[0]
    await t.go(reader, 'r.offer', oid)
    await t.until(lambda: t._off(oid).get('status') in ('seen', 'in_cart'), 8, 'R-03 §5: opening the offer did not make it "seen"')


@flow
async def r04_the_reader_sees_a_lowered_price(t):
    w = t.own_world()
    reader = await t.phone('/reader' + w); shop = await t.phone('/seller' + w)
    await t.go(reader, 'r.offer', 'o1')
    await t.until(lambda: t._off('o1').get('status') == 'seen', 8)
    old = t._off('o1')['price']
    await t.until(lambda: shop.evaluate("() => SC_DEBUG.get('offers','o1').status === 'seen'"), 10)
    await t.go(shop, 's.offers')
    await t.press(shop, 'editoffer:o1')
    await shop.fill('#o_price', str(old - 500))
    await t.press(shop, 'saveoffer:o1')
    await t.until(lambda: t._off('o1')['price'] == old - 500, 8, 'R-04: the lowered price did not reach the server')
    await t.go(reader, 'r.offer', 'o1')
    await t.until(lambda: _contains(reader, '{:,}'.format(old - 500).replace(',', ' ') + ' \u058f'), 10,
                  'R-04: the reader does not see the lowered price')


@flow
async def r05_a_removed_offer_cannot_go_in_the_cart_from_a_stale_screen(t):
    w = t.own_world()
    reader = await t.phone('/reader' + w); shop = await t.phone('/seller' + w)
    await t.go(reader, 'r.request', 'r2')
    oid = await reader.evaluate("() => document.querySelector('#app .row.tap').getAttribute('data-p')")
    await t.until(lambda: t._has(shop, 'offers', oid), 8)
    await t.go(shop, 's.offers')
    await shop.evaluate("(o) => { const b = document.createElement('button'); b.setAttribute('data-act', 'removeoffer:' + o); document.body.appendChild(b); b.click(); b.remove(); }", oid)
    await t.until(lambda: t._off(oid)['status'] == 'removed', 8)
    await t.until(lambda: t._field(reader, 'offers', oid, 'status', 'removed'), 10)
    # the reader's old screen still has the button: press it
    await reader.evaluate("(o) => { const b = document.createElement('button'); b.setAttribute('data-act', 'add:' + o); document.body.appendChild(b); b.click(); b.remove(); }", oid)
    await reader.wait_for_timeout(400)
    srv = [c.get('id') for c in t.world().get('cart', [])]
    assert oid not in srv, 'R-05 §9: a removed offer went into the cart from a stale screen'


@flow
async def r06_checkout_says_cash_and_has_no_card(t):
    w, reader, admin, shop, rid, oid, ordid = await _order_in_own_world(t, 'courier')
    # the placed order screen and the order list both state the amount in cash
    await t.go(reader, 'r.orders')
    assert await _contains(reader, 'in cash') or await _contains(reader, 'In cash'), 'R-06 §11: the order total does not say to pay in cash'
    cards = await reader.evaluate("""() => [...document.querySelectorAll('input')].filter(i => /cc-|card/i.test((i.autocomplete||'') + (i.name||'') + (i.id||''))).length""")
    assert cards == 0, 'R-06 §11: a card field exists'


@flow
async def r06_delivery_windows_and_the_courier_note(t):
    w = t.own_world()
    reader = await t.phone('/reader' + w)
    await t.go(reader, 'r.request', 'r2'); await t.press(reader, 'add:')
    await t.go(reader, 'r.cart'); await t.press(reader, 'delall:pickup', required=False); await t.press(reader, 'checkout')
    # pickup: no note for the courier
    for _ in range(4):
        if await reader.locator('#c_name').count(): break
        await t.press(reader, 'editdetails', required=False)
    assert await reader.locator('#c_note').count() == 0, 'R-06 §8: the note for the courier is asked on a pickup order'
    await t.go(reader, 'r.cart'); await t.press(reader, 'delall:courier', required=False); await t.press(reader, 'checkout')
    await t.press(reader, 'editwhen', required=False)
    chips = await reader.evaluate("""() => [...document.querySelectorAll('[data-act^="setwhen:"]')].map(b => Math.round(b.getBoundingClientRect().height))""")
    assert chips and min(chips) >= 36, 'R-06 §7: delivery windows are not 36px chips: %s' % chips
    wraps = await reader.evaluate("""() => { const b = document.querySelector('[data-act^="setwhen:"]'); return b ? getComputedStyle(b.parentElement).flexWrap : '' }""")
    assert wraps == 'wrap', 'R-06 §7: delivery windows are not a wrapping row (%s)' % wraps


@flow
async def r07_times_are_shown_in_yerevan(t):
    w = t.own_world()
    async def slots(tz):
        ctx = await t.browser.new_context(viewport={'width': 390, 'height': 844}, timezone_id=tz)
        await ctx.route('**/fonts.g*/**', lambda r: r.abort())
        pg = await ctx.new_page(); pg.errors = []
        await pg.goto(t.base + '/reader' + w)
        await t.until(lambda: pg.evaluate('() => !!document.querySelector("main h1")'), 8)
        t.pages.append(pg)
        await t.go(pg, 'r.request', 'r2'); await t.press(pg, 'add:', required=False)
        await t.go(pg, 'r.cart'); await t.press(pg, 'delall:courier', required=False); await t.press(pg, 'checkout')
        await t.press(pg, 'editwhen', required=False)
        return await pg.evaluate("""() => [...document.querySelectorAll('[data-act^="setwhen:"]')].map(b => b.innerText.trim())""")
    a = await slots('Asia/Yerevan'); b = await slots('America/New_York')
    assert a and a == b, 'R-07 §9: delivery times follow the phone\'s time zone, not Asia/Yerevan: %s vs %s' % (a[:3], b[:3])


@flow
async def r08_a_wrong_pickup_code_is_refused(t):
    w, reader, admin, shop, rid, oid, ordid = await _order_in_own_world(t, 'pickup')
    sub = t._ord(ordid)['subs'][0]
    await t.until(lambda: t._has(shop, 'orders', ordid), 10)
    await t.go(shop, 's.order', sub['no'])
    await t.press(shop, 'ready:%s:%s' % (ordid, sub['no']))
    await t.until(lambda: t._ord(ordid)['subs'][0]['status'] == 'shipped', 8)
    await t.go(reader, 'r.orders')
    await t.until(lambda: _contains(reader, sub['code']), 10)
    mono = await reader.evaluate("(c) => { const e = [...document.querySelectorAll('#app *')].find(x => x.children.length === 0 && x.textContent.trim() === c); return e ? getComputedStyle(e).fontFamily : '' }", sub['code'])
    assert 'mono' in mono.lower(), 'R-08 §6: the handover code is not in the mono face (%s)' % mono
    wrong = '1111' if sub['code'] != '1111' else '2222'
    await t.go(shop, 's.order', sub['no'])
    await shop.fill('#code_' + sub['no'], wrong)
    await t.press(shop, 'entercode:%s:%s' % (ordid, sub['no']))
    await shop.wait_for_timeout(500)
    assert t._ord(ordid)['subs'][0]['status'] == 'shipped', 'R-08 §5: a wrong code completed the handover'


@flow
async def r09_closing_a_request_asks_first(t):
    reader = await t.phone('/reader' + t.own_world())
    await t.go(reader, 'r.request', 'r3')
    await reader.evaluate("() => document.querySelector('[data-ask^=\"closereq:\"]').click()")
    await reader.wait_for_timeout(300)
    sheet = await reader.evaluate("() => { const d = document.getElementById('sheet'); return d && d.open ? d.innerText : '' }")
    assert sheet, 'R-09 §7: closing does not open a sheet'
    assert 'Close this request?' in sheet, 'R-09 §7: the sheet does not name the consequence'
    assert 'Are you sure' not in sheet, 'R-09 §7: the sheet asks "Are you sure"'
    assert re.search(r'[Nn]othing is deleted|keep the record', sheet), 'R-09 §7: the sheet does not say what does not change'
    assert t._req('r3')['status'] == 'open', 'R-09 §7: the request changed before confirm'
    await reader.evaluate("() => document.querySelector('#sheet [data-act=\"sheetgo\"]').click()")
    await t.until(lambda: t._req('r3')['status'] == 'closed', 8, 'R-09: confirming did not close the request')


@flow
async def r10_armenian_tab_labels_fit_and_settings_says_what_is_missing(t):
    reader = await t.phone('/reader' + t.own_world())
    await t.go(reader, 'x.settings')
    await t.press(reader, 'lang:hy')
    await t.go(reader, 'r.requests')
    over = await reader.evaluate("""() => [...document.querySelectorAll('#tabbar button, #app .seg button, #app .fchip')]
        .filter(b => b.offsetParent !== null && b.scrollWidth > b.clientWidth + 1).map(b => b.innerText.trim())""")
    assert not over, 'R-10 §11: Armenian labels overflow their slot: %s' % over
    await t.go(reader, 'x.settings')
    txt = await t.text(reader)
    assert re.search(r'[Tt]ranslation|թարգման', txt), 'R-10 §11: settings does not say which language is incomplete'


# ========================== user stories: bookseller =========================

async def _inject(pg, attr, value):
    """Press a button that an older render of the screen would still show (a stale screen)."""
    await pg.evaluate("([a, v]) => { const b = document.createElement('button'); b.setAttribute(a, v); document.body.appendChild(b); b.click(); b.remove(); }", [attr, value])
    await pg.wait_for_timeout(350)


@flow
async def b01_registration_validates_each_step_and_keeps_the_budget(t):
    shop = await t.phone('/seller' + t.own_world())
    await t.go(shop, 'x.settings'); await t.press(shop, 'newshop')
    assert 'step 1 of 4' in (await t.text(shop)).lower(), 'B-01 §10: step 1 does not say "Step 1 of 4"'
    assert await _visible_fields(shop) <= 4, 'B-01 §10: more than four fields on step 1'
    await t.press(shop, 'gstep:2')                                   # no name
    assert 'step 1 of 4' in (await t.text(shop)).lower(), 'B-01 §10: leaving step 1 without a name did not keep you on step 1'
    assert await shop.evaluate("() => !!document.querySelector('#app .err')"), 'B-01 §10: no message for the missing name'
    await shop.fill('#g_shop', 'Story Shop'); await t.press(shop, 'gstep:2')
    await t.press(shop, 'gstep:3')
    assert await _visible_fields(shop) <= 4, 'B-01 §10: more than four fields on step 3'
    await t.press(shop, 'gstep:4')                                   # no branch name or address
    assert 'step 3 of 4' in (await t.text(shop)).lower(), 'B-01 §10: leaving step 3 without an address did not keep you on step 3'


@flow
async def b02_an_offer_cannot_say_any_condition(t):
    shop = await t.phone('/seller' + t.own_world())
    await t.go(shop, 's.newoffer', 'r1')
    for _ in range(6):
        if await shop.locator('#o_cond').count(): break
        acts = await t.acts(shop)
        steps = [a for a in acts if a.startswith('step:')]
        if not steps: break
        await t.press(shop, steps[-1])
        for sel, val in [('#o_title', 'Story book'), ('#o_author', 'A. Writer')]:
            if await shop.locator(sel).count() and not await shop.locator(sel).input_value(): await shop.fill(sel, val)
    assert await shop.locator('#o_cond').count(), 'B-02: never reached the condition field'
    opts = await shop.evaluate("() => [...document.querySelectorAll('#o_cond option')].map(o => (o.value || o.textContent).trim())")
    assert 'any' not in opts, 'B-02 §5: an offer may say condition "any": %s' % opts


@flow
async def b03_offer_edit_rules(t):
    w = t.own_world()
    reader = await t.phone('/reader' + w); shop = await t.phone('/seller' + w)
    await t.go(reader, 'r.offer', 'o1')
    await t.until(lambda: t._off('o1').get('status') == 'seen', 8)
    await t.until(lambda: shop.evaluate("() => SC_DEBUG.get('offers','o1').status === 'seen'"), 10)
    price = t._off('o1')['price']
    await t.go(shop, 's.offers'); await t.press(shop, 'editoffer:o1')
    assert await shop.locator('#o_title').count() == 0, 'B-03 §5: book fields can still be edited after the reader has seen the offer'
    await shop.fill('#o_price', str(price + 500)); await t.press(shop, 'saveoffer:o1')
    assert t._off('o1')['price'] == price, 'B-03 §5: the price went up after the reader saw the offer'
    assert await _contains(shop, 'not raise'), 'B-03 §5: no message for a price rise after seen'
    for i in range(3):                                           # the 1st, 2nd and 3rd change are allowed
        await t.go(shop, 's.offers'); await t.press(shop, 'editoffer:o1')
        price -= 100
        await shop.fill('#o_price', str(price)); await t.press(shop, 'saveoffer:o1')
        await t.until(lambda: t._off('o1')['price'] == price, 8, 'B-03 §5: price change %d was refused' % (i + 1))
    await t.go(shop, 's.offers'); await t.press(shop, 'editoffer:o1')
    if await shop.locator('#o_price').count():
        await shop.fill('#o_price', str(price - 100)); await t.press(shop, 'saveoffer:o1')
    await shop.wait_for_timeout(500)
    assert t._off('o1')['price'] == price, 'B-03 §5: a 4th price change went through'


@flow
async def b03_nothing_changes_after_the_order(t):
    w, reader, admin, shop, rid, oid, ordid = await _order_in_own_world(t, 'pickup')
    await t.until(lambda: t._off(oid)['status'] == 'done_sold', 8)
    before = t._off(oid)['price']
    await t.until(lambda: t._field(shop, 'offers', oid, 'status', 'done_sold'), 10)
    await _inject(shop, 'data-act', 'editoffer:' + oid)            # an old screen's Edit button
    if await shop.locator('#o_price').count():
        await shop.fill('#o_price', str(before - 100))
        await _inject(shop, 'data-act', 'saveoffer:' + oid)
    await shop.wait_for_timeout(400)
    assert t._off(oid)['price'] == before, 'B-03 §5: an ordered offer changed its price'


@flow
async def b04_withdrawing_needs_a_reason_and_stops_after_the_order(t):
    w = t.own_world()
    shop = await t.phone('/seller' + w)
    await t.go(shop, 's.offers')
    await shop.evaluate("() => document.querySelector('[data-ask^=\"removeoffer:\"]').click()")
    await shop.wait_for_timeout(300)
    info = await shop.evaluate("""() => { const d = document.getElementById('sheet'); if (!d || !d.open) return null;
        const go = d.querySelector('[data-act="sheetgo"]'); return { reasons: d.querySelectorAll('[data-act^="sheetreason"]').length, disabled: !!(go && go.disabled) } }""")
    assert info, 'B-04 §7: withdrawing does not open a sheet'
    assert info['reasons'] > 0 and info['disabled'], 'B-04 §5 §7: withdrawing asks no reason (confirm enabled, %d reasons)' % info['reasons']


@flow
async def b04_an_ordered_offer_cannot_be_withdrawn(t):
    w, reader, admin, shop, rid, oid, ordid = await _order_in_own_world(t, 'pickup')
    await t.until(lambda: t._field(shop, 'offers', oid, 'status', 'done_sold'), 10)
    await _inject(shop, 'data-act', 'removeoffer:' + oid)          # an old screen's "take down"
    await shop.wait_for_timeout(500)
    assert t._off(oid)['status'] == 'done_sold', 'B-04 §5 §9: an ordered offer was withdrawn from a stale screen (now %s)' % t._off(oid)['status']


@flow
async def b05_the_order_list_never_acts(t):
    shop = await t.phone('/seller' + t.own_world())
    await t.go(shop, 's.orders')
    await t.press(shop, 'otab:past')                                 # a fresh shop has only finished orders
    acts = await shop.evaluate("() => [...document.querySelectorAll('#app .rowlist [data-act], #app .rowlist [data-ask]')].map(e => e.getAttribute('data-act') || e.getAttribute('data-ask'))")
    assert not acts, 'B-05 §7: the bookseller order list has buttons: %s' % acts[:5]
    rows = await shop.evaluate("() => document.querySelectorAll('#app .rowlist [data-go=\"s.order\"]').length")
    assert rows > 0, 'B-05: order rows do not open the order page'


@flow
async def b06_pickup_buyer_appears_only_once_ready(t):
    w, reader, admin, shop, rid, oid, ordid = await _order_in_own_world(t, 'pickup')
    order = t._ord(ordid); sub = order['subs'][0]
    await t.until(lambda: t._has(shop, 'orders', ordid), 10)
    await t.go(shop, 's.order', sub['no'])
    txt = await t.text(shop)
    assert order.get('phone') and order['phone'] not in txt, 'B-06 §8: the pickup buyer\'s phone shows before "ready"'
    assert order.get('name') and order['name'] not in txt, 'B-06 §8: the pickup buyer\'s name shows before "ready" (%r)' % order.get('name')
    await t.press(shop, 'ready:%s:%s' % (ordid, sub['no']))
    await t.until(lambda: t._ord(ordid)['subs'][0]['status'] == 'shipped', 8)
    await t.go(shop, 's.order', sub['no'])
    txt = await t.text(shop)
    assert order['phone'] in txt, 'B-06 §8: the pickup buyer\'s phone does not show after "ready"'


@flow
async def b07_b08_courier_delivery_hides_the_buyer_and_the_note(t):
    w = t.own_world()
    reader = await t.phone('/reader' + w); admin = await t.phone('/admin' + w); shop = await t.phone('/seller' + w)
    courier = await t.phone('/courier' + w)
    await reader.evaluate("() => { /* fixture: Dina has a note for couriers */ }")
    title = 'Story ' + str(random.randint(1000, 9999))
    rid = await t.reader_asks(reader, title)
    await t.admin_passes_request(admin, rid)
    oid = await t.shop_offers(shop, rid, title)
    await t.admin_passes_offer(admin, oid)
    ordid = await t.reader_buys(reader, rid, oid, 'courier')
    order = t._ord(ordid); sub = order['subs'][0]
    secret = [x for x in (order.get('name'), order.get('phone'), order.get('addr'), order.get('note')) if x]
    assert len(secret) >= 3, 'B-07: the order has no buyer data to hide: %s' % order
    async def shop_sees():
        out = []
        for scr, p in (('s.orders', None), ('s.order', sub['no']), ('s.billing', None), ('s.reviews', None)):
            await t.go(shop, scr, p); txt = await t.text(shop)
            out += ['%s on %s' % (x, scr) for x in secret if x in txt]
        return out
    await t.until(lambda: t._has(shop, 'orders', ordid), 10)
    leaks = await shop_sees()
    await t.go(shop, 's.order', sub['no'])
    assert await _contains(shop, 'do not see the buyer'), 'B-07 §8: the order page does not say why the buyer is hidden'
    await t.press(shop, 'ready:%s:%s' % (ordid, sub['no']))
    await t.until(lambda: t._has(courier, 'orders', ordid), 10)
    await t.until(lambda: courier.evaluate("(o) => SC_DEBUG.get('orders', o).subs[0].status === 'ready'", ordid), 10)
    await t.go(courier, 'c.job', sub['no']); await t.press(courier, 'ccollect:%s:%s' % (ordid, sub['no']))
    await t.until(lambda: t._ord(ordid)['subs'][0]['status'] == 'shipped', 8)
    await t.go(courier, 'c.job', sub['no']); await t.press(courier, 'cdeliverorder:%s' % ordid)
    await t.until(lambda: t._ord(ordid)['subs'][0]['status'] == 'completed', 8)
    await t.until(lambda: t._field(shop, 'orders', ordid, 'id', ordid), 5)
    await shop.wait_for_timeout(3500)
    leaks += await shop_sees()
    assert not leaks, 'B-07/B-08 §8: the shop sees buyer data on a courier delivery: %s' % sorted(set(leaks))
    cnote = [x for x in (order.get('note'),) if x]
    if not cnote: print('      note: this order carried no note for the courier, so B-08 was only checked for name/phone/address')


@flow
async def b09_an_unpaid_statement_is_a_standing_alert(t):
    shop = await t.phone('/seller' + t.own_world())
    await t.go(shop, 's.billing'); await t.press(shop, 'setstate:due')
    where = await shop.evaluate("""() => { const e = [...document.querySelectorAll('#app *')].find(x => x.children.length === 0 && /due today/.test(x.textContent));
        if (!e) return null; const a = e.closest('.note, [role=alert]'); return a ? 'alert' : (e.closest('.card') ? 'card' : 'other') }""")
    assert where, 'B-09: the due statement is not shown'
    assert where == 'alert', 'B-09 §7: an unpaid statement is a %s, not an Alert' % where
    assert await _contains(shop, '֏'), 'B-09 §5: amounts are not in drams'


@flow
async def b10_a_stale_ready_does_not_undo_a_collection(t):
    w, reader, admin, shop, rid, oid, ordid = await _order_in_own_world(t, 'courier')
    sub = t._ord(ordid)['subs'][0]
    courier = await t.phone('/courier' + w)
    await t.until(lambda: t._has(shop, 'orders', ordid), 10)
    await t.go(shop, 's.order', sub['no'])
    await t.press(shop, 'ready:%s:%s' % (ordid, sub['no']))
    await t.until(lambda: t._has(courier, 'orders', ordid), 10)
    await t.until(lambda: courier.evaluate("(o) => SC_DEBUG.get('orders', o).subs[0].status === 'ready'", ordid), 10)
    await t.go(courier, 'c.job', sub['no']); await t.press(courier, 'ccollect:%s:%s' % (ordid, sub['no']))
    await t.until(lambda: t._ord(ordid)['subs'][0]['status'] == 'shipped', 8)
    await t.until(lambda: t._field(shop, 'orders', ordid, 'id', ordid), 5)
    await shop.wait_for_timeout(3500)
    await _inject(shop, 'data-act', 'ready:%s:%s' % (ordid, sub['no']))   # the shop's second tab, never refreshed
    await shop.wait_for_timeout(2500)
    assert t._ord(ordid)['subs'][0]['status'] == 'shipped', 'B-10 §9: a stale "Ready" moved a collected order back to %s' % t._ord(ordid)['subs'][0]['status']


@flow
async def b08_the_shop_never_sees_the_note_for_the_courier(t):
    w = t.own_world()
    reader = await t.phone('/reader' + w); shop = await t.phone('/seller' + w)
    before = {o['id'] for o in t.world()['orders']}
    await t.go(reader, 'r.request', 'r2'); await t.press(reader, 'add:')
    await t.go(reader, 'r.cart'); await t.press(reader, 'delall:courier', required=False); await t.press(reader, 'checkout')
    chose = False
    for _ in range(12):
        acts = await t.acts(reader)
        if await reader.locator('#c_note').count():
            await reader.fill('#c_note', 'Gate 4417, story note')
            await reader.locator('#c_note').blur()
            await t.press(reader, 'donedetails'); continue
        if 'place' in acts:
            if 'Gate 4417' not in await t.text(reader):
                await t.press(reader, 'editdetails'); continue
            await t.press(reader, 'place'); break
        order_of = ['donewhen', 'editdetails'] if chose else ['setwhen:', 'donewhen', 'editdetails']
        for a in order_of:
            hit = next((x for x in acts if x.startswith(a)), None)
            if hit:
                if a == 'setwhen:': chose = True
                await t.press(reader, hit); break
    ordid = await t.until(lambda: next((o['id'] for o in t.world()['orders'] if o['id'] not in before), None), 8, 'B-08: no order placed')
    order = t._ord(ordid); sub = order['subs'][0]
    assert 'Gate 4417' in (order.get('note') or ''), 'B-08: the note did not reach the order (%r)' % order.get('note')
    await t.until(lambda: t._has(shop, 'orders', ordid), 10)
    seen = []
    for scr, p in (('s.orders', None), ('s.order', sub['no'])):
        await t.go(shop, scr, p)
        if 'Gate 4417' in await t.text(shop): seen.append(scr)
    await t.go(shop, 's.order', sub['no']); await t.press(shop, 'ready:%s:%s' % (ordid, sub['no']))
    await t.go(shop, 's.order', sub['no'])
    if 'Gate 4417' in await t.text(shop): seen.append('s.order (ready)')
    assert not seen, 'B-08 §8: the shop sees the note for the courier on %s' % seen


# ============================ user stories: courier ==========================

@flow
async def c01_there_is_no_public_courier_sign_up(t):
    courier = await t.phone('/courier' + t.own_world())
    await t.go(courier, 'x.auth')
    acts = ' '.join(await t.acts(courier))
    assert not re.search(r'startreg|newshop|signup|register', acts), 'C-01 §2: the courier door offers a sign-up (%s)' % acts
    # Prose may say there is nothing to sign up for; only a pressable invitation counts.
    btns = (await courier.evaluate("() => [...document.querySelectorAll('main button, main a, #dock button')].map(b => b.innerText).join(' | ')")).lower()
    assert not re.search(r'sign up|create an account|register', btns), 'C-01 §2: the courier door has a sign-up button (%s)' % btns
    screens = await courier.evaluate("() => Object.keys(window).length")  # page loaded
    for scr in ('c.reg', 'c.signup', 'c.apply'):
        await t.go(courier, scr)
        assert await courier.evaluate('() => SC_DEBUG.screen()') != scr or not await courier.evaluate("() => !!document.querySelector('#app input')"), \
            'C-01 §2: a courier sign-up screen exists (%s)' % scr


@flow
async def c02_a_courier_cannot_collect_what_the_shop_has_not_made_ready(t):
    w, reader, admin, shop, rid, oid, ordid = await _order_in_own_world(t, 'courier')
    sub = t._ord(ordid)['subs'][0]
    courier = await t.phone('/courier' + w)
    await t.until(lambda: t._has(courier, 'orders', ordid), 10)
    assert t._ord(ordid)['subs'][0]['status'] == 'placed'
    await _inject(courier, 'data-act', 'ccollect:%s:%s' % (ordid, sub['no']))   # a stale or forged button
    await courier.wait_for_timeout(1500)
    assert t._ord(ordid)['subs'][0]['status'] == 'placed', 'C-02 §5 §9: the courier collected an order the shop had not marked ready (now %s)' % t._ord(ordid)['subs'][0]['status']


@flow
async def c03_delivery_shows_address_and_note_names_the_cash_and_checks_a_code(t):
    w = t.own_world()
    reader = await t.phone('/reader' + w); shop = await t.phone('/seller' + w); courier = await t.phone('/courier' + w)
    before = {o['id'] for o in t.world()['orders']}
    await t.go(reader, 'r.request', 'r2'); await t.press(reader, 'add:')
    await t.go(reader, 'r.cart'); await t.press(reader, 'delall:courier', required=False); await t.press(reader, 'checkout')
    chose = False
    for _ in range(12):
        acts = await t.acts(reader)
        if await reader.locator('#c_note').count():
            await reader.fill('#c_note', 'Gate 4417, story note'); await reader.locator('#c_note').blur()
            await t.press(reader, 'donedetails'); continue
        if 'place' in acts:
            if 'Gate 4417' not in await t.text(reader):
                await t.press(reader, 'editdetails'); continue
            await t.press(reader, 'place'); break
        for a in (['donewhen', 'editdetails'] if chose else ['setwhen:', 'donewhen', 'editdetails']):
            hit = next((x for x in acts if x.startswith(a)), None)
            if hit:
                if a == 'setwhen:': chose = True
                await t.press(reader, hit); break
    ordid = await t.until(lambda: next((o['id'] for o in t.world()['orders'] if o['id'] not in before), None), 8)
    order = t._ord(ordid); sub = order['subs'][0]
    await t.until(lambda: t._has(shop, 'orders', ordid), 10)
    await t.go(shop, 's.order', sub['no']); await t.press(shop, 'ready:%s:%s' % (ordid, sub['no']))
    await t.until(lambda: t._has(courier, 'orders', ordid), 10)
    await t.until(lambda: courier.evaluate("(o) => SC_DEBUG.get('orders', o).subs[0].status === 'ready'", ordid), 10)
    await t.go(courier, 'c.job', sub['no']); await t.press(courier, 'ccollect:%s:%s' % (ordid, sub['no']))
    await t.until(lambda: t._ord(ordid)['subs'][0]['status'] == 'shipped', 8)
    await t.go(courier, 'c.job', sub['no'])
    txt = await t.text(courier)
    assert order['addr'].split(',')[0] in txt, 'C-03 §8: the courier does not see the address'
    assert 'Gate 4417' in txt, 'C-03 §8: the courier does not see the note for the courier'
    label = await courier.evaluate("() => { const b = document.querySelector('[data-act^=\"cdeliverorder:\"]'); return b ? b.innerText.trim() : '' }")
    total = order['books'] + order['fee']
    assert re.search(r'took', label, re.I) and '{:,}'.format(total).replace(',', ' ') in label, \
        'C-03 §11: the delivery button does not name the cash taken: %r' % label
    has_code = await courier.evaluate("() => !!document.querySelector('#app input[inputmode=numeric]')")
    assert has_code, 'C-03 §5: delivering asks no handover code from the reader'


@flow
async def c04_could_not_deliver_asks_a_reason_first(t):
    w, reader, admin, shop, rid, oid, ordid = await _order_in_own_world(t, 'courier')
    sub = t._ord(ordid)['subs'][0]
    courier = await t.phone('/courier' + w)
    await t.until(lambda: t._has(shop, 'orders', ordid), 10)
    await t.go(shop, 's.order', sub['no']); await t.press(shop, 'ready:%s:%s' % (ordid, sub['no']))
    await t.until(lambda: courier.evaluate("(o) => { const x = SC_DEBUG.get('orders', o); return !!x && x.subs[0].status === 'ready' }", ordid), 12)
    await t.go(courier, 'c.job', sub['no']); await t.press(courier, 'ccollect:%s:%s' % (ordid, sub['no']))
    await t.until(lambda: t._ord(ordid)['subs'][0]['status'] == 'shipped', 8)
    await t.go(courier, 'c.job', sub['no'])
    await courier.evaluate("() => document.querySelector('[data-ask^=\"cfailorder:\"]').click()")
    await courier.wait_for_timeout(300)
    info = await courier.evaluate("""() => { const d = document.getElementById('sheet'); if (!d || !d.open) return null;
        const go = d.querySelector('[data-act="sheetgo"]'); return { reasons: d.querySelectorAll('[data-act^="sheetreason"]').length, disabled: !!(go && go.disabled) } }""")
    assert info, 'C-04 §7: "Could not deliver" does not open a sheet'
    assert info['reasons'] > 0 and info['disabled'], 'C-04 §7: the confirm is not disabled until a reason is picked: %s' % info
    assert t._ord(ordid)['subs'][0]['status'] == 'shipped', 'C-04 §7: the order changed before confirm'


async def _contains(pg, s):
    return s in await Run.text(pg)


async def _not_contains(pg, s):
    return s not in await Run.text(pg)


# ================================ runner =====================================

MONEY_OK = re.compile(r'^\d{1,3}(?:[ \u00a0\u202f]\d{3})*[ \u00a0]֏$')
MONEY_ANY = re.compile(r'[\d][\d ,.\u00a0\u202f]*[ \u00a0]?֏|\bAMD\b|\$\s?\d|\d\s?(?:dram|драм)')


async def _money_on(pg):
    txt = await pg.inner_text('body')
    bad = []
    for m in MONEY_ANY.finditer(txt):
        tok = m.group(0).strip()
        if tok.endswith('֏') and MONEY_OK.match(tok): continue
        bad.append(tok)
    return bad


@flow
async def x05_every_amount_reads_like_5_500_dram(t):
    w = t.own_world()
    seen = {}
    for role, screens in (('reader', ['r.offers', 'r.cart', 'r.orders', 'r.account']),
                          ('seller', ['s.offers', 's.orders', 's.billing', 's.pay', 's.account']),
                          ('courier', ['c.jobs', 'c.done'])):
        pg = await t.phone('/' + role + w)
        for scr in screens:
            await t.go(pg, scr)
            for tok in await _money_on(pg):
                # The bank-transfer field on s.pay says "AMD" because it is copied into a banking app.
                if scr == 's.pay' and tok == 'AMD': continue
                seen.setdefault(tok, set()).add(scr)
    assert not seen, 'X-05 §5 money.ts: amounts not written as "5 500 ֏": ' + '; '.join(
        '%r on %s' % (k, ','.join(sorted(v))) for k, v in list(seen.items())[:8])


PHONE_RE = re.compile(r'(?:\+374[\s-]?\d{2}[\s-]?\d{3}[\s-]?\d{3}|\b0\d{2}[\s-]?\d{3}[\s-]?\d{3}\b)')


@flow
async def x06_logs_carry_no_phone_address_or_code(t):
    w, reader, admin, shop, rid, oid, ordid = await _order_in_own_world(t, 'courier')
    courier = await t.phone('/courier' + w)
    await t.until(lambda: t._has(courier, 'orders', ordid), 10)
    order = t._ord(ordid)
    codes = [str(x.get(k)) for x in order.get('subs', []) for k in ('code', 'payCode') if x.get(k)]
    if order.get('code'): codes.append(str(order['code']))
    addr = str(order.get('address') or order.get('addr') or '')
    leaks = []
    for pg in (reader, admin, shop, courier):
        for line in pg.console:
            if PHONE_RE.search(line): leaks.append('phone: ' + line[:80])
            if addr and len(addr) > 6 and addr in line: leaks.append('address: ' + line[:80])
            if any(c and re.search(r'\b%s\b' % re.escape(c), line) for c in codes): leaks.append('code: ' + line[:80])
    assert not leaks, 'X-06 §8: console output carries personal data: %s' % leaks[:4]


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
