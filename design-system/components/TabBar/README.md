# TabBar

The phone's navigation: fixed to the bottom of the screen, where the thumb is.

Shelfcall is used standing up — a bookseller behind a counter, a courier on a street, a reader on a bus — so the destinations go to the bottom and the top of the screen is left to the screen's own heading. Above 560px the tab bar is not rendered at all and the sections live in the top bar instead; a bar pinned to the bottom of a laptop window is nobody's navigation.

## What goes in it

**Four items, chosen rather than taken off the front of the list.**

| Role | Tabs |
| --- | --- |
| Reader | Requests · Orders · Cart |
| Bookseller | Feed · My offers · Orders · Billing |
| Courier | Deliveries · History |

Billing stays because it is where a shop's money and its standing live. Reviews moved to the shop profile: a seller reads reviews, they are not a place a seller works.

Notifications and the profile are **not** tabs. They live in the top bar. A tab is a place you work; a bell is an interruption.

## Flows hide it

A screen that is a flow — checkout, the offer form, registration, the review — renders no tab bar at all. Two reasons, and both matter:

- A form has one way out, the button at the bottom. A row of exits beside it is an invitation to abandon.
- It is 56px, taken from the height budget every form is measured against (see *Forms* in the brand book). A flow screen needs all of it.

## Mechanics

- `position: fixed`, plus `padding-bottom: env(safe-area-inset-bottom)` for the home indicator.
- The page adds bottom padding of its own while the bar is shown, so nothing ends up underneath it.
- Each item is at least 56px tall and an equal share of the width.
- Icons are Lucide at 21px, `currentColor`, stroke 1.6.
- The badge sits on the icon, not on the label.

## The active tab

Weight **and** stroke, not colour alone: the label goes to 600 and the icon stroke to 2.1. Colour alone fails for readers who do not separate colours, and it fails again when the label is a long Armenian word and the colour is the only thing distinguishing it.

## Labels in three languages

`Հարցումներ` is ten characters. Four tabs at 390px leaves about 97px each, so labels truncate with an ellipsis rather than wrapping to two lines and pushing the bar taller. Pick short words in Armenian and Russian **before** the layout is signed off, with a native speaker — do not discover the constraint in the browser.
