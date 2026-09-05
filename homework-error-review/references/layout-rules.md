# Layout Rules — pagination, fill, and the QA loop

The template (`assets/template.html`) already encodes most rules in CSS. This file
explains the ones that require judgment while filling it, and the render→check→fix
loop that produced clean output on every field-tested booklet.

## Page model

- `@page { size: A4; margin: 0 }` — real margins come from `.page` padding
  (13mm 16mm 14mm). The cover is its own fixed-height flex box (296mm — 1mm short
  of the sheet, so it never spills a blank page).
- One `<div class="page">` ≈ one printed page. `page-break-after: always` on every
  `.page` except the last (CSS handles the last one automatically).
- You choose what goes in each `.page`. Chrome will overflow extra content to a new
  page — that creates a near-empty "spill page" (fill < 15%), which the QA gate
  catches. Fix by moving/splitting `.page` boundaries.

## Chunking guidance (field-tested)

| Section | Per-page quantity |
|---|---|
| How You Did (praise + 3 stat cards + error table + note) | exactly one page |
| Big Idea (metaphor + concept table + tip) | one page |
| Fix blocks | 2 long or 3 short per page |
| Checklist/habits page (table + danger signs + warm-up) | one page |
| Practice items | 5–8 per page depending on length |
| Answer key | one page (12 rows fits; if longer, let the table split by rows) |
| Parent page (Chinese) | one page |

Fill target per page: 40–100%. Pages below 40% read as abandoned — add genuinely
useful content (a warm-up strip, a cheat-sheet table, a hint line), don't pad with
decoration.

## Typography traps (each one caused a real defect once)

1. **Em-dash at line start.** Justified text can wrap `— ` to a line start, which
   the QA flags as CJK-style punctuation violation. Mid-sentence, prefer `:` or `,`
   rewrites: "trust the paper — then fix it" → "trust the paper, and then fix it".
   In table cells, put the dash-explanation on a new line via `<br>` deliberately.
2. **Fixed heights / absolute positioning.** The cover uses flex + `margin-top:auto`
   for its footer. Never `position:absolute` for print layout — headless Chrome
   print pipelines reflow it unpredictably.
3. **Options on one line** joined with `&nbsp;&nbsp;&nbsp;`; 4 options of similar
   width can use `.opts.two-col` (CSS multi-column).
4. **Answer blanks**: `<span class="blank"></span>` (dashed underline), widen via
   inline `style="min-width:100mm"` for sentence answers.
5. **Fonts**: the CSS stack is `"NotoSansSC-Local", "Noto Sans SC", "Microsoft YaHei",
   "PingFang SC", "DejaVu Sans", sans-serif`. `NotoSansSC-Local` comes from base64
   @font-face rules that `make_pdf.py` injects at build time from the bundled TTFs
   (assets/fonts/). Do NOT add `<link>`/`url()` references to font files in the
   HTML — relative-path @font-face from a `file://` page is CORS-blocked by
   Chromium (silently falls back to system fonts); base64 injection is the only
   reliable local-font path. Weight 900 (hero, h1, stat numbers) needs the Black
   face — `setup_env.py` downloads all three weights.
6. **No external resources.** No `src=`, no `@import`, no web fonts, no remote
   URLs. All CSS inline; diagrams must be inline SVG. (Exception: the base64
   @font-face block injected by `make_pdf.py` — local, embedded, offline.)

## Render & QA loop

One command (Windows: `python` / `py`; macOS/Linux: `python3`):

```bash
python3 "$SKILL_DIR/scripts/make_pdf.py" booklet.html --output booklet.pdf
```

`make_pdf.py` embeds fonts, renders (Node+playwright, falling back to the system
browser — Chrome/Edge/Chromium), then runs the QA gate automatically.

Interpret `check_pdf.py`:

| Output | Meaning | Fix |
|---|---|---|
| `page N: fill NN%` < 40 | spill page or overstuffed section | move `.page` boundary; merge or split sections |
| page count > expected | something overflowed | find the page pair (full page + tiny page) and rebalance |
| `FONT FAIL: simple-font CJK` | CJK text embedded as WinAnsi simple font → garbles in Adobe/WPS | run `setup_env.py` (downloads fonts), rebuild via `make_pdf.py`; never ship a PDF failing this |
| text extraction empty | raster-only PDF (screenshot pipeline used by mistake) | re-render via the bundled scripts |
| blank pages | trailing empty `.page` or stray `page-break` | check last `.page` has content; remove stray breaks |

Iterate render→check until: expected page count, every page 40–100% fill, font check
pass, no blank pages. Two iterations is typical; four is the historical max.

## Optional visual gate

If the harness has vision, render previews and inspect:

```bash
python3 "$SKILL_DIR/scripts/check_pdf.py" booklet.pdf --pngs previews   # needs pymupdf
```

Check page 1 (cover: hero/kicker/footer placement), one Fix page (vertical math
layout alignment), the practice page (numbering 1..N complete, blanks visible),
and the answer key (all rows present). Look specifically for: overlapping text,
tables past margins, misaligned column arithmetic, orphan headings at page bottom.

## Known-good reference values

From field-tested booklets (A4, this template): cover fills ~96%; content pages
land 45–98%; a 5-Fix booklet with 10–12 practice items totals 7–8 pages + cover.
If your booklet is wildly off (e.g., 14 pages for 4 errors), you over-wrote —
cut, don't shrink fonts.
