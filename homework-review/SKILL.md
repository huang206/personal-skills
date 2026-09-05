---
name: homework-review
description: >-
  Analyze graded homework/test photos (with teacher markings) to find wrong answers,
  extract knowledge points, and generate a kid-friendly explanation + practice workbook
  PDF with a separate answer key page. Use when the user provides photos of a child's
  graded homework, quiz, or test and asks for 错题分析, 错题讲解, homework error analysis,
  wrong-answer review, knowledge point extraction, similar practice problems, or a
  review/practice PDF generated from graded work. Works for any subject (math,
  language arts, science); output defaults to English for the child plus a Chinese
  parent summary page.
---

# Homework Review — graded work → explanation + practice PDF

You are given photos of a child's graded homework or test. Your job: identify every
wrong answer, extract the knowledge points being tested, and produce ONE polished PDF:
explanations and worked examples covering **all** wrong questions (plus variants and
deeper-check questions), similar practice problems, a Chinese parent summary page, and
an answer key as the **separate last page**.

The HTML→PDF template and scripts are bundled in this skill — no external plugin needed.

## Ground rules (read first)

1. **Never trust vision arithmetic.** Every claimed answer (student's wrong value AND
   the correct value) must be re-computed with a Python one-liner or script before it
   enters the PDF. This applies to math, and to any checkable fact.
2. **Vision models auto-correct wrong answers.** A first-pass transcription will often
   "read" what the student *should* have written instead of what they wrote. A second,
   anti-hallucination pass is MANDATORY. Read `references/image-analysis.md` before
   Phase 2 — it contains the prompt templates that find the real errors.
3. **Answers on the last page, always.** Parents print these. The answer key must be
   its own final page, never sharing a page with questions.
4. **Tone:** written TO the child ("you"), encouraging, grade-appropriate vocabulary,
   celebrate what went right before fixing what went wrong. The parent summary page
   (Chinese) sits just before the answer key.
5. **Memory records, never intervenes.** Every session reads and updates the
   learning-profile memory file (`references/memory-protocol.md` has the format),
   but the memory must NEVER change booklet content on its own: do not add review
   items, trend notes, or any historical material unless the user explicitly asks
   for review/history.

## Workflow

### Phase 0 — Intake

**Read the memory file first** (default `~/.homework-review/memory.md`, or
`$HR_MEMORY`; see `references/memory-protocol.md`): know what the child has
studied and missed before — background only, it must not alter booklet content.

**Subject confirmation gate (mandatory first).** Before analyzing anything in
bulk, look at ONE representative page and declare: subject (math / language arts /
science / …), textbook or worksheet family, grade level, and the evidence you see
(printed headers, question style, e.g. "Wonders grammar page — sentence-combining
exercise"). If this contradicts what the user said or what you assumed, STOP and
confirm with the user before running the full analysis — a wrong subject assumption
silently corrupts every later phase (a grammar worksheet was once fully
misread as multiplication homework).

Confirm from the user's message and the images: subject, grade level, source
(textbook/worksheet name if visible), visible score. Note the child's school language
for the original questions (usually English) — keep original question text verbatim
(translated paraphrase only as an aid if the user asks). Default output: English
kid-facing workbook + one Chinese parent page + English answer key.

### Phase 1 — Image ingestion

iPhone photos usually arrive as HEIC. Normalize every image (HEIC→JPG, long edge
≤2000px, quality 85) with the bundled cross-platform converter (Windows: `python`,
macOS/Linux: `python3`):

```bash
python3 "$SKILL_DIR/scripts/convert_images.py" -o work <source-images...>
```

It uses Pillow + pillow-heif (`pip install pillow pillow-heif`, prebuilt wheels on
Windows/macOS/Linux) and falls back to ImageMagick if present. Photos already in
JPG are simply resized.

### Phase 2 — Error identification (THE critical phase)

Work page by page. Two passes minimum:

**Pass 1 (inventory).** For each page, transcribe: exercise directions, every question
number and text, the student's handwritten answer/work, and every teacher mark
(✓ / ✗ / circle / correction / deducted points). Record which items show error marks.

**Pass 2 (anti-hallucination re-read) — mandatory for every item with an error mark
and every item you're not 100% sure of.** Re-read using the character-by-character
prompt template in `references/image-analysis.md`. Real example from a 4th-grade
multiplication page: pass 1 reported `4 × 58 = 232 ✓`; pass 2 revealed the student
actually wrote **202** (partial products 200 + 32 both correct — the final addition
slipped). Four such errors existed; pass 1 auto-corrected all four.

**Third look if still uncertain:** crop the suspect region from the ORIGINAL image at
full resolution (ImageMagick `convert source.heic -crop WxH+X+Y`), and analyze the
crop. Cross-check against any error-analysis sheet the student filled in (e.g., a
"Test Analysis" page with circled question numbers) and against the visible score
(e.g., 22.5/28 implies 5.5 points lost — your error list must explain the deduction).

**Verification gate.** Before leaving Phase 2, verify in Python: (a) the correct
answer of every problem, (b) the arithmetic relationship between the student's wrong
answer and the right one (off-by-ten? dropped digit? missing carry?). Produce:

- Error table: `problem | student wrote | correct | error pattern (one short phrase)`
- "What went right" list (used for encouragement on page 2 of the PDF)

### Phase 3 — Knowledge points & content design

Read `references/content-design.md` for full rules. In brief:

1. **Group errors into patterns.** Usually 2–4 errors share one root cause ("all in
   the final adding step", "confused so/because direction"). Name the pattern — it
   becomes the spine of the booklet.
2. **Pick ONE central metaphor** for the key concept (road signs for conjunctions;
   KEEP/LOOK/CHANGE for rounding; the newborn hundred for carrying). Kid booklets
   live or die on this.
3. **Plan the document** (structure is fixed, see template):
   - `1. How You Did` — praise + stats cards + error overview table
   - `2. The Big Idea` — the metaphor + a concept table
   - `3+. Fixes` — one block per wrong question: `[What happened?]` + `[How to do it]`
   - `4/5. Checklist / habits` — a 3-step routine + "danger signs" table
   - `5/6. Your Turn` — practice in Parts A/B/C/D
   - `Parent summary (Chinese)` — error patterns + tutoring advice
   - `Answer Key` — last page
4. **Practice coverage rules:** every original error gets (a) its Fix and (b) ≥1
   directly analogous practice item; add variant items (same skill, new surface) and
   1–2 ★ challenge items (find-the-mistake format works brilliantly — reuse the
   child's own error as the planted mistake). Verify every practice answer in Python
   BEFORE writing the answer key. **Hard rule: practice targets ONLY this session's
   errors — never add items from past weak points unless the user explicitly asks
   for review/history.**
5. **Dedup against past practice (the one permitted memory read at generation
   time).** Before finalizing the practice set, scan the session log's "Practice
   items used" lines in the memory file: you may test the SAME skills again, but
   with fresh numbers/sentences — never reuse a parameter set the child has
   already seen (e.g. if 6 × 37 and 9 × 45 appeared before, pick 6 × 39 and
   9 × 54 now). This check only swaps parameters; it never adds or removes topics.

### Phase 4 — Build the HTML

Copy `assets/template.html` (it already contains the full CSS, page skeleton with
section comments, and subject add-on blocks). Fill sections in place. Rules that keep
the layout clean are in `references/layout-rules.md`; the ones that bite most often:

- Each `<div class="page">` holds ~one page of content; don't overstuff (fill target
  40–100% per page).
- No em-dash (—) at a line start: prefer colons/commas mid-sentence.
- Keep `page-break-inside: avoid` on `.q`, `.fix`, `.tip`, `.stats`, `tr` (already in CSS).

### Phase 5 — Render & QA loop

One command does fonts→render→check (Windows: `python`, macOS/Linux: `python3`):

```bash
python3 "$SKILL_DIR/scripts/make_pdf.py" work/booklet.html --output work/booklet.pdf
```

`make_pdf.py` embeds the Noto Sans SC fonts into the HTML as base64 `@font-face`
(solves the Chromium file:// font CORS block — no OS font installation needed on
any platform), renders via Node+playwright with a system-browser fallback
(Chrome/Edge/Chromium auto-discovered on Windows/macOS/Linux), then runs the QA
gate. It prints per-page fill ratio, page count, and font embedding. Fix loop:
fill < 40% or spill pages → move/split `.page` boundaries → re-render → re-check.
The font check MUST pass (no simple-font CJK embedding) — a WinAnsi-embedded CJK
font renders as garbage in Adobe/WPS even though it looks fine in lenient viewers.

First use on a machine: `python3 "$SKILL_DIR/scripts/setup_env.py"` (downloads
fonts to `assets/fonts/`, checks deps, prints per-OS install hints).

Optional final check: render pages to PNG (`check_pdf.py booklet.pdf --pngs previews`)
and eyeball page 1–2 for layout collisions if the harness has vision.

### Phase 6 — Deliver, archive & remember

**Archive the deliverables** after the QA gate passes: move (or copy) the PDF and
its HTML source into `~/homework-review/YYYY-MM-DD-<subject>/` (create the folder
if needed; date = session date, subject = `math` / `language-arts` / etc.; multiple
booklets from the same day share the folder). This is the child's learning
record — report the archive path to the user as the primary PDF location.

**Update the memory file BEFORE reporting to the user** (protocol:
`references/memory-protocol.md`): append the session log entry — including the
"Practice items used" line with each item's key parameters (needed for future
dedup) — and update the Mastery Overview rows for this session's knowledge points.
Memory records only — it must not have influenced the booklet (dedup parameter
swaps are the sole exception, per Phase 3 rule 5).

Give the user: the PDF path, the editable HTML path, the confirmed error table
(the one from Phase 2), and a one-paragraph pattern summary. **Always end the
delivery message with the backfill invitation** (adapt wording, keep the ask):

> 做完后告诉我错了几题/哪几题（例如"错了第 3、7 题"），我会更新学习档案，
> 下次的练习会自动避开出过的题目、换新的数字。

When the user later reports results: backfill that session's Practice line
(e.g. "10 items, 8 correct, missed #3 #7"), adjust Status per the protocol, and
offer the targeted variant worksheet for whatever was missed.

## Files in this skill

| Path | Purpose |
|---|---|
| `references/image-analysis.md` | Vision transcription protocol + anti-hallucination prompt templates. Read before Phase 2. |
| `references/content-design.md` | Error grouping, metaphor, Fix block anatomy, practice design, tone, verification. Read before Phase 3. |
| `references/memory-protocol.md` | Learning-profile memory file: location, format, read/write rules, review-mode trigger. Read at Phase 0 and Phase 6. |
| `references/layout-rules.md` | Pagination, fill, punctuation, QA loop details. Read when building/fixing HTML. |
| `assets/template.html` | The complete HTML/CSS template with section skeleton and subject add-ons. Copy it in Phase 4. |
| `scripts/setup_env.py` | First-use setup: downloads fonts to `assets/fonts/`, checks Python deps + browser, per-OS hints. Cross-platform. |
| `scripts/convert_images.py` | HEIC→JPG / resize via Pillow+pillow-heif (ImageMagick fallback). Cross-platform. |
| `scripts/make_pdf.py` | One-command build: embed fonts (base64 @font-face) → render (Node/playwright, fallback system browser) → QA. |
| `scripts/render_pdf.js` | Playwright renderer (primary path; auto-discovers Chrome/Edge on Win/macOS/Linux). |
| `scripts/render_browser.py` | System-browser renderer fallback (Chrome/Edge/Chromium CLI). Cross-platform. |
| `scripts/check_pdf.py` | PDF QA: page count, fill ratio, text sanity, font embedding. |

## Environment requirements (Windows / macOS / Ubuntu all supported)

- Python 3.9+ with `pip install pillow pillow-heif pymupdf` (prebuilt wheels on all
  three platforms; pymupdf optional — QA degrades gracefully without it)
- ONE renderer, auto-detected in this order:
  1. Node.js + playwright (`npm i -g playwright && npx playwright install chromium`)
  2. Any system Chromium browser — Chrome, Edge (preinstalled on Windows 10/11),
     or Chromium. Nothing to install on a stock Windows or Mac machine.
- Fonts: downloaded once by `setup_env.py` into `assets/fonts/` and embedded into
  each PDF at build time (base64) — no OS-level font installation on any platform.
- Run scripts with `python3` (macOS/Linux) or `python` / `py` (Windows).
