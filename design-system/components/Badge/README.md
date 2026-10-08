# Badge

Status, in a word. Every state a reader, bookseller or courier needs to recognise at a glance is a `Badge` — `to collect`, `past its hour`, `held until 26 Sep`, `settled`, `new seller`.

## A label has no border

A badge sits on a tinted ground and carries **no edge at all**. The border is reserved: an edge means you can press it, a ground means you cannot. Before this rule a badge and an outline button were both "text in a box", and the only way to tell them apart was to tap one — so the `outline` variant is gone.

Nor is a badge ever a solid ink fill. That is the primary button, and there is one of those per screen.

Three variants: `default` is the plain label and by far the most common; `strong` is a label that is **selected or live** — a chosen filter, a count, a running countdown — and gets one step more ground and one step more weight, which is as loud as a label is allowed to get; `destructive` marks a state that has gone wrong or a deadline that has passed, and it is the *tinted* red, never the filled one. A filled red badge reads as a button that deletes something. An approaching deadline is `default`, not `destructive`.

## The rule that matters

**A badge always contains a word.** Colour is never the only carrier of meaning. This is an accessibility floor for colour-blind readers, and it is a practical floor in a product that ships in Armenian, Russian and English where a colour convention may not travel.

Keep the text to one or two words in lower case. `past its hour`, not `OVERDUE — ACTION REQUIRED`.

## What the consumer provides

The text and the `variant`. Badges size themselves to content and never wrap.
