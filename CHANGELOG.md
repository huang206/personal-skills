# Changelog

## v1.1.1 — 2026-09-05

### homework-error-review

- **Archive rule** (Phase 6): every delivered PDF + HTML source is archived into
  `~/homework-review/YYYY-MM-DD-<subject>/` — together with the memory file this
  forms the child's complete learning record. Existing booklets retroactively
  archived (2026-09-01-math … 2026-09-05-math).

## v1.1.0 — 2026-09-05

### homework-error-review

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

### homework-error-review

- Initial release: 6-phase workflow (image ingestion → anti-hallucination error
  identification → knowledge extraction → booklet generation → PDF QA → delivery),
  persistent learning-profile memory (records only, never intervenes),
  cross-platform support (Windows/macOS/Ubuntu; Python core; Node+playwright or
  system Chromium/Edge; base64 @font-face font embedding), HTML/CSS template,
  setup/convert/render/QA scripts, Noto Sans SC fonts (OL 1.1) bundled for
  offline use.
