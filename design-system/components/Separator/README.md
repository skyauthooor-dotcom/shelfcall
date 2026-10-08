# Separator

A hairline. Shelfcall draws every division with `border` and no shadow anywhere, so this is the only divider in the system.

Horizontal between rows in an `ItemGroup` or between a card's sections. Vertical between two inline controls, where it must be inside a flex row with `align-self: stretch`.

A separator is decoration, so it carries `border`'s 1.3:1 and that is correct. A line that separates two *controls* — the edge of a text field, a toggle's track — carries meaning and takes `input` instead, which is the same value but a different promise. If a divider is doing work, it is probably a border on the thing itself.

## What the consumer provides

The orientation. Nothing else — never a colour, never a width.
