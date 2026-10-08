# Avatar

A bookseller's face in the product. shadcn's Avatar: an image with a fallback underneath, and the fallback is what most shops will show for a while.

Four sizes, each for one job. `xs` (20px) sits inline on an offer row beside the shop name. `sm` (28px) is for dense lists. `md` (40px) is the seller card on an offer. `lg` (64px) is the public profile and the shop's own settings.

## The fallback is initials, and that is deliberate

Until a shop uploads a photo, buyers see its initials on a `muted` circle — `AB` for Aram Books, `N` for Nairi. Never a stock shopfront, never a generic book or shop glyph.

A placeholder that looks like a real photo is a small lie about a real business, and in a marketplace where the whole pitch is *a real copy from a real shelf* it is the wrong lie to tell. Initials read as "this shop has not added a picture yet", which is true and costs nobody anything.

The same rule as `New seller`: state the absence, never paper over it.

## What the shop uploads

Their shopfront, a shelf, their logo. One image, cropped square and covered — no gallery, because a profile picture is one thing. The settings screen shows the current one at `lg` beside *Change photo* and *Remove*.

## What the consumer provides

The seller and the size. The component derives the initials from the name, takes the first letter of the first and last word, and caps at two characters.

## Accessibility

The avatar is `aria-hidden` wherever the shop's name is already next to it in text, which is everywhere it currently appears. It is decoration in that position, and a screen reader announcing "A B, Aram Books" is noise.
