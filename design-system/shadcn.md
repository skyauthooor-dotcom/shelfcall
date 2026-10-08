# Living with shadcn

Notes for whoever builds the real thing. Everything here is about staying
close to upstream rather than drifting from it.

## Getting the system into a project

```bash
npx shadcn@latest init      # pick Neutral as the base colour
npx shadcn@latest add button card badge input alert item separator switch tabs empty
```

That writes the components into `components/ui/` as **your** source files. There
is no package to upgrade afterwards and no API owned by someone else. Then
replace the generated `:root` and `.dark` blocks with this system's
`tokens.css`, which carries the same values.

Requirements as of this writing: Tailwind v4, React 19 (18 still works), and
one of Next.js, Vite, TanStack Start, React Router, Astro or Laravel.

## Why the previews here are plain HTML

The components in this reference are written as static HTML carrying shadcn's
own `data-slot` attributes — `data-slot="button"`, `data-slot="card-header"` —
and styled in `components/bundle.css`. That is the exact DOM shadcn's React
components emit. It means the previews render without React, and it means the
markup you see here is the markup you will get from the real components.

What is deliberately missing is everything Radix supplies: focus trapping,
roving tabindex, `aria-*` wiring, escape handling, portal management. Do not
port these stylesheets into production and call it shadcn. Run the CLI.

## The four things that are ours

`BookCover`, `HandoverCode`, `ReasonBlock` and `OfferCard` have no shadcn
equivalent. Each is composed from shadcn primitives where possible and each
states in its own README what it is made of, so it can be rebuilt from stock
components in an afternoon.

## Mobile

shadcn is web-only — Radix is DOM, Tailwind classes are CSS. For App Store and
Play Store builds the sibling project is **react-native-reusables**: the same
component names and the same token vocabulary, on Nativewind instead of
Tailwind. The tokens in this system transfer to it unchanged. The components do
not; they are rewritten against React Native primitives.

Plan for that from the start by keeping every colour decision in a token and
none in a component.

## What we changed from shadcn's defaults

Nothing in the colour scale, nothing in the radius scale. Two additions:

- A typeface pair (Geist, Geist Mono). shadcn ships no type tokens.
- A spacing scale written down. shadcn leans on Tailwind's, which is the same
  4px steps; naming them here just gives the reference something to show.

Two contrast failures were found in shadcn's defaults and left exact — the
light-theme focus `ring` at 2.6:1, and white on `destructive` in dark at 2.9:1.
Both are documented on their tokens with the workaround Shelfcall uses. Fixing
them by retinting would put this system quietly out of step with every other
shadcn project, which costs more than it saves.
