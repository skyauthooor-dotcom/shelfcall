# Switch

A setting that takes effect immediately. Shelfcall uses it for three things only: a courier going on or off shift, a bookseller's email notifications, and whether a branch allows pickup.

A switch has no Save. If something needs confirming it is not a switch — it is a pair of buttons, or a `ReasonBlock` when the change loses something.

Always paired with a label a finger can hit, and a line under it saying what the current position means: *New jobs come to you* / *You will not be given new jobs*. Describe the state, not the switch.

## The hit area and the control are two boxes

This is the part that broke once and is written down so it does not break again.

The button is **40×40 and paints nothing**. The **32×18 track is drawn inside it** as a pseudo-element, and the 14px thumb moves from 6px to 20px.

The tempting shortcut — keep the button at 32×18, pad it out to 40px for the touch target, and claw the background back with `background-clip: content-box` — loses to the `9999px` radius. The background fills the padded box, the radius rounds that box, and the control renders as a solid black disc with a dot in it. It shipped that way and was caught by eye, not by the audit script: the sizes were all correct, the picture was not.

Focus draws on the track, not on the invisible 40px box.

## What the consumer provides

`aria-checked`, the label, and the description for each state. The whole row is the hit target, not just the 32px track.
