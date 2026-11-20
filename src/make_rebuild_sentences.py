"""Every sentence of the rebuilt manuscript that carries a number, with the file each number is read from (Brief 29).

Reads manuscript/rebuild/numbers_trace.json, which `manuscript/numbers_check.py --rebuild` writes as it traces each
number, and the manuscript as submitted on 17 November 2026 (manuscript/submitted_20261117/Satte_JES_manuscript.docx).
A number is marked "new" when the submitted manuscript does not contain it as written (commas ignored), so the list
shows which numbered sentences carry numbers the earlier text did not state.

Writes manuscript/rebuild/numbered_sentences.md.  Usage: python3 src/make_rebuild_sentences.py
"""
import json
import os
import re

from docx import Document

HERE = os.path.dirname(os.path.abspath(__file__))
RB = os.path.join(HERE, "..", "manuscript", "rebuild")
SUB = os.path.join(HERE, "..", "manuscript", "submitted_20261117", "Satte_JES_manuscript.docx")


def numbers(text):
    return {m.group(0).replace(",", "") for m in re.finditer(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?", text)}


def main():
    d = Document(SUB)
    old = " ".join([p.text for p in d.paragraphs] + [c.text for t in d.tables for r in t.rows for c in r.cells])
    old_nums = numbers(old)
    trace = json.load(open(os.path.join(RB, "numbers_trace.json")))
    groups = []
    for t in trace:
        key = (t["segment"], t["sentence"])
        if not groups or groups[-1][0] != key:
            groups.append((key, []))
        groups[-1][1].append(t)
    out = ["# Every numbered sentence of the rebuilt manuscript, with its sources (20 November 2026)", "",
           "Written by `src/make_rebuild_sentences.py` from the numbers check's trace (`numbers_trace.json`). Each "
           "sentence is followed by its numbers, the file and value each is read from, and \"new\" where the manuscript "
           "as submitted on 17 November 2026 does not state that number. Sentences are as the check reads them, with "
           "LaTeX spacing marks (~ is a space).", ""]
    seg = None
    n_new = n_sent = n_sent_new = 0
    for (segment, sentence), items in groups:
        if segment != seg:
            out += ["", f"## {segment}", ""]
            seg = segment
        n_sent += 1
        flags = []
        any_new = False
        for t in items:
            new = t["number"].replace(",", "").replace("$", "") not in old_nums and not t["number"].startswith(("2\\times", "5.565"))
            any_new |= new
            n_new += new
            flags.append(f"   - {t['number']}{' (new)' if new else ''}: {t['source']}")
        n_sent_new += any_new
        out.append(f"{n_sent}. {sentence}")
        out += flags
    out[3:3] = [f"{n_sent} numbered sentences; {n_sent_new} of them carry a number the submitted manuscript does not "
                f"state ({n_new} numbers in all).", ""]
    open(os.path.join(RB, "numbered_sentences.md"), "w").write("\n".join(out) + "\n")
    print(n_sent, "sentences;", n_sent_new, "with new numbers;", n_new, "new numbers")


if __name__ == "__main__":
    main()
