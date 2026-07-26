#!/usr/bin/env python3
"""
generate_index.py -- build the quiz index from banks/*.json
===========================================================
Scans the ./banks folder for question-bank JSON files and writes:

  banks/manifest.json  -- list of {file,title,description,count,topics}
                          (used when the page is SERVED over http)
  banks.js             -- window.QUIZ_BANKS = {...} with all banks inlined
                          (used when quiz.html is opened directly as file://)

Run this whenever you add or edit a bank:

    python3 generate_index.py

Bank file format (either shape is accepted):

    { "title": "My Course", "description": "...", "questions": [ ... ] }
  or a bare list:
    [ ... ]

Each question is an object. Keys are flexible:
    topic        (default "General")
    q / question                       -- the prompt            (required)
    correct / answer                   -- the correct option    (required)
    distractors  (list of exactly 3 wrong options)              (required)
    explain / explanation              -- shown after answering (optional)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BANKS_DIR = os.path.join(HERE, "banks")


def prettify(name):
    stem = os.path.splitext(name)[0]
    return stem.replace("-", " ").replace("_", " ").strip().title()


def get(obj, *keys):
    for k in keys:
        if k in obj and obj[k] not in (None, ""):
            return obj[k]
    return None


def normalise_question(raw, where):
    """Return a clean question dict or raise ValueError."""
    if not isinstance(raw, dict):
        raise ValueError(f"{where}: question is not an object")
    q = get(raw, "q", "question")
    correct = get(raw, "correct", "answer")
    distractors = raw.get("distractors")
    topic = get(raw, "topic") or "General"
    explain = get(raw, "explain", "explanation") or ""

    if not q or not correct:
        raise ValueError(f"{where}: missing question text or correct answer")
    if not isinstance(distractors, list) or len(distractors) != 3:
        raise ValueError(f"{where}: 'distractors' must be a list of exactly 3")
    options = [correct] + list(distractors)
    if any(not isinstance(o, str) or not o.strip() for o in options):
        raise ValueError(f"{where}: options must be non-empty strings")
    if len(set(options)) != 4:
        raise ValueError(f"{where}: options are not all unique")

    return {
        "topic": str(topic),
        "q": str(q),
        "correct": str(correct),
        "distractors": [str(d) for d in distractors],
        "explain": str(explain),
    }


def load_bank(path):
    """Return (meta, questions) or (None, None) on failure (prints reason)."""
    name = os.path.basename(path)
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        print(f"  [SKIP] {name}: invalid JSON ({e})")
        return None, None

    if isinstance(data, list):
        raw_questions = data
        title = prettify(name)
        description = ""
    elif isinstance(data, dict):
        raw_questions = data.get("questions", [])
        title = get(data, "title") or prettify(name)
        description = get(data, "description") or ""
    else:
        print(f"  [SKIP] {name}: top level must be a list or object")
        return None, None

    if not raw_questions:
        print(f"  [SKIP] {name}: no questions found")
        return None, None

    questions, seen, bad = [], set(), 0
    for i, raw in enumerate(raw_questions):
        try:
            qn = normalise_question(raw, f"{name}#{i}")
        except ValueError as e:
            print(f"  [WARN] {e}")
            bad += 1
            continue
        if qn["correct"] in qn["distractors"]:
            print(f"  [WARN] {name}#{i}: correct answer also in distractors")
            bad += 1
            continue
        if qn["q"] in seen:
            print(f"  [WARN] {name}#{i}: duplicate question text (kept once)")
            continue
        seen.add(qn["q"])
        questions.append(qn)

    if not questions:
        print(f"  [SKIP] {name}: no valid questions after checks")
        return None, None

    topics = sorted({q["topic"] for q in questions})
    meta = {
        "file": name,
        "title": title,
        "description": description,
        "count": len(questions),
        "topics": topics,
    }
    note = f" ({bad} skipped)" if bad else ""
    print(f"  [OK]   {title}: {len(questions)} questions, "
          f"{len(topics)} topics{note}")
    return meta, questions


def main():
    if not os.path.isdir(BANKS_DIR):
        print(f"No banks/ folder found at {BANKS_DIR}")
        print("Create it and add at least one *.json bank, then re-run.")
        sys.exit(1)

    files = sorted(f for f in os.listdir(BANKS_DIR)
                   if f.lower().endswith(".json") and f != "manifest.json"
                   and not f.startswith(("_", ".")))
    if not files:
        print("No bank .json files in banks/ -- nothing to do.")
        sys.exit(1)

    print(f"Scanning {len(files)} file(s) in banks/ ...")
    manifest = []
    inline = {}
    for f in files:
        meta, questions = load_bank(os.path.join(BANKS_DIR, f))
        if meta is None:
            continue
        manifest.append(meta)
        inline[meta["title"]] = {
            "title": meta["title"],
            "description": meta["description"],
            "topics": meta["topics"],
            "questions": questions,
        }

    if not manifest:
        print("No valid banks -- aborting.")
        sys.exit(1)

    manifest.sort(key=lambda m: m["title"].lower())

    with open(os.path.join(BANKS_DIR, "manifest.json"), "w",
              encoding="ascii") as fh:
        json.dump(manifest, fh, ensure_ascii=True, indent=1)

    with open(os.path.join(HERE, "banks.js"), "w", encoding="ascii") as fh:
        fh.write("// AUTO-GENERATED by generate_index.py -- do not edit.\n")
        fh.write("window.QUIZ_BANKS = ")
        json.dump(inline, fh, ensure_ascii=True)
        fh.write(";\n")

    total = sum(m["count"] for m in manifest)
    print("-" * 60)
    print(f"Wrote banks/manifest.json and banks.js")
    print(f"{len(manifest)} bank(s), {total} questions total.")
    print("Open index.html (offline) or serve the folder over http.")


if __name__ == "__main__":
    main()
