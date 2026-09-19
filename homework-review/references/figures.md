# Figures — redraw the source pictures (arrays, number lines, models)

Many worksheet problems carry a PICTURE that IS part of the problem: a penny array
that shows 7 × 21, a number line with hops, an area model with labeled cells, a
comparison bar model. When the original had a figure, the booklet must show one
too — quoting only the text loses the very thing the child has to read. Draw
Fix-block figures to match the original, and give practice analogs in the same
figure family with fresh numbers.

## Hard rules

1. **Figures follow the source.** When an original problem is quoted (Fix blocks,
   re-check tables), redraw its figure with the SAME math structure: same
   rows × columns, same partition lines, same labels, same number-line endpoints
   and jump size, same circled cell. Visual style may simplify (dots for coins,
   triangles for trees); the structure may not change. Caption it
   "(redrawn from your worksheet)".
2. **New practice figures stay in the family.** If the source error lived in a
   figure family, the analogous practice item ships with a fresh figure built
   from the new parameters. An array problem asked as bare text is a different
   (easier) problem. Find-the-mistake variants may plant the error IN the figure
   (one jump too few, a wrong cell value, a mislabeled bar).
3. **Counts are arithmetic.** rows × cols, jump size × jump count, cell products,
   bar units — verify every drawn count against the fact in Python before the
   answer key is written. A wrong-count figure teaches the wrong fact.
4. **Inline SVG only** (the build is offline; no external images). Fonts ≥12px
   inside the viewBox, one idea per figure; the template's `figure` CSS already
   sets `page-break-inside: avoid`.
5. **Sizing.** Keep viewBox width ≈720 and height ≤≈260 so figure + caption fit
   under one page of content. For big arrays shrink the dot pitch, never the
   font. Arrays are often wider than they are tall (15+ columns): display them
   smaller with an inline style on the `<svg>` element
   (`<svg style="width:46%" …>`) — the template CSS default of 96% only suits
   full-width strips like number lines and bars. Two or three figures per page
   maximum — each counts toward the 40–100% fill target, and an over-tall figure
   will push the next Fix block onto a spill page.

## Which figure when

| Family | Source looks like | Tests | Snippet |
|---|---|---|---|
| Object/coin array | grid of pennies, trees, stickers | equal-groups multiplication, distributive split | A |
| Jump number line | arcs hopping along a line | skip counting, mental math, rounding zones | B |
| Area model | rectangle split into labeled cells | partial products, 2-digit × 2-digit | C |
| Comparison bars | two stacked bars, one segmented | "n times as many", more/less | D |

## Snippet A — object/coin array (generator; counts guaranteed)

Arrays have too many elements to hand-write reliably, so generate them. Copy this
helper into the session, call it with the ORIGINAL problem's dimensions, and paste
the emitted SVG into a `<figure>`:

```python
def array_svg(rows, cols, split=None, glyph="dot", split_labels=True):
    """Inline-SVG object array. split=N draws a dashed line after column N
    (the distributive split shown on the worksheet)."""
    P = 30 if cols <= 16 else 24            # horizontal pitch
    Q = 26                                   # vertical pitch
    x0, y0 = 34, 24
    W, H = x0 * 2 + (cols - 1) * P, y0 + (rows - 1) * Q + 46
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">']
    for r in range(rows):
        for c in range(cols):
            x, y = x0 + c * P, y0 + r * Q
            if glyph == "dot":   # coins, stickers, counters
                s.append(f'<circle cx="{x}" cy="{y}" r="7.5" fill="#d9a066" stroke="#8a5a2b" stroke-width="1"/>')
            elif glyph == "tree":  # orchard / farm rows
                s.append(f'<path d="M{x},{y-10} L{x+8},{y+4} L{x-8},{y+4} Z" fill="#3e7d4f"/>'
                         f'<rect x="{x-1.5}" y="{y+4}" width="3" height="6" fill="#7a5230"/>')
    if split:  # dashed partition + column braces underneath
        sx = x0 + split * P - P / 2
        s.append(f'<line x1="{sx}" y1="{y0-12}" x2="{sx}" y2="{y0+(rows-1)*Q+12}" '
                 f'stroke="#3f32d0" stroke-width="2" stroke-dasharray="6,5"/>')
        if split_labels:
            yb = y0 + (rows - 1) * Q + 22
            for a, b, lab in ((0, split - 1, str(split)), (split, cols - 1, str(cols - split))):
                xa, xb = x0 + a * P, x0 + b * P
                s.append(f'<line x1="{xa}" y1="{yb}" x2="{xb}" y2="{yb}" stroke="#1a1c1d" stroke-width="1.5"/>')
                s.append(f'<line x1="{xa}" y1="{yb-4}" x2="{xa}" y2="{yb+4}" stroke="#1a1c1d" stroke-width="1.5"/>')
                s.append(f'<line x1="{xb}" y1="{yb-4}" x2="{xb}" y2="{yb+4}" stroke="#1a1c1d" stroke-width="1.5"/>')
                s.append(f'<text x="{(xa+xb)/2}" y="{yb+18}" font-size="14" text-anchor="middle" '
                         f'fill="#1a1c1d">{lab}</text>')
    s.append('</svg>')
    return "\n".join(s)

# example — Michael's pennies, 7 rows of 21, worksheet split after col 20:
print(array_svg(7, 21, split=20))          # → paste inside <figure> … </figure>
# verify the drawn fact while you're at it:
assert 7 * 21 == 147 and 7 * 20 + 7 * 1 == 147
```

Result (schematic — generator emits every element):

```
●●●●●●●●●●●●●●●●●●●●│●      7 rows
●●●●●●●●●●●●●●●●●●●●│●
…                   │
●●●●●●●●●●●●●●●●●●●●│●
├───────── 20 ───────┤─ 1 ─┤
```

Use `<figcaption>Michael's pennies: 7 rows of 21, split 20 + 1 (redrawn).</figcaption>`.

## Snippet B — jump number line (8 jumps of 5 → 40)

```html
<figure>
  <svg viewBox="0 0 720 150" xmlns="http://www.w3.org/2000/svg">
    <defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7"
      markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 Z"
      fill="#3f32d0"/></marker></defs>
    <line x1="40" y1="100" x2="680" y2="100" stroke="#9aa0a6" stroke-width="2"/>
    <!-- ticks + labels every jump (0,5,10 … 40): -->
    <line x1="40"  y1="92" x2="40"  y2="100" stroke="#1a1c1d" stroke-width="2.5"/>
    <line x1="120" y1="92" x2="120" y2="100" stroke="#1a1c1d" stroke-width="2.5"/>
    <line x1="200" y1="92" x2="200" y2="100" stroke="#1a1c1d" stroke-width="2.5"/>
    <line x1="280" y1="92" x2="280" y2="100" stroke="#1a1c1d" stroke-width="2.5"/>
    <line x1="360" y1="92" x2="360" y2="100" stroke="#1a1c1d" stroke-width="2.5"/>
    <line x1="440" y1="92" x2="440" y2="100" stroke="#1a1c1d" stroke-width="2.5"/>
    <line x1="520" y1="92" x2="520" y2="100" stroke="#1a1c1d" stroke-width="2.5"/>
    <line x1="600" y1="92" x2="600" y2="100" stroke="#1a1c1d" stroke-width="2.5"/>
    <line x1="680" y1="92" x2="680" y2="100" stroke="#1a1c1d" stroke-width="2.5"/>
    <text x="40"  y="122" font-size="13" text-anchor="middle">0</text>
    <text x="120" y="122" font-size="13" text-anchor="middle">5</text>
    <text x="200" y="122" font-size="13" text-anchor="middle">10</text>
    <text x="280" y="122" font-size="13" text-anchor="middle">15</text>
    <text x="360" y="122" font-size="13" text-anchor="middle">20</text>
    <text x="440" y="122" font-size="13" text-anchor="middle">25</text>
    <text x="520" y="122" font-size="13" text-anchor="middle">30</text>
    <text x="600" y="122" font-size="13" text-anchor="middle">35</text>
    <text x="680" y="122" font-size="13" text-anchor="middle">40</text>
    <!-- one arc per jump (8 × 80px = 640px track): -->
    <path d="M40,94  Q80,26  120,94"  fill="none" stroke="#3f32d0" stroke-width="2.5" marker-end="url(#arr)"/>
    <path d="M120,94 Q160,26 200,94"  fill="none" stroke="#3f32d0" stroke-width="2.5" marker-end="url(#arr)"/>
    <path d="M200,94 Q240,26 280,94"  fill="none" stroke="#3f32d0" stroke-width="2.5" marker-end="url(#arr)"/>
    <path d="M280,94 Q320,26 360,94"  fill="none" stroke="#3f32d0" stroke-width="2.5" marker-end="url(#arr)"/>
    <path d="M360,94 Q400,26 440,94"  fill="none" stroke="#3f32d0" stroke-width="2.5" marker-end="url(#arr)"/>
    <path d="M440,94 Q480,26 520,94"  fill="none" stroke="#3f32d0" stroke-width="2.5" marker-end="url(#arr)"/>
    <path d="M520,94 Q560,26 600,94"  fill="none" stroke="#3f32d0" stroke-width="2.5" marker-end="url(#arr)"/>
    <path d="M600,94 Q640,26 680,94"  fill="none" stroke="#3f32d0" stroke-width="2.5" marker-end="url(#arr)"/>
    <text x="80" y="20" font-size="14" text-anchor="middle" fill="#3f32d0" font-weight="700">+5</text>
  </svg>
  <figcaption>8 jumps of 5 land on 40 (redrawn from your worksheet).</figcaption>
</figure>
```

Adapt: tick/label values = multiples of the jump size; one arc per jump — the
child's error is often the JUMP COUNT, so draw exactly as many arcs as the fact
demands (or one fewer, on purpose, in a find-the-mistake item).

## Snippet C — area model (46 × 25 = (40 + 6) × (20 + 5))

```html
<figure>
  <svg viewBox="0 0 720 230" xmlns="http://www.w3.org/2000/svg">
    <rect x="80" y="40" width="440" height="140" fill="#f7f7fc" stroke="#3f32d0" stroke-width="2"/>
    <line x1="380" y1="40" x2="380" y2="180" stroke="#3f32d0" stroke-width="1.5"/>
    <line x1="80"  y1="110" x2="520" y2="110" stroke="#3f32d0" stroke-width="1.5"/>
    <text x="230" y="28" font-size="15" text-anchor="middle" fill="#1a1c1d" font-weight="700">40</text>
    <text x="450" y="28" font-size="15" text-anchor="middle" fill="#1a1c1d" font-weight="700">6</text>
    <text x="68"  y="80"  font-size="15" text-anchor="middle" fill="#1a1c1d" font-weight="700">20</text>
    <text x="68"  y="150" font-size="15" text-anchor="middle" fill="#1a1c1d" font-weight="700">5</text>
    <text x="230" y="82"  font-size="17" text-anchor="middle" font-weight="700">800</text>
    <text x="450" y="82"  font-size="17" text-anchor="middle" font-weight="700">120</text>
    <text x="230" y="152" font-size="17" text-anchor="middle" font-weight="700">200</text>
    <text x="450" y="152" font-size="17" text-anchor="middle" font-weight="700">30</text>
  </svg>
  <figcaption>The 46 × 25 area model: every cell = row label × column label (redrawn).</figcaption>
</figure>
```

Adapt: column/row widths need not be proportional, but cell VALUES must equal
label × label — verify all four in Python. If the worksheet circled one cell,
circle the same cell (`<ellipse>` around the value, or fill the cell `#eceafb`).

## Snippet D — comparison bars ("5 times as many")

```html
<figure>
  <svg viewBox="0 0 720 170" xmlns="http://www.w3.org/2000/svg">
    <text x="110" y="53"  font-size="14" text-anchor="end" fill="#1a1c1d">Kyle</text>
    <rect x="120" y="34" width="96" height="32" fill="#eceafb" stroke="#3f32d0" stroke-width="1.5"/>
    <text x="226" y="55"  font-size="14" fill="#1a1c1d">120</text>
    <text x="110" y="118" font-size="14" text-anchor="end" fill="#1a1c1d">Allison</text>
    <rect x="120" y="99" width="480" height="32" fill="#eceafb" stroke="#3f32d0" stroke-width="1.5"/>
    <line x1="216" y1="99" x2="216" y2="131" stroke="#3f32d0" stroke-width="1.5" stroke-dasharray="5,4"/>
    <line x1="312" y1="99" x2="312" y2="131" stroke="#3f32d0" stroke-width="1.5" stroke-dasharray="5,4"/>
    <line x1="408" y1="99" x2="408" y2="131" stroke="#3f32d0" stroke-width="1.5" stroke-dasharray="5,4"/>
    <line x1="504" y1="99" x2="504" y2="131" stroke="#3f32d0" stroke-width="1.5" stroke-dasharray="5,4"/>
    <text x="612" y="120" font-size="15" font-weight="700" fill="#3f32d0">?</text>
    <text x="360" y="90" font-size="14" text-anchor="middle" fill="#3f32d0" font-weight="700">5 units of 120</text>
  </svg>
  <figcaption>"5 times as many": Allison's bar holds 5 of Kyle's bars (redrawn).</figcaption>
</figure>
```

Adapt: the small bar = 1 unit (label the known quantity); the big bar = n units
with dashed separators, its right end a "?" until the answer. Unit width should
be identical across both bars.

## Where figures go in the booklet

- **Fix blocks:** the redrawn ORIGINAL figure sits right under the `.qbox`
  (same structure as the worksheet; the "How to do it" steps may then point at
  its parts: "the dashed line splits 21 into 20 + 1").
- **The Big Idea:** optional — one small figure if the metaphor is pictorial
  (zones, seesaw). Do not decorate; illustrate.
- **Practice:** items in a figure family ship with their figure (fresh numbers
  → fresh dimensions, regenerated/edited SVG, counts re-verified).
- **Answer key:** never a figure; the "why" may reference the figure
  ("5 jumps × 4 = 20, the line proves it").
