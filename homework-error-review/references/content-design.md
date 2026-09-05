# Content Design — from error table to a booklet children will actually read

The PDF is for the CHILD first (they read it alone or with a parent), with one
Chinese page for the parent. Every design decision below follows from that.

## Tone rules (non-negotiable)

- Second person throughout: "You scored…", "You picked…", "Your turn".
- **Open with what went right** and be specific: "your multiplication facts were
  100% correct", "your commas and capital letters were strong". Earned praise only —
  name real strengths from the "what went right" list.
- Never harsh. Errors are traps, sneaky questions, or slipped steps — not failures.
  Good phrases: "Sneaky!", "That makes sense — but it's a trap!", "The 3 tens
  vanished", "the newborn hundred".
- Vocabulary at the child's grade level. Short sentences. Say rules out loud as
  chants: "Keep… Look… Change!", "the open mouth eats the bigger number".
- Close every section with forward motion: "Fix these five, and the next test is
  yours!" / "You've got this!"

## Error grouping → booklet spine

Group the error table into 1–3 patterns. Typical patterns:

| Pattern type | Example | Becomes |
|---|---|---|
| Process-step failure | 4 errors, all in the final adding step | "The Last Step Is Adding" (whole booklet spine) |
| Concept confusion | so/because direction reversed | "Which way does the arrow point?" |
| Rule misapplication | rounds by leading digit, not by the boss digit | "Zones, not guesses" |
| Careless variant | right method, wrong carry | "The Slow-Down Checklist" |

If errors don't group (rare), keep Fixes individual and make the Big Idea about the
meta-skill (checking work). Never force a fake pattern.

## The central metaphor

One image carries the concept. Field-tested winners:
- Conjunctions → **road signs** (and=PLUS, but=SURPRISE, or=CHOICE, so=RESULT→, because=REASON←)
- Rounding to a place → **KEEP / LOOK / CHANGE** three-step chant + the boss digit
- Which numbers round to X → **zones** (every friendly number owns a zone: 5,500–6,499)
- Carrying in addition/multiplication → **the newborn hundred / let the 9s roll over**
- Comparing numbers → **digit-by-digit until the first difference decides**

The metaphor appears in section 2, is reused in every Fix, and returns in the
checklist page. One metaphor per booklet.

## Fix block anatomy (one per wrong question)

```
h2:  Fix N · <span class="say">wrong → right</span>   (e.g. "4 × 58: 202 → 232")
.qbox: the original problem, verbatim
[What happened?]  — what the child actually did, where it slipped, in their terms
[How to do it]    — the correct method step by step, ending "…= ANSWER. ✔"
```

Rules:
- 2–3 Fix blocks per page (each block is atomic; never split one across pages).
- Every Fix must reference the metaphor at least once.
- For arithmetic: show the vertical/step layout (`.steps`, `.coladd` classes) rather
  than describing it in prose. For grammar: show the corrected sentence in bold.

## Practice design (Parts A–D)

Structure and sizing (10–12 items total is the sweet spot):

- **Part A — direct analogs** of the errors (same skill, same format, fresh numbers).
  At least one per original error.
- **Part B — the method in its standard form** (e.g. stacked multiplication so the
  carry is visible; add-commas lines; zone-finding fill-ins).
- **Part C — word problems** mirroring the source worksheet's word problems.
- **Part D — ★ challenge, "be the teacher"**: find-the-mistake items where the
  planted mistake IS the child's own error pattern ("Maya solved 5 × 47 … 200 + 35
  = 255. Find her mistake."). This is the highest-value item type — diagnosing
  one's own error pattern proves mastery. 1–2 items.

Additional rules:
- Every answer gets a one-line "why" in the answer key (the why is where learning
  sticks — write it as a chant or pattern name when possible).
- Hints (small gray text) allowed on 2–3 items, never on Part D.
- **Verify every answer in Python before writing the key.** For distractor-based MC,
  verify that each distractor is actually wrong AND understand what wrong belief it
  catches (state it in the key when useful).

## Answer key page (always the LAST page)

- 3-column table: `#` (8%) | `Answer` (18–22%) | `Why it's right` (rest).
- Opening note: "For checking after you finish. No peeking!"
- Closing `.tip` "How did it go?": a 3-tier encouraging rubric
  (top tier = named mastery, e.g. "zone master", "last-step master";
  mid = "strong, reread X once";
  low = "no problem — reread section N, redo the Fixes, try again tomorrow").
- Never shame a low tier; always end "You've got this!"

## Parent summary page (Chinese, just before the answer key)

One page, for the adult, structure:
1. 一句话总评（先肯定：做对了什么，错题集中在哪个知识点）
2. 错题模式表：`题目 | 孩子的答案 | 正确答案 | 错误模式`
3. 共性问题归纳（1–2 段）：错误的根源是什么、为什么这类题容易错
4. 家庭辅导建议（3 条具体可操作的：怎么做、练什么、注意什么）
5. 使用建议：先让孩子独立读前几节并完成练习，再一起核对答案页

Keep it compact (the page must not overflow); use the same table styles.

## Language configuration

Default: English kid pages + Chinese parent page + English answer key. If the user's
child studies in another language, mirror the source material's language for the kid
pages. Section titles are data, not template constants — translate accordingly
(但家长页固定用中文，除非用户另有说明).
