# BookCover

Shelfcall's own. A book that has no photograph, drawn as a book rather than shown as a broken image.

Most offers arrive with a photo of the real copy, and the photo is the point — it is how a reader judges a used book. But a request has no photo, a reused listing may have lost one, and a courier's manifest does not need to load six images. In all of those the cover renders the title and author as type on a `muted` ground, in the proportions of a book.

Three sizes: `sm` 48×66 in a list row, `md` 64×90 on an order page, `lg` 128×180 on the offer detail. The title clamps to three lines, the author to one; long titles break anywhere rather than overflowing.

When a photo exists it goes inside the same element as an `img` and covers it, so the layout never shifts between a book that has one and a book that does not.

## Built from

Nothing in shadcn — this has no equivalent. It uses `muted`, `border`, `radius-sm` and the `text-xs` scale.

## What the consumer provides

The title, the author, an optional image, and the size. Never a placeholder illustration and never a generic book icon: the type *is* the cover.
