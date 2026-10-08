# OfferCard

Shelfcall's own, and the screen the whole product turns on. One bookseller's answer to one request, laid out so a reader can compare four of them without opening anything.

The order of the card is the order a reader decides in, and it changes with the request:

- **Open-ended request** — the bookseller's note leads, directly under the title, at `text-base` in `foreground`. The reader wrote *something with a crazy scientist*; the only thing separating two copies is why each bookseller thinks it answers that. The note is optional, but on these requests it is given a screen of its own in the offer form and it leads the card here.
- **Specific request** — the reader named the book, so the note drops below the author line and gets quieter. What matters now is condition, price and who is selling.

Then always: author, year, condition; the shop, its branch and its rating; the price; and the actions.

A shop with no completed orders shows `new seller` rather than an invented rating. Never a star average below three reviews.

## Built from

`Item` for the layout, `BookCover` or the real photograph for the media, `Badge` for condition and seller status, `Button` for `Add to cart` and `Not this`.

## What the consumer provides

The offer, the request's kind, and the cart state. The card decides its own order from the kind — the caller never passes a layout.
