# ReasonBlock

Shelfcall's own, and the most important component in the system. Nothing destructive in this product happens on one tap.

A bookseller pulling a book after saying it was ready, a courier reporting a failed delivery, a reader cancelling an order, a shop releasing an uncollected pickup — each of these cancels a real order, reopens a request and sometimes moves cash. Each goes through three states in one place:

1. **Closed.** An `outline` button naming the situation: *Could not deliver*, *Something was wrong with this order*. It is a button, and it looks like one — it just does not do anything destructive yet.
2. **Reasons.** Pressing it opens a `Sheet` carrying a sentence about what will happen and the reasons as chips — *sold in the shop · cannot find it · damaged · changed my mind*.
3. **Confirm.** The sheet's confirm is **disabled until a reason is picked**, and only then does it fire.

The block used to expand inline, which put a destructive confirm somewhere in the middle of a scrolling page, at whatever height the content happened to end. Moving it into a sheet puts it at the bottom of the screen where the thumb is, every time, and makes Escape and the backdrop into ways out that inline expansion never had.

The reason is not paperwork. It is what the reader is told, it is what the operator sees, and picking it is the deliberate act that a bare red button skips. A `destructive` button on its own is not an acceptable substitute anywhere in Shelfcall.

The sentence above the reasons names the consequence in full, including the money: *Say it now and the courier is stood down before the trip. The reader is told and their request reopens.*

## Built from

`Button` in `outline` for the trigger, and a `Sheet` for everything after it — chips for the reasons, `destructive` for the confirm.

## What the consumer provides

The trigger label, the consequence sentence, and the list of reasons. Reasons are a fixed enum per situation, never free text — they are read by the platform, not only by a person.
