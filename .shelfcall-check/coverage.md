# Shelfcall prototype — coverage before the sweep

Skill: shelfcall-prototype-testing. Baseline: build OK · unit 25/25 · e2e 28 flows · contrast 0 failures.
Layers: D domain · P projection · S service · E e2e (tests/e2e/flows.py) · L layout (phone_probe.py, contrast.py).
`covered` = an existing flow exercises it · `partly` = main path only, the story's edge cases are not asserted · `missing` · `n/a` = layer does not exist in the prototype.

| ID | Story | D | P | S | E | L |
|---|---|---|---|---|---|---|
| R-01 | Signs in with Google | — | — | — | missing (no real auth: known gap; door screen only) | — |
| R-02 | Asks for a book | D via E: missing (`any` on request) | — | n/a | partly (`reader_asks`, dock button); step labels, back names, no tab bar, field budget not asserted | missing (probe not yet run) |
| R-03 | Sees offers arriving | D via E: partly (seen reaches shop) | — | n/a | partly (`offer_with_photo…`, `offer_card_opens…`); "rows never act", "no dismiss" not asserted | — |
| R-04 | Sees a changed offer | D via E: missing (price down only, 3 changes, frozen fields) | — | n/a | missing | — |
| R-05 | Puts an offer in the cart | D via E: partly | — | n/a | partly (`shop_removes_its_offer…`: removed offer cannot be bought); stale-screen refusal missing | — |
| R-06 | Checks out | — | — | n/a | partly (pickup + courier order flows); "pay in cash" on total, no card fields, 36px chips, courier note only on delivery not asserted | missing |
| R-07 | Follows an order | — | n/a | n/a | partly (order flows); Yerevan time, reader sees courier note not asserted | — |
| R-08 | Four-digit code | D via E: partly (pickup code entered) | — | n/a | partly; wrong code refused, mono font not asserted | — |
| R-09 | Closes a request | — | — | n/a | partly (`closing_a_request…`); sheet title/consequence, nothing changes before confirm not asserted | — |
| R-10 | hy/ru/en, light/dark | — | — | — | missing (fallback note in settings) | partly (contrast both themes, en only); phone probe missing |
| B-01 | Registers through the wizard | — | — | n/a | covered (`shop_registers_and_the_office_opens_it`); validation sends back to owning step not asserted | missing |
| B-02 | Answers with an offer | D via E: missing (`any` refused on offer, integer drams) | — | n/a | partly (`shop_offers` helper) | — |
| B-03 | Edits an offer | D via E: missing (all edit rules) | — | n/a | missing | — |
| B-04 | Withdraws an offer | D via E: missing (reason required; not after ordered) | — | n/a | partly (`shop_removes_its_offer…`); reason sheet, disabled confirm not asserted | — |
| B-05 | Order list | — | — | — | missing (list has no buttons) | — |
| B-06 | Pickup: marks ready | — | n/a | n/a | missing (buyer name/phone before vs after ready) | — |
| B-07 | Courier-delivery order | — | n/a | n/a | missing (no buyer data anywhere; says why) | — |
| B-08 | Never sees courier note | — | n/a | — | missing | — |
| B-09 | Statement / unpaid | — | — | n/a | partly (`shop_pays…`, `billing_counts…`); unpaid shown as standing alert not asserted | — |
| B-10 | Stale screen | — | — | n/a | partly (`two_phones_at_once…`); typed refusal on a stale action missing | — |
| C-01 | Office-issued login | — | — | — | missing (no public courier sign-up) | — |
| C-02 | Collects from a shop | D via E: partly | — | n/a | covered (`courier_order_from_cart_to_cash`, `courier_paying_at_the_counter…`) | — |
| C-03 | Delivers | D via E: partly | n/a | n/a | partly (`courier_order_from_cart_to_cash`); address+note shown, "Delivered · took X" label not asserted | — |
| C-04 | Something goes wrong | D via E: partly | — | n/a | covered (`courier_cannot_deliver_and_the_order_unwinds`); sheet before loss not asserted | — |
| X-01 | Transition table | missing (rules live in act()) | — | — | — | — |
| X-02 | Projection key sets | — | n/a — known gap: every page holds the whole world | — | — | — |
| X-03 | Typed refusals | n/a (messages are strings) | — | n/a | — | — |
| X-04 | Role isolation | — | — | n/a | known gap (role switcher) | — |
| X-05 | Money | missing (`money()` format, integers) | — | — | — | — |
| X-06 | No personal data in logs | — | — | n/a | partly (page errors collected, console not scanned) | missing |
| X-07 | Phone rules every screen | — | — | — | — | missing (phone_probe.py) |
| X-08 | Contrast | — | — | — | — | covered (contrast.py, both themes) |

---

# After the sweep (2026-10-08)

Ran: unit 25/25 pass · e2e 57 flows (28 regression all pass; 29 story tests: 19 pass, 10 fail = findings) · contrast 216 visits, 0 failures · phone probe reader/seller/courier × hy/ru/en × light/dark.

| ID | Result | Rule broken |
|---|---|---|
| R-01 | pass (door only) | — |
| R-02 | pass | — |
| R-03 | **FAIL** — offer row has 2 buttons (Add to cart, Buy) | §7 |
| R-04 | pass | — |
| R-05 | pass | — |
| R-06 | pass (2 tests) | — |
| R-07 | **FAIL** — times follow phone zone, not Asia/Yerevan | §9 |
| R-08 | pass | — |
| R-09 | pass | — |
| R-10 | pass | — |
| B-01 | pass | — |
| B-02 | pass | — |
| B-03 | pass (2 tests) | — |
| B-04 | **FAIL** ×2 — no reason asked; ordered offer removable from stale screen | §5 §7 §9 |
| B-05 | pass | — |
| B-06 | **FAIL** — pickup buyer name shown before "ready" | §8 |
| B-07 | **FAIL** — reviewer name visible on courier-delivery orders (s.reviews) | §8 |
| B-08 | pass — note never reaches shop | — |
| B-09 | **FAIL** — unpaid statement is a Card, not an Alert | §7 |
| B-10 | **FAIL** — stale "Ready" reverts shipped → ready | §9 |
| C-01 | pass (test fixed: prose "nothing to sign up for" is not an invitation) | — |
| C-02 | **FAIL** — courier collects an order still "placed" | §5 §9 |
| C-03 | **FAIL** — delivery asks no 4-digit code from the reader | §5 |
| C-04 | pass | — |
| X-01 | covered through B-04, B-10, C-02 (all three fail) | §5 transition table |
| X-02 | known gap — every page holds the whole world | §8 |
| X-03 | known gap — refusals are strings, not typed keys | §9 |
| X-04 | known gap — role switcher in prototype | — |
| X-05 | pass (warning: bank field "5 500 AMD" on s.pay) | — |
| X-06 | pass — no phone, address or code in console | — |
| X-07 | **FAIL** on every screen (see probe-summary.txt) — tab counter 10.5px, tab labels 11px, logo 68×20, icon buttons 34×34, demo text 11.5px; "Copy" ×4 on s.pay | §10 |
| X-08 | pass | — |
