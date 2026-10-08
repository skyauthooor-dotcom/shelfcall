# Card

A raised surface with a header, a body and an optional footer. Shelfcall uses it for anything that represents one whole thing: an order, a bookshop's part of an order, the courier's cash position, a statement.

Anatomy, in order: `Card` › `CardHeader` › (`CardTitle`, `CardDescription`, `CardAction`) › `CardContent` › `CardFooter`. `CardAction` sits top-right of the header and spans both its rows — that is where an `Edit` or a status `Badge` goes.

The default card has 24px padding and 24px between its sections, which is right for a card that is the subject of a screen. Inside a list, pass `data-compact` to drop both to 16px.

## When not to use it

Not everything is a card. A list of offers is `Item` rows inside one bordered group, not twelve cards — twelve borders in a column flattens the hierarchy and makes nothing look important. Use `Card` when the thing has parts; use `Item` when it is a line.

## What the consumer provides

The title, the description, any action element, and the body. The card sets its own surface, border and radius from `card`, `border` and `radius-lg`; never override them per instance.
