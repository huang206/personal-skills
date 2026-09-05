# homework-error-review

Give it photos of a child's graded homework or test → get a polished, kid-friendly
PDF: error analysis, knowledge-point explanations with worked examples for every
wrong question (plus variants and ★ challenge items), similar practice problems, a
Chinese parent summary page, and an answer key on the separate last page.

Every session also accumulates a **learning-profile memory file** (knowledge points
and weak areas) — see "Memory file" below. Memory records only: it never changes
booklet content unless you explicitly ask for review/history.

Field-tested end-to-end on 4th-grade Go Math (rounding, place value, multiplication)
and Wonders Language Arts (conjunctions/commas) worksheets.

**Cross-platform: Windows, macOS, and Linux (Ubuntu).** All tooling is Python
(prebuilt wheels everywhere) + either Node/playwright or any system Chromium
browser — on Windows that means Edge, which ships with the OS.

## What's inside

```
homework-error-review/
├── SKILL.md                 # 6-phase workflow (the entry point for any LLM)
├── README.md                # this file
├── references/
│   ├── image-analysis.md    # two-pass transcription + anti-hallucination prompts
│   ├── content-design.md    # error grouping, metaphors, Fix anatomy, practice rules
│   ├── memory-protocol.md   # learning-profile memory: format, read/write rules
│   └── layout-rules.md      # pagination, fill targets, QA loop
├── assets/
│   ├── template.html        # full CSS + page skeleton + subject add-ons
│   └── fonts/               # created by setup_env.py (downloaded once, never OS-installed)
└── scripts/                 # all cross-platform (Windows: python/py; mac/linux: python3)
    ├── setup_env.py         # fonts download + dependency/browser checks + per-OS hints
    ├── convert_images.py    # HEIC→JPG (Pillow+pillow-heif, ImageMagick fallback)
    ├── make_pdf.py          # ONE command: embed fonts → render → QA
    ├── render_pdf.js        # Playwright renderer (primary)
    ├── render_browser.py    # system Chrome/Edge/Chromium renderer (fallback)
    └── check_pdf.py         # PDF QA gate (fill / blank / text / font-embedding)
```

## Install — three platforms, three harnesses

### ZCode / Claude Code / any harness with skill discovery

| Platform | Install |
|---|---|
| All | Unzip into `~/.agents/skills/` (user scope, all projects) or `<project>/.zcode/skills/` (project override). ZCode and Claude Code discover both. |

On Windows, `tar -xf homework-error-review.zip -C "%USERPROFILE%\.agents\skills\"`
(Windows 10 1803+ ships `tar`, which reads zip) or use Explorer.

### CherryStudio (no native SKILL.md support)

1. **Agent/system prompt**: paste `SKILL.md` + the three `references/*.md` into a
   custom agent's system prompt, keeping the skill folder path so the model can
   call scripts and read the template; or
2. **Knowledge base**: add this folder as a knowledge source and instruct the
   agent: "When the user sends graded homework photos, follow
   homework-error-review/SKILL.md."

Works the same on Windows/macOS/Linux — the model only needs to emit the commands;
the scripts run locally.

## Runtime requirements (per platform)

Common core (all platforms): **Python 3.9+** and `pip install pillow pillow-heif pymupdf`
(prebuilt wheels for Windows/macOS/Linux; pymupdf optional — QA degrades without it).

| Need | Windows | macOS | Ubuntu |
|---|---|---|---|
| Python | `winget install Python.Python.3.12` (or python.org) | `brew install python` | preinstalled |
| pip deps | `py -m pip install pillow pillow-heif pymupdf` | `python3 -m pip install …` | `python3 -m pip install …` |
| Renderer | **nothing** — Edge ships with Windows 10/11 | browser usually present; else `brew install --cask google-chrome` | `sudo apt install chromium-browser` |
| Optional Node path | `winget install OpenJS.NodeJS` then `npm i -g playwright && npx playwright install chromium` | same via brew-installed node | same |

Fonts: none installed at OS level. `setup_env.py` downloads Noto Sans SC
(400/700/900, ~31 MB, once, network needed) into `assets/fonts/`, and `make_pdf.py`
embeds them into each PDF build as base64 `@font-face` — the verified workaround
for Chromium's `file://` font CORS block, and it makes output identical on every OS.

Self-test after install (Windows: `python`/`py`; macOS/Linux: `python3`):

```bash
python3 scripts/setup_env.py                     # fonts + deps + browser check
python3 scripts/make_pdf.py assets/template.html --output /tmp/t.pdf
```

## Memory file (knowledge points across sessions)

- Location: `~/.homework-error-review/memory.md` (override with the `HER_MEMORY`
  environment variable). Survives skill upgrades; back it up by copying that one file.
- After every booklet: session log entry + mastery table update
  (knowledge point / status new→improving→mastered / miss count / error pattern).
- **Privacy of content**: memory accumulates silently. Booklets are built from the
  CURRENT homework only — no review items, no trend notes, unless you explicitly
  ask ("加历史回顾", "复习之前的", "make a review sheet").

## Key hard-won behaviors encoded in this skill

1. **Anti-hallucination transcription**: vision models silently auto-correct
   children's wrong answers (read 202 as 232). The mandatory second pass with the
   character-by-character prompt is what actually finds the errors.
2. **No vision arithmetic**: every answer in the booklet is re-computed in Python.
3. **Font-embedding gate**: CJK in a simple-font (WinAnsi) PDF renders as garbage
   in Adobe/WPS while looking fine in lenient viewers — `check_pdf.py` fails the
   build if it detects this.
4. **Fill-ratio gate**: spill pages and overstuffed sections are caught by
   per-page pixel analysis, with a defined rebalancing loop.
5. **Answer key always the last page**; parent summary (Chinese) just before it.
6. **Memory records, never intervenes** — accumulation without unrequested
   personalization.

## License notes

- Skill code/docs: use freely (MIT-style).
- Noto Sans SC fonts: SIL Open Font License 1.1 — downloaded at setup time from
  Google Fonts, not bundled in this package.
