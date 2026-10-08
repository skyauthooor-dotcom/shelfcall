# PickCard

A fork in a flow, offered as cards big enough to read.

Used where the choice decides what happens next and the reader needs a sentence to decide: which kind of request this is, and when a delivery should come.

A card carries a heading and one plain sentence of its own, and sometimes an example in quotes. Neither card is the default and neither looks secondary — an open-ended request is a first-class product, not a fallback for people who failed the real form.

## Tapping one chooses AND moves on

This is the rule, and it was learned the hard way. On one screen a pick card navigated on tap; on another the identical-looking card only selected, and the button below carried the flow. Tapping the card that was already selected did nothing visible, so the control read as broken.

**One component, one behaviour.** A pick card commits the choice and advances. If a screen also needs "keep what is already chosen and move on", that is the wide button underneath, and it says so in those words.

A chosen card still shows it — border in `foreground` plus a 1px inset ring — because the reader may come back to the screen from an Edit and needs to see where they left it.

## What the consumer provides

The heading, the sentence, an optional example line, `aria-pressed`, and the action. Nothing else; this component has no icons, no images and no price.
