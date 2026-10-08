# Input

Text entry: `Label`, the control, and either a description or an error under it. Covers `Input`, `Textarea` and the native `Select`, which share one border, one radius and one height.

Every control has a visible label. Placeholder text is an example of a good answer, never a substitute for the label — it disappears the moment someone types, and it is invisible to a screen reader as a name.

## Errors

An invalid control takes `aria-invalid="true"`, which turns its border `destructive`, and the message goes in `field-error` beneath it. Write what happened and what to do: *That is not the code on the buyer's order. Ask them to read it again.* Never a bare `Invalid`.

The error lives next to the field that caused it. A summary at the top of a form is not enough on a phone, where the field may be off screen.

## Shelfcall's required note

On an open-ended request, the bookseller's note is a required `Textarea` and it is the **first** field on the form, above condition and price. A reader who wrote *something with a crazy scientist* has nothing else to choose between two copies by. The placeholder shows the shape of a good answer rather than describing it.

## How many fit on a screen

A labelled input costs about 78px, a textarea about 115px, and a screen's
heading block about 135px. With a 690px budget that is **four fields and a
heading**, or three plus a textarea. Past that, split the form — see *Forms* in
the brand book. Never answer a long form by shrinking the label, the control or
the gap between them.

## What the consumer provides

The label text, the control's `id` (the label's `for` must match), a placeholder where an example helps, and the description or error.
