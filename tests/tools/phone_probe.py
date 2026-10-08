#!/usr/bin/env python3
"""
Phone probe for the Shelfcall prototype: the measured rules of CLAUDE.md §10
and the visual rules of §6, on every screen a role can reach, in hy, ru and en,
light and dark, at 390x844.

    python3 tests/tools/phone_probe.py                     # every role, language, theme
    python3 tests/tools/phone_probe.py --roles seller      # one role
    python3 tests/tools/phone_probe.py --langs hy --themes light
    python3 tests/tools/phone_probe.py --json out.json     # every finding, for a report

FAIL (a measured rule, §10):
  horizontal scroll at 390px · text under 12px (aria-hidden book covers excepted)
  a tap target under 36px · a flow screen's main button below 690px and not docked
  repeated identical text on one screen
WARN (needs a person, §6/§7):
  more than one solid primary button · a shadow outside the toast
  a border on something you cannot press · a tab bar on a flow screen

It opens public/*.html from disk (each page alone, no server), so build first:
python3 build/build.py. Screenshots of every failing screen go to
.shelfcall-check/ — look at the hy ones yourself. Exit code 1 if anything FAILs.
"""
import argparse, asyncio, json, os, re, sys
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, '.shelfcall-check')
ROLE_PAGE = {'reader': 'reader', 'seller': 'seller', 'courier': 'courier', 'ops': 'admin'}
FLOW = ['r.new', 'r.checkout', 'r.review', 's.newoffer', 's.pay', 's.location', 's.reg', 'x.auth', 's.apply', 'a.newshop']

# states a link crawl cannot reach (same idea as the contrast audit)
SCRIPTED = {
    'reader': [('go', 'r.new', ''), ('act', 'kind:concrete'), ('go', 'r.request', 'r2'), ('act', 'add:'),
               ('go', 'r.cart', ''), ('act', 'checkout'), ('go', 'x.settings', '')],
    'seller': [('go', 's.newoffer', 'r1'), ('go', 's.billing', ''), ('act', 'earn:all'), ('go', 's.pay', ''),
               ('go', 's.reviews', ''), ('act', 'newshop')],
    'courier': [('go', 'c.jobs', ''), ('go', 'c.done', '')],
    'ops': [('go', 'a.newshop', ''), ('go', 'a.shops', '')],
}

AUDIT = r"""
() => {
  const W = 390, USABLE = 690, MIN_TEXT = 12, MIN_TAP = 36;
  const fails = [], warns = [];
  const vis = (el) => { const s = getComputedStyle(el); if (s.display === 'none' || s.visibility === 'hidden' || +s.opacity === 0) return false;
    const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const lab = (el) => (el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '')
    + ' "' + ((el.getAttribute('aria-label') || el.innerText || el.value || el.placeholder || '').trim().replace(/\s+/g, ' ').slice(0, 40)) + '"');
  const scope = '#app, #dock, #tabbar, .bar, #sheet';
  const inScope = (el) => !!el.closest(scope);
  const sw = document.documentElement.scrollWidth;
  if (sw > W) fails.push(['hscroll', `page is ${sw}px wide at ${W}px`]);
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT), seenSmall = new Set();
  while (tw.nextNode()) {
    const n = tw.currentNode; if (!n.textContent.trim()) continue;
    const el = n.parentElement; if (!el || !vis(el) || !inScope(el) || seenSmall.has(el)) continue;
    if (el.closest('[aria-hidden="true"]')) continue;
    if (el.closest('svg')) {               // chart labels are SVG text: measured by their rendered size
      const px = el.getBoundingClientRect().height;
      if (px && px < MIN_TEXT * 0.72) { seenSmall.add(el); fails.push(['text<12', `chart label ~${px.toFixed(1)}px: "${el.textContent.trim().slice(0, 20)}"`]); }
      continue;
    }
    const px = parseFloat(getComputedStyle(el).fontSize);
    if (px < MIN_TEXT) { seenSmall.add(el); fails.push(['text<12', `${px}px ${lab(el)}`]); }
  }
  for (const el of document.querySelectorAll('button, a[href], input:not([type=hidden]), select, textarea, summary, [data-go], [data-act], [role=button]')) {
    if (!vis(el) || !inScope(el) || el.closest('svg')) continue;
    const r = el.getBoundingClientRect();
    if (Math.min(r.width, r.height) < MIN_TAP) fails.push(['tap<36', `${Math.round(r.width)}x${Math.round(r.height)} ${lab(el)}`]);
  }
  const solid = [...document.querySelectorAll('#app button.btn, #app a.btn, #dock button.btn, #dock a.btn')]
    .filter(b => vis(b) && !/\b(ghost|link|secondary|danger|quiet)\b/.test(b.className));
  if (solid.length > 1) warns.push(['primary>1', solid.length + ' solid buttons: ' + solid.slice(0, 4).map(lab).join(', ')]);
  const flow = window.__FLOW__.includes(window.SC_DEBUG && SC_DEBUG.screen());
  if (flow) {
    const main = solid.find(b => /\bwide\b/.test(b.className)) || solid[solid.length - 1];
    if (main) {
      const r = main.getBoundingClientRect(), docked = !!main.closest('#dock');
      if (!docked && r.bottom + window.scrollY > USABLE) fails.push(['button>690', `main button ends at ${Math.round(r.bottom + window.scrollY)}px: ${lab(main)}`]);
    }
    const tb = document.getElementById('tabbar');
    if (tb && vis(tb) && !tb.hidden) warns.push(['tabbar-on-flow', 'a tab bar on a flow screen']);
  }
  const counts = new Map();
  for (const el of document.querySelectorAll('#app h1, #app h2, #app h3, #app p, #app label > span, #app button, #dock button')) {
    if (!vis(el) || el.closest('.rowlist, .stack-list, .row, svg, [aria-hidden="true"]')) continue;
    const t = el.innerText.trim().replace(/\s+/g, ' ');
    if (t.length < 4 || /^[\d\s.,:֏%·←→-]+$/.test(t)) continue;
    counts.set(t, (counts.get(t) || 0) + 1);
  }
  for (const [t, c] of counts) if (c > 1) fails.push(['repeat', `x${c} "${t.slice(0, 60)}"`]);
  const press = 'a,button,input,select,textarea,summary,label,[data-go],[data-act],[data-ask],[role=button]';
  for (const el of document.querySelectorAll('#app *, #dock *')) {
    if (!vis(el)) continue;
    const s = getComputedStyle(el);
    if (s.boxShadow && s.boxShadow !== 'none' && !el.closest('.toast')) warns.push(['shadow', lab(el)]);
    const b = ['Top', 'Right', 'Bottom', 'Left'].every(k => parseFloat(s['border' + k + 'Width']) > 0 && s['border' + k + 'Style'] !== 'none');
    /* a Card, an Item list and an Alert carry a border in shadcn's own anatomy (§7) */
    if (b && !el.matches(press) && !el.closest(press) && !el.matches('input, textarea, select, .card, .rowlist, .note, .codebox'))
      warns.push(['border-not-button', lab(el)]);
  }
  return { fails, warns };
}
"""


async def screens_of(pg):
    return await pg.evaluate('''() => [...new Set([...document.querySelectorAll('#app [data-go], #tabbar [data-go]')]
        .map(e => e.getAttribute('data-go') + '|' + (e.getAttribute('data-p') || '')))]''')


async def goto(pg, scr, prm):
    await pg.evaluate('''([s, p]) => { const b = document.createElement('button'); b.setAttribute('data-go', s);
        if (p) b.setAttribute('data-p', p); document.body.appendChild(b); b.click(); b.remove(); }''', [scr, prm])
    await pg.wait_for_timeout(120)


async def act(pg, pre):
    await pg.evaluate('''(pre) => { const e = [...document.querySelectorAll('[data-act]')].find(x => x.getAttribute('data-act').startsWith(pre));
        if (e) { if (e.click) e.click(); else e.dispatchEvent(new MouseEvent('click', { bubbles: true })); }
        else { const b = document.createElement('button'); b.setAttribute('data-act', pre); document.body.appendChild(b); b.click(); b.remove(); } }''', pre)
    await pg.wait_for_timeout(150)


async def probe(args):
    os.makedirs(OUT, exist_ok=True)
    findings = []
    visits = 0
    async with async_playwright() as p:
        br = await p.chromium.launch()
        for theme in args.themes:
            ctx = await br.new_context(viewport={'width': 390, 'height': 844}, color_scheme=theme,
                                       is_mobile=True, has_touch=True, timezone_id='Asia/Yerevan')
            await ctx.route('**/fonts.g*/**', lambda r: r.abort())
            await ctx.add_init_script('window.__FLOW__ = %s;' % json.dumps(FLOW))
            for role in args.roles:
                for lang in args.langs:
                    pg = await ctx.new_page()
                    await pg.goto('file://' + os.path.join(ROOT, 'public', ROLE_PAGE[role] + '.html'))
                    await pg.wait_for_timeout(500)
                    await act(pg, 'lang:' + lang)
                    states = []
                    todo, done = await screens_of(pg), set()
                    while todo and len(done) < args.max:
                        s = todo.pop(0)
                        if s in done: continue
                        done.add(s); scr, prm = s.split('|')
                        await goto(pg, scr, prm)
                        states.append(('go', scr, prm))
                        await audit_here(pg, findings, theme, role, lang, s)
                        visits += 1
                        fresh = [x for x in await screens_of(pg) if x not in done and x not in todo]
                        todo.extend(fresh[:8])
                    for step in SCRIPTED.get(role, []):
                        if step[0] == 'go': await goto(pg, step[1], step[2])
                        else: await act(pg, step[1])
                        await audit_here(pg, findings, theme, role, lang, ' '.join(x for x in step[1:] if x))
                        visits += 1
                    await pg.close()
            await ctx.close()
        await br.close()
    return findings, visits


async def audit_here(pg, findings, theme, role, lang, where):
    res = await pg.evaluate(AUDIT)
    screen = await pg.evaluate('() => SC_DEBUG.screen()')
    shot = None
    for kind, items in (('FAIL', res['fails']), ('WARN', res['warns'])):
        for rule, detail in items:
            if kind == 'FAIL' and shot is None:
                shot = os.path.join(OUT, '%s.%s.%s.%s.png' % (role, re.sub(r'[^a-z0-9]+', '_', screen), lang, theme))
                await pg.screenshot(path=shot, full_page=True)
            findings.append({'kind': kind, 'rule': rule, 'detail': detail, 'role': role, 'screen': screen,
                             'lang': lang, 'theme': theme, 'via': where,
                             'shot': os.path.relpath(shot, ROOT) if (shot and kind == 'FAIL') else None})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--roles', nargs='+', default=['reader', 'seller', 'courier'], choices=list(ROLE_PAGE))
    ap.add_argument('--langs', nargs='+', default=['hy', 'ru', 'en'])
    ap.add_argument('--themes', nargs='+', default=['light', 'dark'], choices=['light', 'dark'])
    ap.add_argument('--max', type=int, default=60, help='screens crawled per role and language')
    ap.add_argument('--json', help='write every finding to this file')
    ap.add_argument('--details', action='store_true', help='print every occurrence, not one line per rule and screen')
    args = ap.parse_args()
    if not os.path.exists(os.path.join(ROOT, 'public', 'reader.html')):
        sys.exit('public/ is missing: run python3 build/build.py first')
    findings, visits = asyncio.run(probe(args))
    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f: json.dump(findings, f, ensure_ascii=False, indent=1)
    # one line per (kind, rule, role, screen), with where it happens
    groups = {}
    for x in findings:
        k = (x['kind'], x['rule'], x['role'], x['screen'])
        g = groups.setdefault(k, {'n': 0, 'langs': set(), 'themes': set(), 'eg': x['detail'], 'shot': x['shot']})
        g['n'] += 1; g['langs'].add(x['lang']); g['themes'].add(x['theme'])
        if x['shot'] and not g['shot']: g['shot'] = x['shot']
    nf = sum(1 for k in groups if k[0] == 'FAIL')
    print('%d screen visits · %d FAIL groups · %d WARN groups' % (visits, nf, len(groups) - nf))
    for k in sorted(groups, key=lambda k: (k[0] != 'FAIL', k[2], k[1], k[3])):
        g = groups[k]
        print('%s %-16s %-8s %-12s %s/%s  x%d  %s%s' % (k[0], k[1], k[2], k[3], ','.join(sorted(g['langs'])),
              ','.join(sorted(g['themes'])), g['n'], g['eg'][:90], ('  [' + g['shot'] + ']') if g['shot'] else ''))
    if args.details:
        for x in findings: print(json.dumps(x, ensure_ascii=False))
    sys.exit(1 if nf else 0)


if __name__ == '__main__':
    main()
