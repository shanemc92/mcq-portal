---
name: mcq-generator
description: Generate a multiple-choice question bank (JSON) from plain text or Markdown study notes, in the standard quiz-bank format (title/description/questions with topic, q, correct, distractors, explain).
---

# MCQ Question Bank Generator

Turn study notes into a JSON question bank. Output must be valid JSON matching the schema below, ready to drop into a quiz app.

## Input

Plain text or Markdown notes on any subject. Notes may have headings, bullet points, or be unstructured prose.

## Output schema

```json
{
  "title": "Course or topic name",
  "description": "One-line description (optional).",
  "questions": [
    {
      "topic": "Section or theme this question belongs to",
      "q": "The question text",
      "correct": "The correct answer",
      "distractors": ["Wrong 1", "Wrong 2", "Wrong 3"],
      "explain": "Why the correct answer is right (1-2 sentences)"
    }
  ]
}
```

Rules for the schema itself:
- `topic` groups questions for score breakdowns. Use the notes' own section headings where possible; keep topic names short and consistent (same topic = same exact string across questions).
- Always exactly 3 distractors per question (4 options total).
- `explain` is required, not optional. This is where the learning happens.

## Question-writing rules

**Test understanding, not recall of phrasing.** Don't lift a sentence from the notes and blank out one word. Rephrase the concept so the learner has to actually know it, not pattern-match text.

**Difficulty: make it count.**
- Distractors must be real, adjacent, plausible concepts, not filler. Each wrong answer should be something a partially-informed learner would genuinely consider.
- Prefer distractors that are "almost right": a term from the same category, a close numeric value, a related protocol/command/concept that's commonly confused with the correct one.
- Avoid distractors that are obviously wrong, unrelated, or absurd. If a distractor can be eliminated without knowing the subject, rewrite it.
- Where the notes support it, base at least some questions on edge cases, exceptions, or "which of these is NOT true" style framing, not just top-line facts.

**No answer-length tells.** Never make the correct answer the longest, most detailed, or most hedged option. Keep correct answer and distractors roughly the same length and level of specificity. If the correct answer needs more words to be precise, pad distractors to match, don't leave them short.

**No structural tells.**
- Don't always put the correct answer in the same position (this generator doesn't control display order, but write answers so no one is a giveaway regardless of shuffling).
- Avoid absolute qualifiers ("always", "never", "only") exclusively on wrong answers — vary this across correct and incorrect options, or better, avoid absolutes unless the notes state them precisely.
- Avoid distractors that are grammatically or semantically inconsistent with the question stem (mismatched tense, wrong category of thing) — these are free tells.
- Don't reuse the same distractor across multiple questions unless it's genuinely a plausible wrong answer each time.

**Coverage.**
- Spread questions across all sections/topics in the notes, not just the first part.
- Prioritize concepts the notes emphasize, define explicitly, or repeat — these are more likely to be exam-relevant.
- Skip trivial or non-testable content (e.g. formatting notes, references, "see above").

**Explain field.**
- State why the correct answer is right.
- Where useful, briefly say why the most tempting distractor is wrong — this is where close-distractor questions earn their value.
- Keep it factual, no filler ("great question", "as we can see").

## Process

1. Read through the notes and identify distinct topics/sections.
2. For each topic, draft questions covering its key concepts, aiming for even coverage rather than clustering on the first few paragraphs.
3. For each question, write the correct answer first, then build 3 distractors that are genuinely competitive — pull them from related concepts elsewhere in the notes, common misconceptions, or near-miss values/terms.
4. Check each question against the rules above before finalizing: length parity, no absolute-qualifier tell, distractor plausibility.
5. Assemble into the JSON schema and validate it parses.

## Validation checklist (run before output)

- [ ] Valid JSON, matches schema exactly (field names, types, array of exactly 3 distractors)
- [ ] No `correct` answer is the longest option in its question
- [ ] No `correct` answer is uniquely more specific/hedged than its distractors
- [ ] Every distractor is topically plausible, not random noise
- [ ] `explain` present and non-empty for every question
- [ ] Topics match the notes' own structure and are spelled consistently
- [ ] Questions spread across all major sections of the source notes, not front-loaded
