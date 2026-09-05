# personal-skills
Personal Skills for LLM Harness

Personal LLM skill collection, version-controlled. Each folder is a self-contained
skill following the open SKILL.md convention (works with ZCode, Claude Code, and
as pasted instructions in CherryStudio).

## Skills

### homework-error-review

Graded homework/test photos → kid-friendly PDF (error analysis, knowledge-point
explanations, practice problems, Chinese parent page, answer key on the last page),
plus a persistent learning-profile memory file that accumulates knowledge points
and weak areas across sessions (records only — never changes booklet content
unless explicitly asked).

- Platform support: Windows / macOS / Ubuntu (Python core; Node+playwright or any
  Chromium browser incl. system Edge for rendering)
- Docs: see `homework-error-review/README.md`

**Install (use from harnesses):** copy or sync into the cross-tool skill
directory — the installed copy is what harnesses discover:

```bash
rsync -av --delete --exclude '.git' ~/work/personal-skills/homework-error-review/ ~/.agents/skills/homework-error-review/
# Windows (PowerShell): Copy-Item -Recurse -Force $env:USERPROFILE\work\personal-skills\homework-error-review $env:USERPROFILE\.agents\skills\
```

**Note on fonts:** `assets/fonts/*.ttf` (~31 MB, Noto Sans SC, SIL OFL 1.1) are
committed for offline use. A slim clone without them still works —
`python3 scripts/setup_env.py` re-downloads them once.

**Learning-profile memory** lives OUTSIDE this repo at
`~/.homework-error-review/memory.md` (survives skill reinstalls; override with
`$HER_MEMORY`). Back it up separately if desired.
