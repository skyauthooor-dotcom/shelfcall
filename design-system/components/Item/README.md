# Item

One line in a list: an offer, an order, a branch, a review. `Item` is what Shelfcall uses instead of a card wherever the thing is a line rather than a subject.

Anatomy: `Item` › `ItemMedia` (a `BookCover` or thumbnail) › `ItemContent` › (`ItemTitle`, `ItemDescription`) › `ItemActions`. Wrap a run of them in `ItemGroup` with `ItemSeparator` between, inside one bordered container — one border around twelve rows, not twelve borders.

`data-variant="outline"` gives a single item its own border, for the rare case where one stands alone.

## Rows that open pages

An `Item` rendered as a `button` or `a` opens the thing it names. **A row that navigates carries no other action**: the seller's order list is rows only, because deciding to send a courier across town should not be one thumb-flick away from a scroll. Put the decision on the page the row opens.

A row that does not navigate may carry one action in `ItemActions` — `Add to cart` on an offer, `Remove` on a cart line.

## What the consumer provides

The media element, the title, the description and any action. `ItemContent` clips its own overflow, so a long title truncates rather than pushing the price off the row.
