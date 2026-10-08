"""Walk every screen with Russian selected and list what is still in English.

Rather than a hand-written path through the app — which breaks the moment a
label is translated, because the selectors were the labels — this crawls:
from each role's home it presses every tab, and on each screen it presses each
card, opener and button in turn, replaying the route from a fresh load. What it
cannot reach it says so.

Run it with:  python3 i18n/audit.py   (needs: pip install playwright)

Proper nouns are not translation debt: shop names, people's names, book titles
and their authors stay as they are in any language.
"""
import json, pathlib, re, sys
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
MASTER = HERE.parent / 'prototype' / 'shelfcall-all-roles.html'
TMP = HERE / '_audit.html'          # scratch, git-ignored
TODO = HERE / '_i18n_todo.json'     # the result, git-ignored

src = MASTER.read_text(encoding='utf-8')
TMP.write_text(
    "<!doctype html><html><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'></head><body>"
    + src + "</body></html>", encoding='utf-8')
url = TMP.as_uri()

PROPER = set("""Aram Books Nairi Grigor Dina Sergey Anna Lusine Vahe Yerevan Shelfcall
Mashtots Tumanyan Komitas Saryan Arshakunyats Frankenstein Mary Shelley Solaris
Stanislaw Stanisław Lem Bulgakov Mikhail Master Margarita Pillow Book Sei Shonagon
Shōnagon Norwegian Wood Haruki Murakami Jekyll Hyde Stevenson Penguin Progress Mir
Khudozhestvennaya Literatura Borges Chrysalids Anna Karenina Lev Tolstoy Yasunari
Kawabata Stalker Arkady Strugatsky Armenian Miniatures Dune Google Geist Sep Oct
Nov Dec Jan Feb Mar Apr Jun Jul Aug X""".split())

COLLECT = """() => {
  const out = [], seen = new Set();
  const push = t => { t = (t||'').replace(/\\s+/g,' ').trim();
                      if (t && !seen.has(t)) { seen.add(t); out.push(t); } };
  [document.querySelector('main'), document.getElementById('bar'),
   document.getElementById('tabbar'), document.getElementById('sheet')].forEach(root => {
    if (!root) return;
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let n; while ((n = w.nextNode())) push(n.textContent);
    root.querySelectorAll('input,textarea').forEach(el => push(el.getAttribute('placeholder')));
    root.querySelectorAll('[aria-label]').forEach(el => push(el.getAttribute('aria-label')));
    root.querySelectorAll('option').forEach(el => push(el.textContent));
  });
  return out;
}"""

LATIN = re.compile(r'[A-Za-z]')

def is_debt(s):
    if not LATIN.search(s):
        return False
    words = re.findall(r"[A-Za-z][A-Za-z'’-]*", s)
    rest = [w for w in words if w not in PROPER]
    if not rest:
        return False
    # initials and one short capitalised token are names, not copy
    rest = [w for w in rest if len(w) > 1]
    if not rest:
        return False
    if all(w[0].isupper() for w in rest) and len(rest) <= 3:
        return False
    return True

found = {}

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 390, "height": 844})
    pg.set_default_timeout(2500)

    def fresh(role):
        pg.goto(url); pg.wait_for_timeout(350)
        pg.click("[aria-label='Settings']"); pg.wait_for_timeout(250)
        pg.click("button:has-text('Русский')"); pg.wait_for_timeout(250)
        if role != 'reader':
            pg.select_option("#roleSel", role); pg.wait_for_timeout(300)
        else:
            pg.click("#tabbar button >> nth=0"); pg.wait_for_timeout(250)

    def grab(label):
        for s in pg.evaluate(COLLECT):
            if is_debt(s):
                found.setdefault(s, set()).add(label)

    # things worth pressing, in the order we try them
    OPENERS = ['.card-row', '.rowlist .row', '.opens', '.pick', '.stack-list .card button',
               'main .btn']

    def crawl(role, tabs):
        for ti in range(tabs):
            try:
                fresh(role)
                pg.click("#tabbar button >> nth=%d" % ti); pg.wait_for_timeout(300)
            except Exception:
                continue
            grab('%s tab%d' % (role, ti))
            # one level down: press each opener on this tab, one per replay
            for sel in OPENERS:
                n = pg.locator(sel).count()
                for i in range(min(n, 6)):
                    try:
                        fresh(role)
                        pg.click("#tabbar button >> nth=%d" % ti); pg.wait_for_timeout(250)
                        pg.locator(sel).nth(i).click(); pg.wait_for_timeout(300)
                        grab('%s tab%d %s#%d' % (role, ti, sel, i))
                        # and one level further, following the primary action
                        for j in range(3):
                            btn = pg.locator('main .btn')
                            if not btn.count(): break
                            btn.nth(0).click(); pg.wait_for_timeout(280)
                            grab('%s tab%d %s#%d>%d' % (role, ti, sel, i, j))
                    except Exception:
                        pass
        # the chrome screens
        for lbl, sel in [('notifs', "[aria-label='Notifications']"),
                         ('settings', "[aria-label='Settings']")]:
            try:
                fresh(role); pg.click(sel); pg.wait_for_timeout(300); grab(role + ' ' + lbl)
            except Exception:
                pass

    crawl('reader', 3)
    crawl('seller', 5)
    crawl('courier', 2)
    crawl('ops', 5)
    b.close()

TMP.unlink(missing_ok=True)

rows = sorted(found.items(), key=lambda kv: (-len(kv[1]), kv[0].lower()))
print('\nUNTRANSLATED STRINGS: %d\n' % len(rows))
for s, where in rows:
    print('%-3d %s' % (len(where), s[:130]))

json.dump([s for s, _ in rows], open(TODO, 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\n%d strings written to %s' % (len(rows), TODO.name))
