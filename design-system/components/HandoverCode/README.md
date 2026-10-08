# HandoverCode

Shelfcall's own. Four digits a reader reads aloud in a shop, and the bookseller types in.

It is one mechanism doing four jobs: it reserves the copy, it identifies the right stranger at the counter, it tells the platform the handover happened, and it credits the sale to that shop. Pickups only — a courier already knows which door they knocked on, so a delivery has no code.

Set in `mono-code` at 28px with 0.2em tracking, which is the only place in the product type is this large. The digits must be legible across a counter, at an angle, in a shop that may be dim.

Never truncate it, never mask it, never put it behind a tap. The reader's side shows it plainly from the moment the shop marks the book ready.

## Built from

`Card`'s surface and border, plus the `mono-code` type style. The entry side is an `Input` with `aria-invalid` and a `field-error`.

## What the consumer provides

The four digits and one line of explanation. On the seller's side, the input and the error message.
