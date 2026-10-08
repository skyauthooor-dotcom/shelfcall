#!/usr/bin/env python3
"""
Contrast audit of every screen it can reach, in the light and the dark theme.

    python3 tests/tools/contrast.py              # all pages, both themes
    python3 tests/tools/contrast.py --details    # every failing element

Checks, as WCAG 2.2 measures them:
  text            4.5:1 against what is actually behind it
  large text      3:1   (24px and up, or 18.66px bold and up)
  control edges   3:1   the border of anything you press or type into, against
                        the ground around it (1.4.11 non-text contrast)
Colours are read by painting them onto a canvas, so oklch(), color-mix() and
transparency are measured as the browser draws them, not as written.

It opens the pages from public/ on disk (this-tab-only mode), so no server is
needed. Build first: python3 build/build.py. Exit code 1 if anything fails.
"""
import asyncio, json, os, sys
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MEASURE = r"""
() => {
  const cv = document.createElement('canvas'); cv.width = cv.height = 1;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  const rgba = (c) => { cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = c; cx.fillRect(0, 0, 1, 1);
    const d = cx.getImageData(0, 0, 1, 1).data; return [d[0], d[1], d[2], d[3] / 255]; };
  const over = (top, under) => { const a = top[3]; return [0, 1, 2].map(i => top[i] * a + under[i] * (1 - a)).concat([1]); };
  const lum = (c) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const pageBg = rgba(getComputedStyle(document.body).backgroundColor);
  const htmlBg = rgba(getComputedStyle(document.documentElement).backgroundColor);
  const canvasBg = htmlBg[3] > 0 ? htmlBg : (pageBg[3] > 0 ? pageBg : [255, 255, 255, 1]);
  const groundOf = (el) => {           // what is painted behind el, composited
    const stack = [];
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const cs = getComputedStyle(e);
      const c = rgba(cs.backgroundColor);
      if (c[3] > 0) stack.push(c);
      if (c[3] >= 1) break;
    }
    let g = canvasBg;
    for (let i = stack.length - 1; i >= 0; i--) g = over(stack[i], g);
    return g;
  };
  const visible = (el) => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && +cs.opacity > 0.05; };
  const effOpacity = (el) => { let o = 1; for (let e = el; e && e.nodeType === 1; e = e.parentElement) o *= +getComputedStyle(e).opacity; return o; };
  const label = (el) => (el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : ''));
  const out = [];
  // text
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  let n;
  while ((n = walker.nextNode())) {
    const t = n.textContent.trim(); if (!t) continue;
    const el = n.parentElement; if (!el || seen.has(el) || !visible(el)) continue;
    if (el.closest('[aria-hidden="true"], script, style, noscript, .cover, [data-decor]')) continue;
    seen.add(el);
    const cs = getComputedStyle(el);
    if (el.closest('button[disabled], [aria-disabled="true"], input[disabled]')) continue;   // exempt in WCAG
    let fg = rgba(cs.color); fg[3] *= effOpacity(el);
    const bg = groundOf(el);
    const fgc = over(fg, bg);
    const size = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight, 10) >= 700;
    const large = size >= 24 || (size >= 18.66 && bold);
    const need = large ? 3 : 4.5;
    const r = ratio(fgc, bg);
    if (r + 0.005 < need) out.push({ kind: 'text', r: +r.toFixed(2), need, el: label(el), text: t.slice(0, 50), size });
  }
  // placeholders, which are text a person has to read before typing
  document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach(el => {
    if (!visible(el) || !el.placeholder) return;
    const ph = rgba(getComputedStyle(el, '::placeholder').color);
    const bg = groundOf(el);
    const r = ratio(over(ph, bg), bg);
    if (r + 0.005 < 4.5) out.push({ kind: 'text', r: +r.toFixed(2), need: 4.5, el: label(el) + '::placeholder', text: el.placeholder.slice(0, 50), size: 0 });
  });
  // control edges
  document.querySelectorAll('button, input:not([type=hidden]), select, textarea, [role=button], .btn').forEach(el => {
    if (!visible(el) || el.disabled) return;
    const cs = getComputedStyle(el);
    const w = parseFloat(cs.borderTopWidth);
    const fill = rgba(cs.backgroundColor);
    const around = groundOf(el.parentElement || el);
    const border = rgba(cs.borderTopColor);
    if (border[3] === 0 && fill[3] === 0) return;     // a text-only button: its text is what is measured
    if (w >= 1 && cs.borderTopStyle !== 'none') {
      const edge = over(border, around);
      const inside = over(fill, around);
      const r = Math.max(ratio(edge, around), ratio(inside, around));
      if (r + 0.005 < 3) out.push({ kind: 'edge', r: +r.toFixed(2), need: 3, el: label(el), text: (el.innerText || el.value || el.placeholder || '').trim().slice(0, 40) });
    }
  });
  return out;
}
"""

PAGES = [('all-roles', ['reader', 'seller', 'courier', 'ops']), ('empty', ['reader'])]

# States a link crawl cannot reach: a cart and its checkout, a sheet asking
# before something destructive, the offer form, the admin's review page.
# ('go', screen, param) | ('act', prefix) | ('ask', prefix: opens the sheet)
SCRIPTED = {
    'reader': [('go', 'r.request', 'r2'), ('act', 'add:'), ('go', 'r.cart', ''), ('act', 'checkout'),
               ('act', 'setwhen:'), ('act', 'donewhen'), ('act', 'editdetails'),
               ('go', 'r.request', 'r1'), ('ask', 'closereq:'), ('go', 'x.settings', '')],
    'seller': [('go', 's.newoffer', 'r1'), ('go', 's.billing', ''), ('go', 's.stats', '')],
    'ops':    [('go', 'a.req', 'r7'), ('go', 'a.offer', 'o5'), ('go', 'a.apps', '')],
    'courier': [('go', 'c.jobs', '')],
}


async def screens_of(pg):
    return await pg.evaluate('''() => [...new Set([...document.querySelectorAll('[data-go]')]
        .map(e => e.getAttribute('data-go') + '|' + (e.getAttribute('data-p') || '')))]''')


async def audit():
    details = '--details' in sys.argv
    failures = {}
    count = 0
    async with async_playwright() as p:
        br = await p.chromium.launch()
        for theme in ['light', 'dark']:
            ctx = await br.new_context(viewport={'width': 390, 'height': 844}, color_scheme=theme)
            await ctx.route('**/fonts.g*/**', lambda r: r.abort())
            pg = await ctx.new_page()
            for page, roles in PAGES:
                for role in roles:
                    url = 'file://' + os.path.join(ROOT, 'public', page + '.html')
                    await pg.goto(url); await pg.wait_for_timeout(500)
                    await pg.evaluate('t => document.documentElement.setAttribute("data-theme", t)', theme)
                    if role != 'reader':
                        await pg.select_option('#roleSel', role); await pg.wait_for_timeout(300)
                    todo, done = await screens_of(pg), set()
                    todo = [s for s in todo if not s.startswith('x.')] + ['x.settings|', 'x.notifs|']
                    while todo and len(done) < 60:
                        s = todo.pop(0)
                        if s in done: continue
                        done.add(s)
                        scr, prm = s.split('|')
                        await pg.evaluate('''([s, p]) => { const b = document.createElement('button'); b.setAttribute('data-go', s);
                            if (p) b.setAttribute('data-p', p); document.body.appendChild(b); b.click(); b.remove(); }''', [scr, prm])
                        await pg.wait_for_timeout(120)
                        count += 1
                        for f in await pg.evaluate(MEASURE):
                            key = (theme, f['kind'], f['el'], f['text'][:30])
                            if key not in failures:
                                failures[key] = dict(f, theme=theme, where='%s:%s %s' % (page, role, scr))
                        # one level deeper: the detail pages this screen links to
                        if len(done) < 60:
                            fresh = [x for x in await screens_of(pg) if x not in done and x not in todo and not x.startswith('x.')]
                            todo.extend(fresh[:8])
                    # the scripted states for this role
                    await pg.goto(url); await pg.wait_for_timeout(400)
                    await pg.evaluate('t => document.documentElement.setAttribute("data-theme", t)', theme)
                    if role != 'reader':
                        await pg.select_option('#roleSel', role); await pg.wait_for_timeout(300)
                    for step in SCRIPTED.get(role, []):
                        if step[0] == 'go':
                            await pg.evaluate('''([s, p]) => { const b = document.createElement('button'); b.setAttribute('data-go', s);
                                if (p) b.setAttribute('data-p', p); document.body.appendChild(b); b.click(); b.remove(); }''', [step[1], step[2]])
                        else:
                            attr = 'data-act' if step[0] == 'act' else 'data-ask'
                            await pg.evaluate('''([a, pre]) => { const e = [...document.querySelectorAll('[' + a + ']')]
                                .find(x => x.getAttribute(a).startsWith(pre)); if (e) e.click(); }''', [attr, step[1]])
                        await pg.wait_for_timeout(250)
                        count += 1
                        for f in await pg.evaluate(MEASURE):
                            key = (theme, f['kind'], f['el'], f['text'][:30])
                            if key not in failures:
                                failures[key] = dict(f, theme=theme, where='%s:%s %s' % (page, role, ' '.join(step[:2])))
                    await pg.evaluate('() => { const d = document.getElementById("sheet"); if (d && d.open) d.close(); }')
            await ctx.close()
        await br.close()

    bad = list(failures.values())
    print('%d screen visits, %d distinct failures' % (count, len(bad)))
    by = {}
    for f in bad:
        by.setdefault((f['theme'], f['kind']), []).append(f)
    for (theme, kind), fs in sorted(by.items()):
        print('\n%s / %s: %d' % (theme, kind, len(fs)))
        for f in sorted(fs, key=lambda x: x['r'])[: (None if details else 12)]:
            print('  %5.2f < %-3s %-34s %-32s %s' % (f['r'], f['need'], f['el'][:34], repr(f['text'][:30]), f['where']))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(asyncio.run(audit()))
