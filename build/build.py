#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the deployable site from the one master file.

    python3 build/build.py

Reads   prototype/shelfcall-all-roles.html   (the only file you edit)
        build/landing.html                   (the site's front page)
        docs/*.html                          (spec, audit, supply test)
Writes  public/                              (everything Vercel serves)

        public/index.html        front page, links to every build
        public/all-roles.html    every role, with the role switcher
        public/reader.html       reader only
        public/seller.html       bookseller only
        public/courier.html      courier only
        public/admin.html        Shelfcall team (ops) only
        public/empty.html        nothing filled in, switcher kept, for testing
        public/docs/*.html       the documents, as whole pages

Each single-role build is the master with the role switcher cut out, the role
pinned, the opening screen changed, and some seed data appended so the app
opens on something worth looking at.

public/ is generated. Never edit it by hand; run this script and commit the
result. Vercel serves public/ as it is, with no build step of its own.
"""

import glob, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MASTER = os.path.join(ROOT, 'prototype', 'shelfcall-all-roles.html')
LANDING = os.path.join(HERE, 'landing.html')
DOCS = os.path.join(ROOT, 'docs')
OUT = os.path.join(ROOT, 'public')

# ---------------------------------------------------------------- anchors
# Matched by pattern rather than by exact text, so adding a role or a class to
# the top bar does not break the build. If one stops matching, the build stops
# and says which.

# the <span class="role"> ... <select id="roleSel"> ... </select></span> in the top bar
ROLE_SWITCHER = re.compile(
    r"""^[ \t]*'<span class="role">.*?</select></span>'\+\n""", re.S | re.M)

# the change listener that reacts to the switcher
ROLE_CHANGE_HANDLER = re.compile(
    r"""^[ \t]*if \(e\.target\.id === 'roleSel'\)\{\n.*?^[ \t]*\}\n""", re.S | re.M)

# the sentence under the footer's Light / Busy switch
FOOTER_TEXT = re.compile(
    r"""esc\('Prototype with sample data — every role is you\. ' \+.*?\)\)\+'</p>';""", re.S)

ROLE_DEFAULT = "    me: { role:'reader',"
SCREEN_DEFAULT = "  var view = { screen:'r.requests',"
FIRST_RENDER = "  render();\n})();"

HOME = {'reader': 'r.requests', 'seller': 's.feed', 'courier': 'c.jobs',
        'ops': 'a.work'}

# ---------------------------------------------------------------- seeds
# Appended just before the first render(). They mutate the same `db` the
# master defines, so they can only use helpers the master already declared.

SELLER_SEED = r"""
  /* --- seed: a finished order, and one past its confirm hour --- */
  (function(){
    /* one offer the reader has already read and one sitting in their cart,
       so the narrowed edit rules are reachable without staging a whole flow */
    offer('o1').status = 'seen';
    offer('o5') && (offer('o5').status = 'in_cart');
    offer('o4').status='done_sold'; req('r2').status='fulfilled';
    db.requests.push({ id:'r9', reader:'sergey', kind:'concrete',
      text:'Solaris, the Mir printing if you have it.', title:'Solaris',
      author:'Stanisław Lem', budget:4000, city:'Yerevan', cond:'any',
      posted: now - 12*DAY, status:'fulfilled' });
    db.offers.push({ id:'o9', req:'r9', seller:'aram', loc:'mash', title:'Solaris',
      author:'Stanisław Lem', year:1988, pub:'Mir', cond:'good used', price:3400,
      note:'', status:'done_sold', sent: now - 11*DAY });
    db.orders.push({ id:1038, reader:'sergey', closed:['r9'], released:0,
      name:'Sergey', phone:'+374 ** ** ** **', delivery:'pickup', fee:0, books:3400, total:3400, subs:[
      { no:'1038-A', seller:'aram', loc:'mash', items:['o9'], delivery:'pickup',
        fee:0, books:3400, total:3400, status:'completed', code:'5120',
        by:'code', reviewed:true, doneAt: now - 10*DAY } ] });
    /* a second finished order, unrated, so the one-tap review ask is live */
    db.requests.push({ id:'r10', reader:'dina', kind:'concrete',
      text:'The Pillow Book — any decent edition.', title:'The Pillow Book',
      author:'Sei Shōnagon', budget:9000, city:'Yerevan', cond:'any',
      posted: now - 9*DAY, status:'fulfilled' });
    db.offers.push({ id:'o10', req:'r10', seller:'aram', loc:'mash', title:'The Pillow Book',
      author:'Sei Shōnagon', year:2006, pub:'Penguin', cond:'good used', price:7200,
      note:'', status:'done_sold', sent: now - 8*DAY });
    db.orders.push({ id:1039, reader:'dina', closed:['r10'], released:0, name:'Dina',
      phone:'+374 91 ** ** **', addr:'Komitas 24, apt 7',
      delivery:'courier', fee:db.deliveryFee, books:7200, total:7200+db.deliveryFee, subs:[
      /* delivered, counted against the commission, and NOT yet paid for: the
         state the shop could not see before the earnings screen existed */
      { no:'1039-A', seller:'aram', loc:'mash', items:['o10'], delivery:'courier',
        fee:0, books:7200, total:7200, status:'completed', by:'courier',
        courier:'vahe', payMode:'after', doneAt: now - 2*DAY } ] });

    /* --- a little history, so "by day and by month" has something to show ---
       Three more finished sales spread over this month and last, one of them
       paid by a courier who says so while the shop has not agreed yet. */
    (function(){
      var HIST = [
        ['o21','Anna Karenina','Lev Tolstoy', 5200, 1041, 'pickup',  6*DAY,  'paid'],
        ['o22','The Master of Go','Yasunari Kawabata', 4100, 1042, 'courier', 6*DAY, 'claimed'],
        ['o23','Stalker','Arkady Strugatsky', 2800, 1043, 'courier', 34*DAY, 'paid'],
        ['o24','Armenian Miniatures','', 16000, 1044, 'pickup', 41*DAY, 'paid']
      ];
      HIST.forEach(function(row, i){
        var oid = row[0], no = row[4]+'-A', at = now - row[6];
        db.offers.push({ id:oid, req:'r9', seller:'aram', loc: i%2 ? 'tum' : 'mash',
          title:row[1], author:row[2], cond:'good used', price:row[3],
          note:'', status:'done_sold', sent: at - DAY });
        db.orders.push({ id:row[4], reader:'sergey', closed:[], released:0,
          name:'Sergey', phone:'+374 ** ** ** **',
          delivery:row[5], fee:0, books:row[3], total:row[3], subs:[
          { no:no, seller:'aram', loc: i%2 ? 'tum' : 'mash', items:[oid],
            delivery:row[5], fee:0, books:row[3], total:row[3],
            status:'completed', by: row[5]==='pickup' ? 'code' : 'courier',
            reviewed:true, doneAt: at,
            shopConfirmedCash: row[7]==='paid' && row[5]==='courier' } ] });
        if (row[5]==='courier')
          db.ledger.push({ at: at + 3600e3, amount: row[3], from:'courier', to:'shop',
                           sub: no, note:'settled after delivery', pending:false });
      });
    })();
    /* a live COURIER order, so the shop can see that it sees nothing.
       (Was #1044 and the next one #1041, which the history above already
       uses - two orders with one number. They are 1045 and 1046 now.) */
    db.orders.push({ id:1045, reader:'dina', closed:[], released:0, name:'Dina',
      phone:'+374 91 22 33 44', addr:'Komitas 24, apt 7',
      delivery:'courier', fee:db.deliveryFee, books:4500, total:4500+db.deliveryFee, subs:[
      { no:'1045-A', seller:'aram', loc:'mash', items:['o1'], delivery:'courier',
        fee:0, books:4500, total:4500, status:'placed',
        payMode:'after', placedAt: now - 20*60*1000 } ] });
    /* and a pickup five hours old: past its one open hour to confirm */
    db.orders.push({ id:1046, reader:'dina', closed:['r2'], released:0, name:'Dina',
      phone:'+374 91 ** ** **', addr:'Komitas 24, apt 7', delivery:'pickup', fee:0, books:6000, total:6000, subs:[
      { no:'1046-A', seller:'aram', loc:'tum', items:['o4'], delivery:'pickup',
        fee:0, books:6000, total:6000, status:'placed', code:'7314',
        placedAt: now - 5*HOUR } ] });
    db.seq.ord = 1047;
  })();
"""

COURIER_SEED = r"""
  /* --- seed: one job to collect, one on you, one settled --- */
  (function(){
    offer('o1').status='done_sold'; offer('o2').status='done_not_chosen';
    offer('o3').status='done_not_chosen'; req('r1').status='fulfilled';
    offer('o4').status='done_sold'; req('r2').status='fulfilled';
    db.requests.push({ id:'r9', reader:'sergey', kind:'concrete',
      text:'Solaris, the Mir printing if you have it.', title:'Solaris',
      author:'Stanisław Lem', budget:4000, city:'Yerevan', cond:'any',
      posted: now - 12*DAY, status:'fulfilled' });
    db.offers.push({ id:'o9', req:'r9', seller:'nairi', loc:'tum12', title:'Solaris',
      author:'Stanisław Lem', year:1988, cond:'good used', price:3400,
      note:'Cover worn at the corners, text block sound.', status:'done_sold',
      sent: now - 11*DAY });
    db.orders.push({ id:1040, reader:'sergey', closed:['r9'], released:0,
      name:'Sergey', phone:'+374 93 44 55 66', addr:'Saryan 18, apt 3',
      delivery:'courier', fee:db.deliveryFee, books:3400, total:3400+db.deliveryFee, subs:[
      { no:'1040-A', seller:'nairi', loc:'tum12', items:['o9'], delivery:'courier',
        fee:0, books:3400, total:3400, status:'completed', by:'courier',
        courier:'vahe', payMode:'onpickup', paidShop:true, settled:true } ] });
    db.orders.push({ id:1042, reader:'dina', closed:['r1'], released:2, name:'Dina',
      phone:'+374 91 22 33 44', addr:'Komitas 24, apt 7',
      note:'Second entrance, the gate code is 4417. Call rather than ring — the bell is broken.',
      delivery:'courier', fee:db.deliveryFee, books:4500, total:4500+db.deliveryFee, subs:[
      { no:'1042-A', seller:'aram', loc:'mash', items:['o1'], delivery:'courier',
        fee:0, books:4500, total:4500, status:'ready', payMode:'after',
        placedAt: now - 3*HOUR } ] });
    /* this one the buyer pinned to a window, so the courier is holding it */
    db.orders.push({ id:1043, reader:'dina', closed:['r2'], released:0, name:'Dina',
      phone:'+374 91 22 33 44', addr:'Komitas 24, apt 7',
      when:{ kind:'slot', at: (function(){ var t=new Date(now); t.setDate(t.getDate()+1); t.setHours(18,0,0,0); return t.getTime() })() },
      delivery:'courier', fee:db.deliveryFee, books:6000, total:6000+db.deliveryFee, subs:[
      { no:'1043-A', seller:'aram', loc:'tum', items:['o4'], delivery:'courier',
        fee:0, books:6000, total:6000, status:'shipped', courier:'vahe',
        payMode:'after', placedAt: now - 26*HOUR } ] });
    db.seq.ord = 1044;
    /* the settled job as ledger entries, not booleans */
    ledgerAdd(3400, 'courier', 'shop',   '1040-A', 'paid at pickup');
    ledgerAdd(3400 + db.deliveryFee, 'buyer', 'courier', '#1040', 'cash on delivery');
  })();
"""

EMPTY_SEED = r"""
  /* --- seed: nothing at all -----------------------------------------------
     A build for testing with real people. There are no requests, no offers,
     no orders, no cart and no history, and the reader has given us no name,
     phone or address - exactly the state a person is in the first time they
     open this. Everything they see, they will have put there.

     What is KEPT is the other side of the market: the bookshops with their
     branches and opening hours, and one courier. Without them there is nobody
     to answer a request, and the tester would be talking to an empty city.
     The role switcher stays in this build so one person can post as a reader,
     answer as a shop and deliver as the courier. */
  (function(){
    db.requests = []; db.offers = []; db.orders = []; db.cart = [];
    db.ledger = []; db.alerts = [];
    db.seq = { r: 1, o: 1, ord: 1001 };
    Object.keys(db.readers).forEach(function(k){
      var rd = db.readers[k];
      rd.name = ''; rd.phone = ''; rd.address = ''; rd.courierNote = '';
    });
    db.account.state = 'trial'; db.account.trialStart = now;
    db.account.claim = null; db.account.reject = null; db.account.claimStrikes = 0;
    db.notifSeen = now;
  })();
"""

EMPTY_FOOTER = ('Nothing is filled in: no requests, no orders, no history, and no '
                'name, phone or address until you type them. Switch roles above to '
                'answer your own request as a bookshop and deliver it as the courier. '
                'Reload to wipe it.')

# (file, role, title, keep switcher, seed, footer override)
BUILDS = [
    ('all-roles', 'reader',  'Shelfcall Prototype',          True,  None,         None),
    ('reader',    'reader',  'Shelfcall for Readers',        False, None,         None),
    ('seller',    'seller',  'Shelfcall for Booksellers',    False, SELLER_SEED,  None),
    ('courier',   'courier', 'Shelfcall for Couriers',       False, COURIER_SEED, None),
    ('admin',     'ops',     'Shelfcall Admin',              False, None,         None),
    ('empty',     'reader',  'Shelfcall — empty, for testing', True, EMPTY_SEED, EMPTY_FOOTER),
]

DOC_HEAD = (
    '<!doctype html>\n<html lang="en">\n<head>\n'
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
    '<meta name="color-scheme" content="light dark">\n'
    '<meta name="robots" content="noindex">\n'
    '</head>\n<body>\n')
DOC_TAIL = '\n</body>\n</html>\n'


def whole_document(fragment):
    """The master and the docs are FRAGMENTS: published as artifacts, the host
    supplies the doctype, the charset and the viewport. Served from Vercel,
    nothing supplies them - without a doctype the page renders in quirks mode,
    and without a declared charset every dash, bullet and Cyrillic letter can
    turn into mojibake. So everything in public/ is written as a whole page."""
    if fragment.lstrip().lower().startswith('<!doctype'):
        return fragment
    return DOC_HEAD + fragment + DOC_TAIL


def js_string(text):
    return "'" + text.replace('\\', '\\\\').replace("'", "\\'") + "'"


def need(anchor, src, label):
    found = anchor.search(src) if hasattr(anchor, 'search') else anchor in src
    if not found:
        sys.exit('build.py: could not find the %s anchor in the master.\n'
                 'Did the top bar, the footer or the start-up code change? '
                 'Update the anchor in build/build.py.' % label)


def build(src, role, title, keep_switcher, seed, footer):
    s = src
    s = s.replace('<title>Shelfcall Prototype</title>', '<title>%s</title>' % title, 1)
    if not keep_switcher:
        s = ROLE_SWITCHER.sub('', s, count=1)
        s = ROLE_CHANGE_HANDLER.sub('', s, count=1)
    s = s.replace(ROLE_DEFAULT, "    me: { role:'%s'," % role, 1)
    s = s.replace(SCREEN_DEFAULT, "  var view = { screen:'%s'," % HOME[role], 1)
    if footer:
        s = FOOTER_TEXT.sub(lambda m: "esc(%s)+'</p>';" % js_string(footer), s, count=1)
        # the Light half of the footer switch has nothing in it in this build
        s = s.replace(": 'a few requests, offers and orders')", ": 'nothing until you add it')", 1)
    if seed:
        s = s.replace(FIRST_RENDER, seed + '\n' + FIRST_RENDER, 1)
    return whole_document(s)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print('wrote %-28s %7d bytes' % (os.path.relpath(path, ROOT).replace(os.sep, '/'),
                                       len(text.encode('utf-8'))))


def main():
    with open(MASTER, encoding='utf-8') as f:
        src = f.read()

    need(ROLE_SWITCHER, src, 'role switcher')
    need(ROLE_CHANGE_HANDLER, src, 'role change handler')
    need(FOOTER_TEXT, src, 'footer text')
    for text, label in [(ROLE_DEFAULT, 'default role'), (SCREEN_DEFAULT, 'first screen'),
                        (FIRST_RENDER, 'first render')]:
        need(text, src, label)

    # start clean, so a build that was dropped does not linger on the site
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)

    for name, role, title, keep_switcher, seed, footer in BUILDS:
        html = build(src, role, title, keep_switcher, seed, footer)
        if keep_switcher:
            assert 'id="roleSel"' in html, 'the %s build needs its role switcher' % name
        else:
            assert 'roleSel' not in html, 'role switcher survived in %s' % name
        write(os.path.join(OUT, name + '.html'), html)

    with open(LANDING, encoding='utf-8') as f:
        write(os.path.join(OUT, 'index.html'), f.read())

    # a prototype full of sample people and shops is not for search engines
    write(os.path.join(OUT, 'robots.txt'), 'User-agent: *\nDisallow: /\n')

    for doc in sorted(glob.glob(os.path.join(DOCS, '*.html'))):
        with open(doc, encoding='utf-8') as f:
            write(os.path.join(OUT, 'docs', os.path.basename(doc)), whole_document(f.read()))


if __name__ == '__main__':
    main()
