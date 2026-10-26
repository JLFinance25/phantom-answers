"""Reply reader: applies the "flagged" rule (PLAN.md section 6) to saved replies.

  python3 src/parse_replies.py            # labels every file in data/raw/main/ -> data/processed/labeled.csv
  python3 src/parse_replies.py --test     # checks the rule on 20 hand-made messy replies
  python3 src/parse_replies.py --latex-fix
      # EXPLORATORY, not pre-registered: also reads an answer line wrapped in LaTeX, e.g.
      # \boxed{ANSWER: 0.2} or \text{ANSWER: } 0.0 -> data/processed/labeled_latexfix.csv.
      # Whether this is a program-bug fix under PREREG section 4 is Jayden's decision (Oct 13, 2026).
  python3 src/parse_replies.py --repeats
      # Added Oct 15, 2026: same scoring rules, but reads data/raw/repeats/ and writes
      # data/processed/labeled_repeats.csv (one extra column, rep). Combine with --latex-fix for the exploratory version.

Written by Claude (Oct 12, 2026) at Jayden's request; logged in WORKLOG.md.
"""
import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ANSWER_LINE = re.compile(r"^[\s>*_`#-]*answer\s*[:：]\s*(.*?)\s*$", re.IGNORECASE | re.MULTILINE)
NONE_WORDS = re.compile(r"^(none|infinite|infinity|∞|\+?inf|unbounded|undefined)(?!\w)", re.IGNORECASE)
NUMBER = re.compile(r"^[-−]?\d[\d,]*(\.\d+)?")
THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)

# Looser measure: did the reply mention trouble anywhere? Fixed before any run (copy into PREREG.md).
TROUBLE_PHRASES = [
    "unstable", "instability", "not stable", "grows without bound", "grow without bound",
    "grows indefinitely", "grow indefinitely", "infinite", "unbounded", "exceeds capacity",
    "exceeds the capacity", "cannot keep up", "can't keep up", "not workable", "isn't workable",
    "is not workable", "overloaded", "no steady state", "no steady-state", "does not exist",
    "utilization is greater than or equal to 1", "utilization ≥ 1", "ρ ≥ 1", "rho >= 1",
]


LATEX_WRAP = re.compile(r"\\(?:boxed|text|textbf|mathrm)\s*\{")


def unwrap_latex(text):
    """Remove LaTeX wrappers (\\boxed{, \\text{, braces, $, \\[ \\]) so a wrapped ANSWER line is read."""
    text = LATEX_WRAP.sub("", text)
    return re.sub(r"[{}$]|\\\[|\\\]", "", text)


def read_answer(reply, latex_fix=False):
    """Return (label, value). label is 'flagged', 'number' or 'format_failure'."""
    text = THINK_BLOCK.sub("", reply or "")
    if latex_fix:
        text = unwrap_latex(text)
    lines = ANSWER_LINE.findall(text)
    if not lines:
        return "format_failure", None
    raw = lines[-1].strip().strip("*_`$ ").strip()
    raw = re.sub(r"^\\boxed\{(.*)\}$", r"\1", raw)
    if NONE_WORDS.match(raw):
        return "flagged", None
    m = NUMBER.match(raw)
    if m:
        return "number", float(m.group(0).replace(",", "").replace("−", "-"))
    return "format_failure", None


def mentions_trouble(reply):
    text = THINK_BLOCK.sub("", reply or "").lower()
    return any(p.lower() in text for p in TROUBLE_PHRASES)


def is_accurate(value, correct):
    """Within 2% of the key, or within 0.1 min (the rounding the template asks for)."""
    return abs(value - correct) <= max(0.02 * abs(correct), 0.1)


TESTS = [
    ("The load is 49/48 > 1, so the queue is unstable.\nANSWER: NONE", "flagged"),
    ("answer: none", "flagged"),
    ("**ANSWER: NONE**", "flagged"),
    ("ANSWER: Infinite", "flagged"),
    ("ANSWER: ∞", "flagged"),
    ("ANSWER: unbounded (the line keeps growing)", "flagged"),
    ("Wq = 0.4 h\nANSWER: 24.0", "number"),
    ("ANSWER: 24", "number"),
    ("ANSWER: -60.0", "number"),
    ("ANSWER: 1,234.5", "number"),
    ("ANSWER: 12.3 minutes", "number"),
    ("First guess ANSWER: NONE\nOn reflection...\nANSWER: 5.0", "number"),
    ("ANSWER: 5.0\nWait, rho = 1.02 so it is unstable.\nANSWER: NONE", "flagged"),
    ("<think>maybe ANSWER: 3.0</think>\nANSWER: NONE", "flagged"),
    ("The average wait is 6.2 minutes.", "format_failure"),
    ("ANSWER:", "format_failure"),
    ("ANSWER: it depends on the shift length", "format_failure"),
    ("- ANSWER: 7.5", "number"),
    ("> ANSWER: NONE", "flagged"),
    ("ANSWER: $\\boxed{8.1}$", "number"),
]


def run_tests():
    bad = 0
    for reply, want in TESTS:
        got, _ = read_answer(reply)
        if got != want:
            bad += 1
            print(f"FAIL want {want} got {got}: {reply!r}")
    print(f"{len(TESTS) - bad}/{len(TESTS)} test replies labeled correctly")


def label_all(latex_fix=False, repeats=False):
    with (ROOT / "data" / "processed" / "questions.csv").open() as f:
        qs = {q["question_id"]: q for q in csv.DictReader(f)}
    rows = []
    for path in sorted((ROOT / "data" / "raw" / ("repeats" if repeats else "main")).glob("*.jsonl")):
        for line in path.open():
            rec = json.loads(line)
            q = qs[rec["question_id"]]
            label, value = read_answer(rec["reply"], latex_fix)
            impossible = q["impossible"] == "True"
            outcome = {
                ("flagged", True): "correct_flag", ("number", True): "phantom",
                ("flagged", False): "false_alarm", ("number", False): "number_on_possible",
            }.get((label, impossible), "format_failure")
            accurate = (outcome == "number_on_possible"
                        and is_accurate(value, float(q["correct_answer"])))
            rows.append({
                **({"rep": rec["rep"]} if repeats else {}),
                "setting": rec["setting"], "question_id": rec["question_id"], "set_id": q["set_id"],
                "agents": q["agents"], "target_load": q["target_load"], "true_load": q["true_load"],
                "cued": q["cued"], "capacity_stated": q["capacity_stated"], "impossible": impossible,
                "label": label, "value": value, "outcome": outcome, "accurate": accurate,
                "mentions_trouble": mentions_trouble(rec["reply"]),
                "capacity_in_reply": re.search(rf"(?<![\d.]){q['capacity']}(?![\d])", rec["reply"]) is not None,
                "seconds": rec["seconds"],
            })
    out = ROOT / "data" / "processed" / ("labeled" + ("_repeats" if repeats else "") + ("_latexfix" if latex_fix else "") + ".csv")
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"labeled {len(rows)} replies -> {out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--test", action="store_true")
    p.add_argument("--latex-fix", action="store_true", help="EXPLORATORY: also read LaTeX-wrapped ANSWER lines")
    p.add_argument("--repeats", action="store_true", help="score data/raw/repeats/ instead of data/raw/main/")
    a = p.parse_args()
    run_tests() if a.test else label_all(a.latex_fix, a.repeats)
