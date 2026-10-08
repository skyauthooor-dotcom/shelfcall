# Shelfcall — source

## The name

Chosen by Tigran, recorded here exactly as written:

```
The Book Point
Точка книги
Կետ գրքի
```

Nothing in the code has been renamed yet — the prototype, the artifacts and the
spec still say Shelfcall, which is a working name. Renaming is one pass over
the shell, the titles, the footer and the four HTML files, plus the artifact
titles; say the word and it is done.


A reverse marketplace for books. Readers describe what they want; booksellers
answer with real copies off their shelves; a courier delivers and takes the cash;
the Shelfcall team (admin) approves shops and watches requests, orders and cash.

Everything here is plain HTML, CSS and JavaScript. No framework, no package
manager, no dependencies except Google Fonts. The only tooling is a few Python
scripts with no third-party packages (the i18n audit and the tracker need
Playwright and openpyxl, and are optional).

```
prototype/
  shelfcall-all-roles.html   ← the only file you edit. All four roles, with a switcher.
build/
  build.py                   ← builds public/ from the master
  landing.html               ← the site's front page
  build_tracker.py           ← makes the supply-test .xlsx tracker (into out/)
public/                      ← GENERATED. What Vercel serves. Never edit by hand.
  index.html                 ← front page, links to everything below
  all-roles.html             ← every role, with the switcher
  reader.html  seller.html  courier.html  admin.html   ← one role each
  empty.html                 ← nothing filled in, switcher kept, for testing
  docs/                      ← the three documents as whole pages
i18n/
  ru.py                      ← the Russian dictionary: whole strings and patterns
  build_i18n.py              ← writes it into the master's RU_X / RU_P tables
  audit.py                   ← crawls every screen in Russian and lists what is left
docs/
  spec.html                  ← v0.3 · 40 stories, 7 flows, 26 screens, data model, settled decisions
  audit.html                 ← 16 edge cases, each with its status; the drift table, now closed
  supply-test.html           ← the two-week bookseller test, scripts and go/no-go gate
design-system/               ← tokens, component notes and previews (reference only)
api/world.js                 ← the shared test world (Vercel function + Redis)
api/_sync-core.js            ← its merge rules; the master carries an identical copy
tests/                       ← unit tests, end-to-end flows, contrast audit (see Testing)
test.bat                     ← Windows: run every check in one go
vercel.json  .vercelignore   ← deploy settings: serve public/, clean URLs, noindex
push.bat                     ← Windows: rebuild, commit and push to GitHub in one go
```

## Working on it

Edit `prototype/shelfcall-all-roles.html`, then rebuild the site:

```bash
python3 build/build.py        # on Windows: python build\build.py  (or py build\build.py)
```

That rewrites everything in `public/`, so you can open the pages locally.
Vercel runs the same build on every deploy (`buildCommand` in `vercel.json`),
so what goes live always comes from the master, even if `public/` in git is
out of date. The master is the source of truth; the switcher in its top bar is
a prototype control that the build strips out of the single-role pages.

The master is a **fragment** (no doctype, no `<head>`), because that is what an
artifact is published as. The build wraps every page in `public/` as a whole
document with a charset and viewport, so do not open the master straight from
disk to judge it — open `public/all-roles.html`.

To try the site locally exactly as Vercel will serve it, open
`public/index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8000 --directory public     # then http://localhost:8000
```

## Deploying

The site is static pages plus one small function (`api/world.js`). Vercel
builds the pages with Python, which its build machines already have.

1. Push this folder to a GitHub repository (with `public/` committed). On
   Windows, double-click `push.bat`: it rebuilds `public/` (if Python is
   installed), commits whatever changed and pushes to
   `github.com/skyauthooor-dotcom/shelfcall`. Run it again after every change.
2. In Vercel: **Add New → Project**, import the repository.
3. Leave **Framework Preset** on *Other*. `vercel.json` already sets the build
   command (`python3 build/build.py`) and points Vercel at `public/`.
4. Deploy. Every push to the main branch redeploys; every other branch gets
   its own preview URL, which is the easy way to test a change before it goes
   to the shared link.

`vercel.json` turns on clean URLs (`/reader` rather than `/reader.html`) and
sends `X-Robots-Tag: noindex` on every page, with a `robots.txt` to match —
the prototype is full of sample people, phone numbers and shops and should not
turn up in search. Nothing persists on the server: each tester's state lives
in their own browser tab and resets on reload.

## The shared test

On the deployed site every page joins a shared **world**, so the roles reach
each other across phones: a reader posts a request on one phone, the admin
approves it on a laptop, the bookshop sees it in its feed on a third device
and answers, and the reader sees the offer arrive.

- `api/world.js` is a Vercel function that keeps each world in Redis (Upstash,
  through its REST API — no npm packages). It needs the **Upstash for Redis**
  integration on the Vercel project; the integration adds the environment
  variables (`KV_REST_API_URL` / `KV_REST_API_TOKEN`) by itself.
- `/all-roles`, `/reader`, `/seller`, `/courier` and `/admin` share the world
  called `main`, which starts with the sample data. `/empty` has its own world,
  `empty`, which starts with no requests or orders. Add `?world=anything` to
  any page to start a separate world for a separate group of testers.
- The footer of every page says *Shared test* and has **Start over for
  everyone**, which puts that world back to how it started, on every phone.
- Everyone playing the reader is Dina, everyone playing the bookseller is Aram
  Books — there are no accounts in a prototype. Who you are, your theme, your
  language and what you have read stay on your own device.
- Changes are sent after every action, field by field: the admin approving a
  request and a shop marking it seen are two edits that both survive. Only
  two people changing the very same field collide, and then the later one
  wins. Each page checks for other people's changes every 3 seconds (every
  15 while its tab is in the background, and at once when you come back to
  it), and does not redraw while you are typing or a sheet is open.
- Photos are stored as small JPEGs (640px) inside the record, so the shop's
  photo reaches the reader's phone.
- With no database (opened from disk, as an artifact, or before Redis is
  added) a page falls back to the old behaviour: this tab only, with the
  Light / Busy switch in the footer.

This is a test harness. Anyone with the link can change a world, there is no
sign-in and nothing is private. None of it should be carried into the real
app, where the server owns the rules (see the project instructions).

The sync code is one block in the master, between `shared test world` and
`end of shared test world`. The screens know nothing about it: they change
`db` and call `render()` as before, and the block sends the difference. The
merge rules themselves are in `api/_sync-core.js`; the master carries an
identical copy between the `sync-core` markers, and both the build and the
unit tests stop if the two differ.

## Testing

```bash
python3 build/build.py                    # build first: the tests use public/
node --test tests/*.test.js               # merge rules and the server (no packages)
python3 tests/e2e/flows.py                # every cross-role flow, one browser per role
python3 tests/tools/contrast.py           # contrast of every screen, light and dark
```

On Windows, `test.bat` runs all four. The end-to-end flows and the contrast
audit need Playwright once: `pip install playwright` and
`python -m playwright install chromium`.

The flows start `tests/tools/devserver.js`, which serves `public/` the way
Vercel does and runs `api/world.js` against an in-memory Redis. Each role is
its own browser, so it is three or four phones talking to one server:

- a request reaches the shop only after the admin approves it, on a shop page
  that was open all along, and the approval survives the shop opening it;
- a request or an offer sent back never reaches the other side;
- an offer with a photo reaches the reader, and the reader opening it shows
  as "seen" for the shop;
- a pickup order from cart to handover code to review, and a courier order
  from cart to collection to delivery and the cash in the ledger;
- the reader cancelling, the shop removing an offer, the courier failing a
  delivery, the reader closing a request;
- a shop tab left in the background still receiving the approved request;
- two phones writing at once, typing never wiped by an update, start over for
  everyone, separate worlds, and every page still working opened from disk.

The contrast audit checks text (4.5:1, 3:1 when large), placeholders and the
edge of everything you can press (3:1), measured as the browser paints it.

## Light and dark

Light, Dark or Match my phone is remembered on the device for every page of
the site, applied before the first paint, and the browser's own controls
(scrollbars, the list a `<select>` opens) follow it.

## How the prototype is put together

One file, three sections: `<style>` at the top, an empty `<main>`, and one
`<script>` holding everything.

- **`db`** — the entire world as a plain object: readers, sellers with their
  locations, requests, offers, cart, orders, courier, account state. In memory
  only. Reload and it resets.
- **`view`** — `{ screen, p, draft, open, toast }`. That is the whole router.
- **`db.ledger`** — every cash movement as a row, `{at, amount, from, to, sub, note, pending}`.
  Nothing about money is a boolean; every figure on the courier's and the shop's
  money screens is a sum over these.
- **`SCREENS`** — a map of screen id to a function returning an HTML string.
  `r.*` reader, `s.*` seller, `c.*` courier, `a.*` admin, `x.*` shared.
- **`render()`** — calls the current screen function and sets `innerHTML`.
- One document click listener reads `data-go` (navigate), `data-act`
  (do something), `data-ask` (ask before doing something destructive).

To add a screen: write `function scrThing(){ return '<h1>…</h1>' }`, add it to
`SCREENS`, point a button at it with `data-go="x.thing"`.

## What it is and is not

It is a **prototype**: the flows are real and the state is real, so the
closing rules, the cart flags, the handover code and the courier ledger all
behave as specified. Photos are held as object URLs on the device.

It is **not the product**: no accounts, no payments, and the only server is
the shared test world described above — a test harness, not a backend. Nothing here should be carried into production except the screen
designs, the copy and the state machines.

## The clocks

A dozen timed rules are specified, and none of them can be implemented in a
prototype with no server. The rule from `docs/spec.html`, §07, is:

> **Derive for display, queue for consequence.**

Four are a query at read time and cannot silently fail — the 72-hour fallback
pool, the review edit window, free-month status and payment overdue. The rest
produce a consequence and need one worker over one table:

```
scheduled_tasks(kind, entity_id, due_at, done_at, attempts, last_error)
```

In the prototype they are computed at render, which is why the bookseller build
seeds one order already past its confirm hour — otherwise that state is
unreachable.

## Russian

758 whole strings and 269 patterns in `i18n/ru.py`. They are applied
**after** render, by walking the text nodes of the screen, rather than by
wrapping every literal in the source. A deliberate trade — it keeps ~600 call
sites out of the diff, it cannot miss a string that only one branch produces,
and a miss is *visible* rather than silent: an untranslated string simply stays
in English, which is the policy the settings screen already promised.

Three things make the tables small enough to maintain:

- a pattern carries numbers, names and dates through untouched, so `open 5
  days` and `open 9 days` are one entry rather than one per number;
- `$*1` sends a capture back through the dictionary, so a phrase inside a
  phrase translates too (`posted 2 days ago`);
- `{1:день|дня|дней}` picks the Russian plural from capture 1, which is why
  nothing here reads "1 предложений";
- and a line the app built by joining facts with ` · ` is split and looked up
  piece by piece, so the name passes through while the rest translates.

What it never touches: people's names, shop names, book titles, authors, and
the prose the seed data puts in booksellers' mouths. Those are content.

```bash
python3 i18n/build_i18n.py   # write i18n/ru.py into the master's RU_X / RU_P tables
python3 build/build.py       # then rebuild the site
python3 i18n/audit.py        # crawl every screen in Russian, list what is left (needs Playwright)
```

`ru.py` was re-extracted from the master on 8 October 2026: the prototype had
gained ~290 translations while it was being worked on as an artifact, and the
old `build_i18n.py` regenerated the whole block from a template, which would
have thrown them away along with `RU_SUB`. It now touches only the two tables.
The last audit (8 October) listed 235 strings still in English in Russian mode.

Armenian still has only its original twenty-odd keys and falls back to English
for the rest — visibly, on purpose.

## Decisions baked in

The design system is **shadcn/ui**, adopted whole — their default Neutral
palette in OKLCH, their `0.625rem` radius scale, their component anatomy, and
Geist for type. The full reference, including the four components shadcn has no
equivalent for, is a Design System artifact; `prototype/` implements it in plain
CSS keyed to shadcn's own `data-slot` attributes, so the markup here is the
markup the real React components emit.

No “confirm”. The bookseller's one action is **Ready for delivery** or **Ready
for pickup**, pressed with the book in hand, on the order's own page — and the
way out stays open afterwards, so a book that breaks overnight does not send a
courier across town. Checkout is one screen. A courier's jobs group by order,
with a card per bookshop inside, because a courier makes one trip to one
address. Light, dark, or match the phone.

**Three doors, not one sign-up.** A reader is let in with one Google tap and
asked for nothing — name, phone and address are taken at the first checkout,
where the reason for asking is on the screen. A bookseller fills four
compulsory steps, because a shop with no name, address or hours cannot be shown
to anybody. A courier has no sign-up at all: the office issues the login.

**Delivery is one event for the order.** The courier still collects shop by
shop, but hands over once and takes the cash once, and the button only appears
when every shop has been collected from. One fee per order whatever it holds —
two books cost what one costs, two shops cost what one costs — and that fee is
the platform's. Booksellers are paid for books and never set a delivery price.

**The seller's feed is only what they have not answered.** Sending an offer
takes the request out of the feed and into My offers, where it can be answered
again. A greyed-out row is not a to-do; it is noise.

**No form is taller than one phone screen.** The primary button ends above
690px at 390×844, which makes the ceiling four fields and a heading; longer
forms are split into steps. Everything tappable reaches 36px. Both are checked
by script across every screen, not judged by eye.

12% commission after a free month counted from the shop's first sent offer.
Each shop billed on its own anniversary day, due the day it is issued,
restricted that night if unpaid. One *open* hour to confirm an order, counted
only during that branch's opening hours, and auto-cancel at **the end of the
next open day** — a shop that shuts early loses no time it was never open for.
Three days to collect a pickup.
Silence ladder at 24 h, 72 h and 30 days. Cash only — a four-digit code for
pickups, the courier closes deliveries. Yerevan only. No chat, anywhere.

`docs/spec.html` §07 carries the full list and the settings table they live in.

## Before building the real thing

Read `docs/audit.html` first. Eleven of its sixteen cases are built here and
clickable; the four that stay open are policy decisions or jobs too small to
reach without a real settings screen. The one that matters is **E4**: nothing
runs the clocks, and a prototype cannot fix that. The rule is written down —
*derive for display, queue for consequence* — and what it needs is one
`scheduled_tasks` table and one worker.

Two things the model needs that the prototype only gestures at: an append-only
`event_log`, and `scheduled_tasks`. Both are cheap now and expensive later.
