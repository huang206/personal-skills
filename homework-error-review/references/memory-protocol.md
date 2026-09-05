# Memory Protocol — the learning profile file

The skill maintains ONE persistent memory file that accumulates knowledge points
and the child's weak areas across sessions.

**Golden rule: the memory RECORDS, it never intervenes.** Do not change any
booklet content based on memory unless the user explicitly asks for review/history.

## Location

- Default: `~/.homework-error-review/memory.md` (survives skill upgrades/reinstalls)
- Override: environment variable `HER_MEMORY=/path/to/file.md`
- Auto-created with the template below on first use. Never delete or truncate it;
  only append sessions and update table rows.

## File format

```markdown
# Learning Profile — 学习档案
Maintained automatically by homework-error-review. Last updated: YYYY-MM-DD.

## Mastery Overview — 知识点掌握总表

| Knowledge point (双语) | Subject | First seen | Last seen | Status | Misses | Error pattern |
|---|---|---|---|---|---|---|
| Rounding to nearest thousand 四舍五入到千位 | math | 2026-09-01 | 2026-09-03 | improving | 3 | picks by leading digit; forgets to round up |

## Session Log — 会话记录

### YYYY-MM-DD · <subject> · <unit/topic>
- Source: <worksheet/test name if known>, score if visible
- Errors: <the confirmed error table from Phase 2, condensed>
- Root cause: <the named pattern(s), one line each>
- What went right: <strengths, one line>
- Metaphor used: <e.g. "KEEP-LOOK-CHANGE chant"> (note if it seemed to help)
- Practice: <N items generated; scores to be backfilled if user reports later>
```

## When to read

At Phase 0 (Intake), right after identifying subject/grade: read the memory file
if it exists. Use it ONLY as background understanding — e.g., recognizing that a
"new" error is actually the same old pattern resurfacing (which sharpens your
Phase 2/3 analysis), or reusing a metaphor that worked before.

## When to write (mandatory, before delivery)

At Phase 6, after the PDF is generated and passes QA, update the memory:

1. **Append a session entry** to the Session Log (format above).
2. **Update the Mastery Overview**, row per knowledge point involved THIS session:
   - New point → add a row (`Status: new`, `Misses: 1`).
   - Existing point → update `Last seen`, increment `Misses` if the child erred
     again, keep `First seen`.
   - **Status transitions:** `new → improving` when the same point reappears with
     fewer/different errors or the user reports most practice items correct;
     `→ mastered` only when the user explicitly reports success (e.g., "做对了",
     "全对", a later test shows the point correct) — never assume mastery from
     your own booklet alone.
   - Do not duplicate rows for the same knowledge point; match on the knowledge
     point name (keep names stable — reuse the existing wording from the table).
3. Update the `Last updated` date in the header.

If the user later reports practice scores ("他做对了10道里的9道"), backfill that
session's Practice line and adjust Status accordingly.

## What must NOT happen

- **No automatic review items.** A booklet's practice set targets ONLY the current
  homework's errors — never inject items from past weak points on your own
  initiative.
- **No automatic trend commentary.** The parent page does not get a
  "compared to last time" note unless the user asks.
- Memory contents are never shown to the child.

## When the user DOES ask for review/history

Trigger phrases: "加历史回顾", "复习之前的", "把以前错的也出点题", "make a review
sheet", "include past weak points", "出一份复习卷". Then:

1. Read the Mastery Overview; select rows with `Status` ≠ mastered, prioritized by
   recency and miss count (3–8 knowledge points is typical).
2. Build a REVIEW booklet: same template, but section 1 becomes "What We're
   Reviewing" (from the memory table), fixes reference the original sessions'
   error patterns, and practice spans all selected points.
3. Mark the booklet's practice items with the session dates they came from
   (small gray text, e.g. "from Sep 1") so the parent sees the lineage.
4. Still update the memory afterwards (a review session is a session).
