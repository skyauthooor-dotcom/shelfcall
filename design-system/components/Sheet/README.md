# Sheet

The one place Shelfcall asks "are you sure" — except that it never says those
words. Anything that cannot be undone stops here first: closing a request,
taking an offer down, cancelling an order, putting a copy back on the shelf,
handing cash to a shop, withdrawing a payment claim, retiring a branch, giving
up on a delivery.

It is a native `<dialog>` opened with `showModal()`. Escape, the backdrop,
focus trapping and inertness behind it are the browser's job; we do not
reimplement any of them.

## Why a sheet and not a dialog in the middle

It rises from the bottom because the thumb is at the bottom. A centred dialog
on a 390×844 phone puts its buttons at the middle of the screen, which is the
one region a one-handed grip reaches worst.

## Anatomy

```html
<dialog data-slot="sheet" aria-modal="true">
  <form method="dialog" data-slot="sheet-content">
    <div data-slot="sheet-grip" aria-hidden="true"></div>
    <h2 data-slot="sheet-title">Close this request?</h2>
    <p data-slot="sheet-body">The shops stop seeing it, and any offers on it
      are set aside. Nothing is deleted — you keep the record, and you can post
      it again any time.</p>
    <div data-slot="sheet-actions">
      <button data-slot="button" data-variant="destructive" type="button">Yes, close it</button>
      <button data-slot="button" data-variant="outline"     type="button">Keep it</button>
    </div>
  </form>
</dialog>
```

## The copy is the component

A sheet that says "Are you sure?" has told the reader nothing they did not
already know. Two rules, both enforced by `_test_sheet.py`:

1. **The title names the consequence**, in the words of the thing that will
   happen: *Close this request?*, *Take this offer down?*, *Handed the cash
   over?* Never *Are you sure?*, never *Confirm*.
2. **The body says what changes and what does not.** Most destructive-looking
   actions in Shelfcall are not destructive at all — a closed request is kept
   and can be posted again — and saying so is what stops people hesitating over
   a safe action and rushing a dangerous one.

The confirm button repeats the verb: *Yes, close it*, *Yes, it is gone*,
*Yes — handed over 4 500 ֏*. The money is named again, because "yes" to *Pay?*
is not the same answer as "yes" to *Pay 3 400 ֏?*

## Order and shape of the buttons

Stacked, full width, **confirm first, way out second**. Side by side would put
a destructive action one thumb-slip from the way out; stacking gives each its
own row, and the nearer of the two — the lower — is the safe one.

The way out is always labelled with the thing that stays: *Keep it*, not
*Cancel*. "Cancel" in an order-cancelling dialog is a genuine ambiguity.

## When a reason is required

Some actions need to know *why* before they will fire: a courier who could not
deliver, a reader disputing an order. Those sheets carry a row of reason chips
and **the confirm is disabled until one is picked** — see `ReasonBlock`, which
is now a button that opens one of these rather than an inline block.

## What the consumer provides

The title, the body, the confirm label, the action, and optionally the list of
reasons. Everything else — dismissal, focus, the animation, the safe-area
padding — is the component's.

## Dismissal costs nothing

Escape, the backdrop and *Keep it* are the same answer and go through one
path: close the dialog, and let the `close` event clear the state. Nothing
destructive can happen down a dismissal path; that is checked by test.

## Motion

18ms is not a typo: `.18s` rise of 14px, and nothing at all under
`prefers-reduced-motion`. The sheet is announcing itself, not performing.
