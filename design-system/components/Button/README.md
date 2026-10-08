# Button

Every action in Shelfcall. This is shadcn's Button; what Shelfcall adds is a rule about when each variant is allowed, and there are only four the product actually uses.

## The four tiers

**`default` — primary. One per screen.** The thing the screen exists for: `Buy · 4 500 ֏`, `Approve and place the order`, `Ready for delivery`, `Send for checking`. If two buttons on a screen are `default`, the screen has not decided what it is for. It is a solid ink fill **with a border** — the only solid fill on the screen. There is no accent hue: the logo is black type on white paper and works reversed, so a coloured button would be a thing the mark does not have.

**`secondary` — the other real choice.** Filled, quiet, **and bordered like every other button**, the same weight of decision as the primary but a different one: `Add to cart` beside `Buy`, `Read them` beside a count of reviews. This used to be described as "rarely right"; it is now the standard partner to a primary, because a reader comparing copies genuinely has two things they might do with the same offer.

**`outline` — the way out, or the side road.** `Cancel`, `Open the cart first`, `Use one you listed before`. It is not a lesser primary; it is a different kind of move.

**`link` — text that navigates.** Underlined, inline, for something that is really a link wearing a button's clothes. It keeps a 36px hit box even though it reads as type: a thumb cannot aim at a 20px line.

`ghost` survives for repeated in-row actions (`Edit`, `Remove`) where a border on every row would make a cage — but it keeps its border in Shelfcall's own CSS. A borderless variant existed and was retired: it was 14px/500 on nothing, which differs from body text by a single step of font weight, and people stopped seeing it as a button. Anything that is really a heading you can open gets a `›` chevron instead of button clothes.

`destructive` is **not** available as a standalone button anywhere in Shelfcall. Anything that cancels an order, pulls a book or releases a copy opens a `Sheet` first, and the variant exists here because that sheet's confirm uses it.

Label a button with the thing that will happen, in the words of the thing that will happen, and name the money: `Delivered · took 5 500 ֏`, not `Complete`.

## Size

There is one. **40px tall, 14px type, everywhere** — in a row, inside a card, at the bottom of a flow. `data-size="sm"`, `"xs"` and `"lg"` still parse, and they all resolve to the same metrics; they are kept only so existing markup does not break.

This replaced a 28/32/36/48 scale. Four heights meant a reader had to learn that a 32px thing and a 40px thing were both buttons while a 20px underlined thing was one too — and the small ones, which were the ones repeated most often in lists, were the hardest to hit. Importance is carried by **fill and width**, which are read at a glance and cost no height: the committing action is filled in ink and usually full width; everything else is `outline` and sized to its label.

Gradients, glows and drop shadows are not available and are not coming. If a primary does not feel important enough, the answer is more space around it and less competition beside it, not decoration on it.

`icon` is the one genuine exception, at 40×40, because it is square by definition.

Every button scales to `.985` while pressed. That is the whole motion budget for a button.

## What the consumer provides

The label, the `variant`, and `data-block` for full width. Not the size. Icons are Lucide at 16px and take `currentColor`; place them with `data-icon="inline-start"` or `inline-end`.

## Dark theme

`destructive` takes `background` as its ink in dark, not white: white on `destructive` measures 2.9:1 there. `default` inverts wholesale — the ink and the paper swap, so the primary is a white fill with #1C1C1C type. That is the logo reversed, which is the point.
