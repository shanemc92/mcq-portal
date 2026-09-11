# Exam Review -- multi-course flashcard quiz

An offline MCQ flashcard player with four switchable themes. Each course is a
separate JSON bank in `banks/`; a dropdown lets you pick which one to drill.

![screenshot](docs/screenshot.gif)

Four sample banks are included (`networking-fundamentals.json`,
`general-knowledge.json`, `linux-command-line.json`,
`sysadmin_250_Question_Bank.json`) so you can open `index.html` and try the
course switcher immediately.

## Themes

Click the theme button in the top right of the header to cycle through four
themes (green-on-dark, dark, light, and a proto/wireframe look). Your choice
is remembered between visits.

## Folder layout

```
mcq-portal/
  index.html               <- open this
  generate_index.py        <- rebuilds the index after you add/edit banks
  MCQ-Generator SKILL.md   <- instructions for generating a bank with an AI assistant
  banks.js                 <- generated (offline bundle)
  banks/
    manifest.json          <- generated (used when served over http)
    _template.json          <- copy this to start a new course (ignored by the menu)
    networking-fundamentals.json
    general-knowledge.json
    linux-command-line.json
    sysadmin_250_Question_Bank.json
```

## Add a new course

1. Copy `banks/_template.json` to `banks/my-course.json` and fill it in
   (by hand, or hand your notes plus `MCQ-Generator SKILL.md` to an AI
   assistant).
2. Run the index builder:

   ```bash
   python3 generate_index.py
   ```

3. Reload `index.html`. Your course appears in the dropdown.

Files starting with `_` or `.` are ignored, so `_template.json` never shows up.

## Bank format

Either a `{ "title", "description", "questions": [...] }` object or a bare list
of questions. Each question:

```json
{
  "topic": "Section name (groups the score breakdown)",
  "q": "The question text",
  "correct": "The correct option",
  "distractors": ["wrong 1", "wrong 2", "wrong 3"],
  "explain": "Shown after answering (optional)"
}
```

Key names are flexible: `q`/`question`, `correct`/`answer`,
`explain`/`explanation`. Each question needs exactly 3 distractors and 4 unique
options; `generate_index.py` warns and skips anything malformed.

## Running it

- **Offline (phone/desktop):** just open `index.html`. It loads `banks.js`
  (the generated bundle), so no server is needed. Re-run `generate_index.py`
  whenever a bank changes.
- **Served (optional):** `python3 -m http.server` then open
  `http://localhost:8000/index.html`. In this mode the page reads
  `banks/manifest.json` and fetches banks on demand -- handy if you host it,
  though you still run the generator to refresh the manifest.

## Controls

Answer with `A`-`D`, `Enter` or `N` for next, `S` to skip, `Q` to quit and
score. On the results screen, `R` restarts. The report breaks the score down
by topic and flags weak areas (`< review`).
