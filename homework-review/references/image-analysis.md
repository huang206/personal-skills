# Image Analysis Protocol — finding the REAL errors

Photos of graded work contain three layers: printed questions, the student's
handwriting, and the teacher's marks. Your job is to extract all three exactly.
The single biggest failure mode is **the vision model auto-correcting the student's
wrong answers** while transcribing — it reads "what the answer should be" instead of
"what the child wrote". This protocol exists to defeat that.

## Why two passes

Field-tested example (4th grade, multiplication). Pass 1 reported:

> "4 × 58 — student decomposed 4 × 50 = 200, 4 × 8 = 32, combined 200 + 32 = **232** ✓"

Reality: the student wrote **202**. The partial products were right, the final
addition slipped, the teacher circled 202 and wrote 232 in red. Pass 1 silently
"fixed" the child's answer, which would have hidden the entire error pattern.
Four errors on that worksheet — pass 1 auto-corrected all four. Pass 2 found them all.

## Pass 1 — inventory prompt (per full page)

Use a transcription prompt that asks for everything, but do NOT trust it for final
error identification:

> Transcribe in detail: 1) the topic/skill of each exercise; 2) every question with
> its number and exact numbers/text; 3) the student's handwritten work and answers;
> 4) the teacher's red-pen marks (checks, X marks, circles, corrections) and WHICH
> items were marked WRONG; 5) any visible score.

Purpose of pass 1: build the page map (which questions exist, which have error
marks, where uncertainty is). Record which items need pass 2.

## Pass 2 — anti-hallucination prompt (MANDATORY)

Re-read every item that has ANY error mark, and every item where you are not
fully certain. Adapt this template (math version shown; swap the wording for
other subjects):

> 重要：请逐个字符仔细读学生手写的数字，不要自动纠正成正确答案——学生可能有
> 算错的地方，你要忠实转录学生实际写的数字。请告诉我：1) 每道题的算式和题号；
> 2) 学生实际手写的每个数字（包括分解式的每个部分积和最终答案，一个字符一个
> 字符地读）；3) 页面上所有红笔痕迹的确切位置和形状（勾/叉/圈/划线/旁边改写的
> 数字），在哪个数字上面。

For English-language analysis, the equivalent key phrases are:
"read the handwritten digits CHARACTER BY CHARACTER", "do NOT auto-correct to the
mathematically correct value", "transcribe what is actually written, even if it is
wrong", "state exactly where each red mark sits and which digit it covers".

Key interrogation questions to resolve per item:
- Student's final answer: digit by digit — is that really a 0 or a 3? a 5 or a 3?
- If partial products / intermediate steps exist: read EACH one separately.
- Teacher's mark: is the X on the final answer, on an intermediate step, or on the
  estimate line? What did the teacher write next to it?
- Word problems: read the answer SENTENCE too (unit words like "books" matter).

## Pass 3 — full-resolution crops (when pass 1 and pass 2 disagree, or marks are fuzzy)

Downscaled 1500px pages make digits ambiguous. Crop the suspect band from the
ORIGINAL image (usually 3024×4032) and analyze the crop:

```bash
convert ORIGINAL.HEIC -crop 3024x800+0+650 -resize 1700x -quality 92 crop.jpg
```

Crop guidance: take the question number plus ~4 lines of context. Don't crop so
tight that the teacher's mark is clipped — the mark is part of the evidence.

## Cross-checks (cheap, catches systematic misses)

1. **Score arithmetic.** A visible score like 22.5/28 must be explainable by your
   error list (5 items × 1 pt + one half = 5.5 lost). If the numbers don't add up,
   you missed an error or misread one.
2. **Student's own error-analysis sheet.** Many worksheets include a "Test Analysis"
   page where the child circles their missed question numbers. The circled set is
   ground truth for WHICH questions were wrong — your red-mark findings must match.
3. **Neighbor questions.** If Q7 and Q9 are confirmed wrong and Q8 is "uncertain",
   crop Q8 specifically rather than trusting the page-level read.

## Verification gate (before any content is written)

For every item in the final error table, run the math yourself:

```python
# example: verify student answer vs correct
print(4 * 58, '| student wrote 202, parts 200 + 32')
# → 232 | so the slip was in 200 + 32, dropping the 3 tens
```

Also verify the ERROR RELATIONSHIP (this becomes the "What happened?" text):
- 202 vs 232 → dropped the tens digit (off by exactly 30)
- 305 vs 405 → missed the carry (off by exactly 100)
- 354 vs 344 → tens digit off by one (carry miscounted)
- 228 vs 238 → same pattern

If you cannot state the precise relationship, re-read the image — you may still be
looking at a transcription artifact rather than the child's real mistake.

## Language-arts and other subjects

The same protocol applies; "digits" becomes "words":
- Read the student's chosen word letter by letter (so/many, and/but look alike at
  low resolution).
- Transcribe the printed sentence verbatim, including the blank position.
- The teacher's correction (word crossed out, replacement written) is the ground
  truth for "correct answer" — but still sanity-check that the corrected word makes
  sense in context before teaching it.

## Output of Phase 2

1. Error table: `problem | student wrote | correct | error pattern (short phrase)`
2. What-went-right list (for the encouragement opening)
3. Confidence notes: any item where the reading remains uncertain → say so in the
   PDF's footnote ("copied from the graded pages; trust the paper if anything
   differs") and, if materially uncertain, to the user in the delivery message.
