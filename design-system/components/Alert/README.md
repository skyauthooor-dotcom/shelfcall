# Alert

A standing condition the person needs to know about, attached to the thing it concerns. Not a notification and not a toast — an `Alert` is part of the page and stays as long as the condition does.

`default` states a fact: *A courier is coming for it. Keep it by the counter.* `destructive` states a problem that costs something: *Your statement is unpaid. New requests stop here until it is settled.*

## When not to use it

Do not use an `Alert` to ask for a decision. If the person must choose, the choice belongs in the page as controls. An `Alert` with a button in it is usually a `ReasonBlock` or a `Card` wearing the wrong clothes.

Do not stack them. Two alerts on one screen means neither is read; pick the one that is actually blocking and put the other in the body text.

## What the consumer provides

An optional icon, a title, and a description. Keep the title to one line and put the consequence in the description — what happens if this is ignored, in plain words.
