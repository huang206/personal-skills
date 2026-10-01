# Changelog

## v1.5.0 — 2026-10-01

### homework-review

- **Convert non-JPG/PNG photos locally, first** (Phase 1 rewritten): HEIC (or any
  non-JPG/PNG format) arrives as a raw binary attachment no vision step digests;
  convert to JPG locally BEFORE any analysis. First try the system converter
  one-shot (`for f in *.HEIC; do heif-convert "$f" "${f%.HEIC}.jpg"; done`,
  Ubuntu: `sudo apt install libheif-examples`), then — always, because it also
  normalizes to long edge ≤2000px / quality 85 — the bundled
  `convert_images.py`. Field-tested 2026-10-01.
- **Codec fix documented**: `heif-convert` failing with `Unsupported codec` means
  system libheif lacks the HEVC decoder; on Ubuntu the verified fix is
  `sudo apt install libheif-plugin-libde265` (needs the user's password — ask
  them to run it; the bundled Pillow converter covers the gap meanwhile).
- **Vision fallback to visual-judge agents** (field-tested 2026-10-01): local
  conversion ≠ viewable images. If Read returns only a CDN/text URL and the 4_5v
  image MCP answers `1210` on every input (including known-good public URLs —
  server-side dead), stop probing image tools and dispatch the Phase 2
  transcription passes to `documents:visual-judge` / `pdf:visual-judge` agents,
  whose Read renders JPG/PNG natively: normalized JPGs for pass 1, full-res
  crops (Pillow from the ORIGINAL files) for pass 2. Phase 5's optional visual
  check now names the same judge dispatch as the no-native-vision gate.

## v1.4.0 — 2026-09-19

### homework-review

- **Figures follow the source** (new ground rule 6): when an original problem
  carries a figure (coin/object arrays, jump number lines, area models,
  comparison bars), the booklet now redraws it — in that problem's Fix block and
  in fresh-number practice analogs of the same figure family. Quoting a pictured
  problem as text alone quietly changes the question (a 7 × 21 penny array became
  bare text in the 2026-09-18 booklet, which prompted this).
- New `references/figures.md`: hard rules (structure must match the source,
  counts Python-verified, inline SVG only, sizing), a which-figure-when table,
  and copy-adapt snippets — Python generator for object arrays (dots/trees,
  optional dashed distributive split with column braces), jump number line with
  arrow markers, labeled area model, "n times as many" comparison bars.
  Smoke-tested: all four families render clean in the PDF pipeline (147-coin
  array, 8-jump line, 4-cell model, 5-unit bars, 5×14 tree array).
- `references/image-analysis.md`: Pass 1 now transcribes figures (type,
  dimensions, labels, partitions); interrogation questions demand COUNTING
  figures; crops cover figure regions; Phase 2 output gains a figure inventory.
- `references/content-design.md`: Fix blocks redraw their source figure under
  the qbox; practice items in figure families ship with fresh figures;
  find-the-mistake variants may plant the error in the figure.
- `SKILL.md` (ground rule, Pass 1, Phase 4 bullet, files table),
  `assets/template.html` (pointer comment), `README.md` (tree + behaviors)
  updated to point at the library.

## v1.3.0 — 2026-09-12

### homework-review

- **Knowledge points grouped by subject** in the learning-profile memory
  (`~/.homework-review/memory.md`): `## Mastery Overview` now holds one
  `### <Subject>` sub-table per subject (`### Math 数学`, `### Language Arts
  英语语法`, …; slugs match the Session Log's `· <subject> ·` field), and each
  sub-table drops the redundant Subject column. Existing profile migrated
  in place (16 math + 2 language-arts rows).
- `references/memory-protocol.md`: format template and write rules updated —
  new rows go under the matching subject sub-table, a new subject creates its
  sub-table, points never move between subjects. SKILL.md Phase 6 points to
  the grouping rule.

## v1.2.0 — 2026-09-05

### homework-review (renamed from homework-error-review)

- **Global rename** `homework-error-review` → `homework-review`: skill directory,
  SKILL.md `name` field, all docs/scripts references, and the distribution zip.
- **Memory file moved**: `~/.homework-error-review/memory.md` →
  `~/.homework-review/memory.md` (existing profile migrated); environment override
  renamed `HER_MEMORY` → `HR_MEMORY`.
- Selftest re-run 7/7 from the renamed tree; installed copy re-synced under the
  new name (old `~/.agents/skills/homework-error-review/` removed).

## v1.1.1 — 2026-09-05

### homework-review

- **Archive rule** (Phase 6): every delivered PDF + HTML source is archived into
  `~/homework-review/YYYY-MM-DD-<subject>/` — together with the memory file this
  forms the child's complete learning record. Existing booklets retroactively
  archived (2026-09-01-math … 2026-09-05-math).

## v1.1.0 — 2026-09-05

### homework-review

- **Subject confirmation gate** (Phase 0): declare subject/textbook/grade with
  evidence from one page before full analysis; halt on mismatch with the user's
  description. Prevents whole-run misidentification (a grammar worksheet was once
  fully misread as multiplication homework before this rule).
- **Practice dedup**: session log now records each generated item's key parameters
  ("Practice items used"). Phase 5 checks past parameters before finalizing —
  same skills, always fresh numbers/sentences. Read-only check; never adds topics
  (the sole permitted generation-time memory use).
- **Score backfill loop**: delivery message now always invites the parent to
  report missed items; protocol defines the backfill procedure (update Practice
  line, adjust mastery status, offer — not auto-generate — variant practice).
- **tests/selftest.py**: one-command install verification (deps, fonts, renderer,
  full template build + QA gate) for any platform.

## v1.0.0 — 2026-09-05

### homework-review

- Initial release: 6-phase workflow (image ingestion → anti-hallucination error
  identification → knowledge extraction → booklet generation → PDF QA → delivery),
  persistent learning-profile memory (records only, never intervenes),
  cross-platform support (Windows/macOS/Ubuntu; Python core; Node+playwright or
  system Chromium/Edge; base64 @font-face font embedding), HTML/CSS template,
  setup/convert/render/QA scripts, Noto Sans SC fonts (OL 1.1) bundled for
  offline use.
