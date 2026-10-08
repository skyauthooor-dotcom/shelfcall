Shelfcall runs on shadcn/ui, unmodified. The colour tokens, the radius scale
and every component's anatomy are shadcn's own; nothing here is a variant of
them. When shadcn and this document disagree, shadcn is right and this
document is stale.

What Shelfcall adds is on top, never instead: four components shadcn has no
equivalent for, and the rules below about which shadcn component answers which
situation in a book marketplace.

## Content fundamentals

Write from the reader's side of the screen. A person collects a book, pays a
bookseller and waits for a courier; they do not "complete a transaction" or
"initiate fulfilment".

Say what will happen, in the words of the thing that will happen. `Ready for
delivery` is the label, not `Confirm` — confirming is a form the shop fills in,
marking a book ready is a claim about a physical object on a counter. Every
committing button is written this way: `Add to cart`, `Approve and place the
order`, `Collected from the shop`, `Delivered · took 5 500 ֏`.

Money is always cash and always named. A button that takes money says the
amount. A total says `to pay in cash`, never `Pay`, because nothing is charged
anywhere in Shelfcall.

Second person for the person acting, third for everyone else: `You pay Aram
Books in the shop`, `Dina has been told`. Never `we` for the platform except
where the company genuinely acts — `we will tell the reader straight away`.

No emoji. No exclamation marks. Armenian is the first language, Russian and
English after it, so keep sentences short and avoid idiom that will not
translate: `past its hour` survives, `dropped the ball` does not.

Errors say what happened and what to do: *That is not the code on the buyer's
order. Ask them to read it again.* Never an apology, never `Oops`.

## Colour

Use the tokens, never a literal. `foreground` on `background` and `card`;
`muted-foreground` for anything secondary — but not on a `muted` ground at body
size, where it measures 4.3:1 in the light theme.

**There is no third colour, and the reason is the logo.** The mark is black
type on white paper — a reference to printing — and it works reversed, white on
black. An accent hue would be a thing the mark does not have, so the product
has two colours and one of them is the paper.

A hue *was* tried here and removed. What it was invented to solve is real:
black was doing three jobs at once — "press this", "this is selected" and "this
is running out of time" — and a reader cannot be asked to tell three meanings
apart by one colour. The fix is **shape**:

| meaning | how it looks |
| --- | --- |
| press this | a solid ink fill **with a border**. One per screen, never two. |
| this is selected | a tinted ground and **no border**. A label never wears an edge. |
| this is running out | a tinted ground and a dot; `tint-bad` once it has gone. |

**BORDER MEANS BUTTON.** That one sentence is the whole system. It survives a
photocopy, a colour-blind reader and a phone in sunlight, which a hue does not,
and it is the reason `Badge` lost its `outline` variant: a badge with a border
and an outline button were both "text in a box", and the reader had to tap one
to find out which.

`primary` is the ink — #1C1C1C, not #0A0A0A. Nothing in the product is darker
than that in either theme, and the dark page is that same value, so the two
themes are one pair reversed rather than two palettes.

`destructive` is for loss that cannot be undone — cancelling an order, pulling
a book after saying it was ready, an overdue statement, a rejected handover
code. It is not a warning colour and not an attention colour. A deadline that
has passed is `destructive`; a deadline approaching is `muted-foreground`.

Nothing here is judged by eye. `_contrast.py` paints each colour into a canvas
in the page and measures what the browser actually resolved — not what the CSS
string says, which is how an earlier accent got scored at 2.5:1 when it was
really 7.4:1. Body text measures 17.0:1 light and 16.3:1 dark; muted text 4.74:1
and 6.60:1; and the surface ladder is checked to climb in one direction, so a
card can never end up darker than the page it sits on.

Two contrast facts, both inherited from shadcn and both kept exact rather than
quietly retinted:

- `ring` is 2.6:1 on `background` in the light theme, under the 3:1 a focus
  indicator needs. Shelfcall answers with thickness, not hue: the ring is 3px
  with a 1px offset.
- White on `destructive` in the dark theme is 2.9:1. A destructive *button* in
  dark therefore takes `background` as its ink, not white.

## Type

Geist for everything, Geist Mono for the handover code and order numbers.
Both are on Google Fonts. shadcn prescribes no typeface — the framework
template supplies one — so this is Shelfcall's choice, and it is shadcn's own
choice on their site.

`text-sm` is the working size: buttons, inputs, list rows. `text-xs` in
`muted-foreground` is metadata and must never carry a fact a decision rests on
— a price, a deadline or an address belongs at `text-sm` or larger.

Set the four-digit handover code in `mono-code` and nowhere else. It is the
only number in the product a person reads aloud.

## Spacing and shape

Tailwind's 4px scale. `space-4` is card padding, row padding and the phone
gutter; `space-5` is the gutter above phone width. Any control a thumb must hit
is at least `space-10` tall.

`radius-md` on controls, `radius-lg` on cards and alerts, `radius-full` only on
things that are actually circular. Everything derives from `radius`; change
that one token and the scale moves together.

Borders separate, shadows do not. Shelfcall uses `border` for every edge and no
shadow at all except the toast, which floats over content and has to.

## Forms

**No screen that asks for input is taller than the phone it runs on.** The
primary button must sit above the fold on a 390&times;844 screen once the
browser's own chrome is subtracted — about 690px of usable height. This is
measured, not estimated; a form the person has to scroll to finish is a form
they abandon halfway.

That budget is roughly: a heading block costs ~135px, each labelled field ~78px,
a textarea ~115px, a button 40px — the only button height there is. Four
fields and a heading is the ceiling.

A flow screen renders no `TabBar`, which is worth 56px of that budget.

When a form exceeds it, split it — do not shrink the type or the touch targets.
Splitting rules, in order:

1. **Required fields first, optional ones on their own screen.** Publisher,
   edition, language, pages and binding sit behind *More about this copy*; the
   required path stays two screens deep.
2. **A field the whole thing turns on gets its own screen.** On an open-ended
   request the bookseller's note is the entire reason a reader picks that copy,
   so it is one screen with one field on it.
3. **Short fields pair up and stay paired.** `.two.tight` keeps author/year and
   condition/price side by side even at phone width. Only pair fields whose
   content is genuinely short.
4. **Validate on the way out of each screen**, and send the person back to the
   screen that owns the offending field with the message on it.

Every step says where it is — *Step 2 of 3* — and every step after the first
has a back link naming what it goes back to, not just an arrow.

## Touch targets

**Nothing tappable is smaller than 36px in its smallest state.** Not a back
link, not a small button, not a segment tab, not the switch, not the × on a
removable chip. This is measured across every screen by script — overflow,
type under 12px, targets under 36px, repeated text — because a rule judged by
eye is a rule that holds until someone is in a hurry.

Where the visual size is deliberately small, the height comes from padding
rather than from the box:

```css
.back { min-height: 40px; padding: 0 10px; margin-left: -10px; }  /* optical alignment kept */
.btn, .btn.sm, .seg button { min-height: 40px; }                  /* one size, everywhere */
.tog { width: 40px; height: 40px; }                               /* the hit area paints nothing */
.tog::before { width: 32px; height: 18px; }                       /* the track is drawn inside it */
.chip.rm button { min-width: 36px; min-height: 36px; }
```

The switch is two boxes on purpose. An earlier version padded one button out to
40px and tried to claw the background back with `background-clip`, which lost
the fight with a 9999px radius and rendered the whole control as a black disc.
A hit area and a control are different boxes; drawing them as one is what
crushed it.

No screen scrolls sideways at 390px: long titles truncate, long numbers wrap.
Decorative type on a `BookCover` is the one thing allowed under 12px, and it
carries `aria-hidden` so it is not read out either.

## Three doors, not one form

The three roles do not share a sign-up. They share a screen that offers three
doors, and each one behaves differently on purpose:

| Role | The door | Why |
| --- | --- | --- |
| Reader | One Google button, nothing else | Name, phone and address are asked at the first checkout, where the reason for asking is on screen. A reader who never buys is never asked. |
| Bookseller | A four-step wizard, nothing optional | A shop with no name, address or hours cannot be shown to anyone, so there is nothing to defer. |
| Courier | Login and password, issued by the office | A courier sees addresses, phone numbers, gate codes and cash. There is no sign-up to offer. |

Each wizard step obeys the forms budget above — a heading and at most four
fields — and carries *Step 2 of 4* plus a back link that names where it goes.

**Booksellers have an `Avatar`.** A real photo when they upload one, initials
in `primary` when they have not. Never a stock shopfront and never a generic
silhouette: an empty avatar should look like a shop that has not finished
setting up, because that is what it is.

## Privacy between roles

Shelfcall has three roles who see three different things about the same order,
and the differences are deliberate.

**The note for the courier is the courier's.** It goes to the reader who wrote
it and to the courier carrying the job. The bookseller never sees it, at any
status, on any screen — a gate code is a delivery instruction, not an order
attribute. The field carries a line saying so where it is typed, because
someone writing their door code deserves to know who reads it.

**On a courier delivery the bookseller never learns who the buyer is.** Not
the name, not the phone, not the address — not in the order list, not on the
order page, not in the review block, not ever. The shop hands the book to a
Shelfcall courier and is paid for the book; where it ends up is our leg of the
trip. A shop that never receives a home address cannot leak it, lose it, or
turn up at it, and a home address is the most sensitive thing this product
holds.

The order page says this out loud rather than leaving an empty field, because
a blank where a name should be reads as a bug.

**On a pickup the shop sees a name and a phone, and only then.** A stranger is
going to walk in and say "I am here for an order", and somebody has to match
them to a parcel; if they never come, the shop needs to be able to ring. The
phone appears once the shop marks the book ready — nothing is released to a
shop that has not committed a copy.

These two are the same rule pointed in opposite directions: each role gets
exactly what its job needs and nothing that belongs to someone else's.

## How far an offer may still be edited

An offer is not a listing. It is an answer to a person, and the licence to
change it narrows as it travels:

| Status | What may change |
| --- | --- |
| sent | anything — nobody has looked |
| seen | the price, downwards only; the note |
| in cart | the same — they chose this copy at this price |
| ordered | nothing. Withdraw it with a reason instead |

The book itself — title, author, year, edition, condition — freezes the moment
a reader has read the offer, because that is what they are choosing between.
Raising a price after it has been seen is refused with the reason on screen,
not hidden by a disabled field.

**Three price changes, then no more.** A price that moves every day is a
negotiation, and the reader has no way to answer it: there is no chat for them
to push back in. A shop whose copy is worth less than it asked can take the
offer down and send a fresh one.

The rule lives in the save handler, not only in the screen, so a stale view
cannot walk around it.

## One vocabulary for condition

**new · good used · used · old.** The same four words on the request and on the
offer.

Two lists nearly shipped — readers choosing between *any used* and *like new*
while shops offered *worn* and *new*. A reader could not compare what came back
with what they asked for, which is the only thing that screen is for.

`any` exists on a request and never on an offer: it is not a grade, it is the
absence of a preference.

## Three languages, and what is not translated yet

Armenian is the default; Russian and English are reached from the language
control on the account screen, beside Appearance.

**Anything not yet translated falls back to English rather than being machine
translated,** and the settings screen says so. That is how a translation
actually rolls out, and it is honest in a way the alternatives are not: a
control that switches nothing is a lie, and a half-machine-translated app is
worse than either. What is translated is translated properly; what is not is
visibly still to do.

Two consequences for layout, both of which cost money if found late:

- Armenian words are long. Anything in a fixed-width slot — tab labels, chips,
  segmented controls — must be checked in Armenian before the layout is signed
  off, not after.
- Keys are the contract, values are drafts. No Armenian or Russian string
  reaches a reader without a native speaker reading it first.

## Iconography

Lucide, which is what shadcn's components expect. Stroke 1.5, size 16 inside a
`text-sm` control and 20 standing alone. Icons take `currentColor` so they
inherit the control's ink.

Icons never carry meaning alone. A status is a `Badge` with a word in it; an
icon beside that word is decoration and may be dropped. This matters for
colour-blind readers and it matters more in three languages.

## Which component for which situation

| Situation | Component |
| --- | --- |
| An offer in a list | `Item`, with `Badge` for status and one `Button` |
| An order, a shop's card, the cash summary | `Card` |
| Status: *to collect*, *past its hour*, *settled* | `Badge` — a ground, never a border |
| A standing condition: unpaid statement, book unavailable | `Alert` |
| An action that loses something | `Sheet` — never a bare destructive `Button` |
| An action that needs a reason first | `ReasonBlock`, which opens a `Sheet` |
| A four-digit handover code | `HandoverCode` |
| A book with no photograph | `BookCover` |
| Nothing here yet | `Empty`, always with the reason and a way out |
| Where the app's sections live, on a phone | `TabBar` — and never on a flow screen |
| A fork in a flow, with a sentence per choice | `PickCard` — alone on a screen it advances; sharing the screen it selects and stays |
| A delivery window | chips, 36px, in a wrap row under a day strip |

## Two rules that are not shadcn's

**No component takes a destructive action on one tap.** Anything that cancels,
pulls or releases opens a `Sheet` first, which names the consequence in the
words of the thing that will happen — *Close this request?*, never *Are you
sure?* — and says what does **not** change, because most of these actions are
recoverable and hesitating over a safe one is its own cost. Where a reason is
required, the confirm stays disabled until one is picked. A single red button
is not an acceptable substitute anywhere in this product.

**A list never acts.** Rows open pages; decisions are made on the page. This is
why the seller's order list has no buttons on it at all.

**Nothing asks the reader to tidy up after us.** There is no "not this one" on
an offer, no archiving, no marking-as-read. An offer a reader does not want is
one they simply do not buy. Every such control is work done for our benefit
that looks like work done for theirs, and it buys a second place for things to
hide in.
