"""Blind hand-check for the qwen3:8b thinking-off main run (PREREG section 4, PLAN section 6).

  python3 src/handcheck.py make       # draws the 150 replies, writes sheet.html, labels.csv, key_DO_NOT_OPEN.csv
  python3 src/handcheck.py compare    # AFTER Jayden has labeled all 150: percent agreement + disagreements

Random seed: 20261013 (fixed, so `make` always draws the same 150 replies in the same order).

Draw, in PREREG's order, without replacement (from data/raw/main/qwen3-8b-nothink.jsonl joined to
data/processed/questions.csv on question_id):
  A  50 replies at true load >= 1.00      -> impossible == "True" in questions.csv (exact flag, no float test)
  B  50 replies at load 0.95 to 1.05      -> target_load 0.95, 0.98, 1.00, 1.02, 1.05, not already drawn
                                             (target_load is the design's load level; true_load wobbles
                                             around it because rates are whole numbers, e.g. 0.9462 for 0.95)
  C  50 replies that settle (load < 1.00) -> impossible == "False", not already drawn
The 150 are then shuffled into one order and numbered 1 to 150, so the number says nothing about the group.

The sheet shows only the question text and the reply. The key (group, true load, the program's label)
stays in key_DO_NOT_OPEN.csv until Jayden has finished labeling.

Written by Claude (Oct 13, 2026) at Jayden's request; logged in WORKLOG.md.
"""
import argparse
import csv
import html
import json
import random
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_replies import read_answer  # noqa: E402  (the scorer being checked)

ROOT = Path(__file__).resolve().parent.parent
SEED = 20261013
REPLIES = ROOT / "data" / "raw" / "main" / "qwen3-8b-nothink.jsonl"
QUESTIONS = ROOT / "data" / "processed" / "questions.csv"
OUT_DIR = ROOT / "data" / "processed" / "handcheck"

GROUP_A = "A_load_1.00_and_up"
GROUP_B = "B_near_the_line_0.95_to_1.05"
GROUP_C = "C_settles_below_1.00"
GROUPS = [GROUP_A, GROUP_B, GROUP_C]
PER_GROUP = 50
BAND = (Decimal("0.95"), Decimal("1.05"))

HAND_LABELS = ["NONE", "NUMBER", "UNCLEAR"]
YES_NO = ["yes", "no"]
# How the program's label lines up with Jayden's three choices.
PROGRAM_TO_HAND = {"flagged": "NONE", "number": "NUMBER", "format_failure": "UNCLEAR"}

KEY_NOTE = ("# DO NOT OPEN THIS FILE until you have labeled all 150 items. It holds the program's labels "
            "and the load of each question, which would spoil the blind check. (seed %d)" % SEED)
KEY_COLUMNS = ["item", "question_id", "group", "true_load", "agents", "impossible", "program_label",
               "target_load"]
LABEL_COLUMNS = ["item", "my_label", "manager_knows", "notes"]


def load_joined():
    with QUESTIONS.open(newline="", encoding="utf-8") as f:
        qs = {q["question_id"]: q for q in csv.DictReader(f)}
    joined = {}
    with REPLIES.open(encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            qid = rec["question_id"]
            if qid in joined:
                sys.exit(f"duplicate question_id in the replies file: {qid}")
            joined[qid] = {"q": qs[qid], "reply": rec["reply"]}
    return joined


def draw(joined):
    """Return the 150 drawn question_ids as [(question_id, group), ...] in the shuffled order."""
    rng = random.Random(SEED)
    ids = sorted(joined)
    taken = set()
    drawn = []

    def take(group, pool):
        pool = [i for i in pool if i not in taken]
        if len(pool) < PER_GROUP:
            sys.exit(f"only {len(pool)} replies available for group {group}")
        pick = rng.sample(pool, PER_GROUP)
        taken.update(pick)
        drawn.extend((i, group) for i in pick)

    take(GROUP_A, [i for i in ids if joined[i]["q"]["impossible"] == "True"])
    take(GROUP_B, [i for i in ids if BAND[0] <= Decimal(joined[i]["q"]["target_load"]) <= BAND[1]])
    take(GROUP_C, [i for i in ids if joined[i]["q"]["impossible"] == "False"])
    rng.shuffle(drawn)
    return drawn


INSTRUCTIONS = """\
<h1>Hand-check sheet</h1>
<div class="box">
<p><b>What this is.</b> There are 150 items. Each one shows a question that was given to an AI model, and the
model's reply. You are checking, by eye, what each reply actually says.</p>
<p><b>What to do.</b> For each item, find the row with the same item number in <code>labels.csv</code>
(same folder as this page) and fill in:</p>
<ol>
<li><b>my_label</b> &mdash; read the reply's <i>final answer</i> and type one of:
  <ul>
  <li><b>NONE</b> if the final answer says there is no valid long-run wait;</li>
  <li><b>NUMBER</b> if the final answer is a wait in minutes;</li>
  <li><b>UNCLEAR</b> if there is no clear final answer.</li>
  </ul></li>
<li><b>manager_knows</b> &mdash; type <b>yes</b> or <b>no</b>: <i>would a manager reading this reply know
  this staffing plan does not work?</i></li>
<li><b>notes</b> &mdash; optional. Anything odd you noticed.</li>
</ol>
<p><b>Please don't</b> work out the load or the right answer yourself. Judge what the reply
<i>communicates</i>, not whether the math is right. Don't change the item numbers in <code>labels.csv</code>,
and don't open <code>key_DO_NOT_OPEN.csv</code> until all 150 rows are filled in.</p>
</div>
"""

STYLE = """\
body { font-family: Georgia, "Times New Roman", serif; max-width: 52rem; margin: 2rem auto; padding: 0 1rem;
       line-height: 1.45; color: #1a1a1a; background: #fff; }
h1 { margin-bottom: 0.5rem; }
h2 { margin: 2.5rem 0 0.4rem; padding-top: 1rem; border-top: 3px solid #333; }
h3 { margin: 1rem 0 0.25rem; font-size: 0.95rem; color: #444; text-transform: uppercase; letter-spacing: 0.04em; }
.box { background: #fff8dc; border: 2px solid #c9a227; border-radius: 6px; padding: 0.5rem 1.25rem; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; font-family: Menlo, Consolas, monospace; font-size: 0.85rem;
      padding: 0.75rem; margin: 0; border-radius: 4px; }
pre.q { background: #f1f1f1; border: 1px solid #ccc; }
pre.r { background: #fff; border: 2px solid #4a6fa5; }
@media print { h2 { page-break-before: always; } }
"""


def build_sheet(joined, drawn):
    parts = ["<!DOCTYPE html>", '<html lang="en">', "<head>", '<meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width, initial-scale=1">',
             "<title>Hand-check sheet</title>", f"<style>\n{STYLE}</style>", "</head>", "<body>",
             INSTRUCTIONS]
    for n, (qid, _group) in enumerate(drawn, start=1):
        rec = joined[qid]
        parts.append(
            f'<section id="item-{n}">\n<h2>Item {n}</h2>\n'
            f'<h3>Question the model saw</h3>\n<pre class="q">{html.escape(rec["q"]["text"], quote=False)}</pre>\n'
            f'<h3>Model reply</h3>\n<pre class="r">{html.escape(rec["reply"], quote=False)}</pre>\n</section>')
    parts += ["</body>", "</html>", ""]
    return "\n".join(parts)


def write_csv(path, header_comment, columns, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        if header_comment:
            f.write(header_comment + "\n")
        w = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def labels_already_filled(path):
    if not path.exists():
        return False
    with path.open(newline="", encoding="utf-8-sig") as f:
        return any((row.get(c) or "").strip() for row in csv.DictReader(f)
                   for c in ("my_label", "manager_knows", "notes"))


def make(out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    labels_path = out_dir / "labels.csv"
    if labels_already_filled(labels_path):
        sys.exit(f"{labels_path} already has labels in it. `make` would wipe them, so it stops. "
                 "Move or rename that file first if you really want a fresh sheet.")
    joined = load_joined()
    drawn = draw(joined)

    (out_dir / "sheet.html").write_text(build_sheet(joined, drawn), encoding="utf-8")
    write_csv(labels_path, None, LABEL_COLUMNS,
              [{"item": n, "my_label": "", "manager_knows": "", "notes": ""} for n in range(1, len(drawn) + 1)])
    key_rows = []
    for n, (qid, group) in enumerate(drawn, start=1):
        q = joined[qid]["q"]
        label, _value = read_answer(joined[qid]["reply"])
        key_rows.append({"item": n, "question_id": qid, "group": group, "true_load": q["true_load"],
                         "agents": q["agents"], "impossible": q["impossible"], "program_label": label,
                         "target_load": q["target_load"]})
    write_csv(out_dir / "key_DO_NOT_OPEN.csv", KEY_NOTE, KEY_COLUMNS, key_rows)
    print(f"wrote {len(drawn)} items to {out_dir} (sheet.html, labels.csv, key_DO_NOT_OPEN.csv; seed {SEED})")


def read_key(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        lines = [ln for ln in f if not ln.startswith("#")]
    return list(csv.DictReader(lines))


def compare(labels_path, key_path):
    key = read_key(key_path)
    with labels_path.open(newline="", encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if any((v or "").strip() for v in r.values())]

    problems = []
    mine = {}
    for r in rows:
        item = (r.get("item") or "").strip()
        label = (r.get("my_label") or "").strip().upper()
        mgr = (r.get("manager_knows") or "").strip().lower()
        if not item:
            problems.append("a row has no item number")
            continue
        if item in mine:
            problems.append(f"item {item} appears twice")
        if not label:
            problems.append(f"item {item}: my_label is blank")
        elif label not in HAND_LABELS:
            problems.append(f"item {item}: my_label '{r.get('my_label')}' is not NONE, NUMBER or UNCLEAR")
        if not mgr:
            problems.append(f"item {item}: manager_knows is blank")
        elif mgr not in YES_NO:
            problems.append(f"item {item}: manager_knows '{r.get('manager_knows')}' is not yes or no")
        mine[item] = label
    key_items = {k["item"] for k in key}
    for item in sorted(key_items - set(mine), key=int):
        problems.append(f"item {item}: no row in the labels file")
    for item in sorted(set(mine) - key_items):
        problems.append(f"item {item}: not an item in the key")
    if problems:
        print("Not comparing yet. Fix these first:")
        for p in problems[:40]:
            print("  -", p)
        if len(problems) > 40:
            print(f"  ... and {len(problems) - 40} more")
        sys.exit(1)

    totals = {g: [0, 0] for g in GROUPS}
    disagreements = []
    for k in key:
        theirs, prog = mine[k["item"]], PROGRAM_TO_HAND[k["program_label"]]
        totals[k["group"]][1] += 1
        if theirs == prog:
            totals[k["group"]][0] += 1
        else:
            disagreements.append((int(k["item"]), k["question_id"], theirs, k["program_label"]))

    agree = sum(a for a, _ in totals.values())
    n = sum(t for _, t in totals.values())
    print(f"Agreement overall: {agree}/{n} = {100 * agree / n:.1f}%")
    for g in GROUPS:
        a, t = totals[g]
        print(f"  {g}: {a}/{t} = {100 * a / t:.1f}%")
    print(f"\nDisagreements ({len(disagreements)}):")
    print(f"  {'item':>4}  {'question_id':<22} {'Jayden':<8} program")
    for item, qid, theirs, prog in sorted(disagreements):
        print(f"  {item:>4}  {qid:<22} {theirs:<8} {prog} (= {PROGRAM_TO_HAND[prog]})")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make", help="draw the 150 replies and write the sheet, labels file and key")
    m.add_argument("--out", type=Path, default=OUT_DIR, help="output folder (default: data/processed/handcheck)")
    c = sub.add_parser("compare", help="compare Jayden's finished labels with the program's (run only when done)")
    c.add_argument("--labels", type=Path, default=OUT_DIR / "labels.csv")
    c.add_argument("--key", type=Path, default=OUT_DIR / "key_DO_NOT_OPEN.csv")
    args = p.parse_args()
    make(args.out) if args.cmd == "make" else compare(args.labels, args.key)
