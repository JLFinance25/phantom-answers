"""Checks and side-by-side tables for the qwen3:8b thinking-on run (added Oct 15, 2026; changes no scoring rule).

  python3 src/think_report.py            # after parse_replies.py, parse_replies.py --repeats and analyze.py

Reads data/raw/main/<setting>.jsonl, data/raw/repeats/<setting>.jsonl, data/processed/labeled.csv and
labeled_repeats.csv. Prints everything and writes:
  data/processed/think_vs_others_1agent.csv   1-agent questions only, one row per setting
  data/processed/repeats_agreement.csv         one row per setting: do the 3 repeats agree, do they match temperature 0

It never edits raw data or the scored files. Exit code 1 if a run-completeness check fails.
Written by Claude (Oct 15, 2026) at Jayden's request; logged in WORKLOG.md.
"""
import argparse
import csv
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_replies import ANSWER_LINE, read_answer  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
EXPECT = {"think": True, "num_predict": 12000, "num_ctx": 16384, "digest": "500a1f067a9f"}  # PREREG section 8, Oct 13


def read_jsonl(path):
    with path.open() as f:
        return [json.loads(line) for line in f]


def reason(rec):
    """Why a reply has no usable answer line (own groups; all count as format failures under PREREG section 4)."""
    text = rec["reply"] or ""
    cap = rec.get("done_reason") == "length"
    if read_answer(text)[0] != "format_failure":
        return "scored"
    if cap:
        return "cap hit, no ANSWER line"
    if re.search(r"answer\s*[:：]", text, re.IGNORECASE):
        return "ANSWER: present but unreadable (e.g. LaTeX-wrapped)"
    if "\\boxed" in text:
        return "\\boxed{x} only, no ANSWER line"
    return "no ANSWER line (other)"


def completeness(setting, ok):
    q = list(csv.DictReader((PROC / "questions.csv").open()))
    one = [x for x in q if x["agents"] == "1"]
    main = read_jsonl(ROOT / "data" / "raw" / "main" / f"{setting}.jsonl")
    ids = Counter(r["question_id"] for r in main)
    print(f"== {setting}: main file ==")
    print(f"records {len(main)}, distinct questions {len(ids)}, expected {len(one)} (all 1-agent questions)")
    dup = [i for i, n in ids.items() if n > 1]
    missing = {x["question_id"] for x in one} - set(ids)
    extra = set(ids) - {x["question_id"] for x in one}
    for name, bad in (("duplicates", dup), ("missing", missing), ("not 1-agent / unknown", extra)):
        print(f"{name}: {len(bad)}")
        ok.append(not bad)
    settings = {(r["think"], r["num_predict"], r["num_ctx"], r["model_digest"][:12], r["temperature"], r["rep"])
                for r in main}
    print("settings seen (think, num_predict, num_ctx, model ID, temperature, rep):", settings)
    ok.append(settings == {(EXPECT["think"], EXPECT["num_predict"], EXPECT["num_ctx"], EXPECT["digest"], 0.0, 0)})
    print("done_reason:", dict(Counter(r["done_reason"] for r in main)))
    print("reply lengths: max eval_tokens", max(r["eval_tokens"] or 0 for r in main),
          "| mean seconds", round(sum(r["seconds"] for r in main) / len(main), 1))
    print("why no usable answer line (all format failures):",
          dict(Counter(reason(r) for r in main if reason(r) != "scored")))
    print(f"cap hits: {sum(r['done_reason'] == 'length' for r in main)} "
          f"(of those with a readable ANSWER line, scored normally: "
          f"{sum(r['done_reason'] == 'length' and reason(r) == 'scored' for r in main)})")

    rep_path = ROOT / "data" / "raw" / "repeats" / f"{setting}.jsonl"
    if rep_path.exists():
        rep = read_jsonl(rep_path)
        picked = {x["question_id"] for x in random.Random(7).sample(one, 100)}   # the draw run_models.py --agents 1 makes
        pairs = Counter((r["question_id"], r["rep"]) for r in rep)
        print(f"\n== {setting}: repeats file ==")
        print(f"records {len(rep)}, distinct questions {len(set(r['question_id'] for r in rep))}, "
              f"reps {sorted(set(r['rep'] for r in rep))}, duplicates {sum(n > 1 for n in pairs.values())}")
        print("same 100 questions as run_models.py would draw:", {r["question_id"] for r in rep} == picked,
              "| temperatures:", set(r["temperature"] for r in rep))
        ok.append(len(rep) == 300 and {r["question_id"] for r in rep} == picked and len(pairs) == 300)
        print("done_reason:", dict(Counter(r["done_reason"] for r in rep)))
    else:
        print(f"\n(no repeats file yet: {rep_path})")


def one_agent_table():
    d = pd.read_csv(PROC / "labeled.csv")
    d = d[d.agents == 1]
    rows = []
    for s, g in d.groupby("setting"):
        imp, pos = g[g.impossible], g[~g.impossible]
        rows.append({"setting": s, "n_replies": len(g), "n_impossible": len(imp),
                     "phantom": (imp.outcome == "phantom").sum(), "correct_flag": (imp.outcome == "correct_flag").sum(),
                     "impossible_format_failure": (imp.outcome == "format_failure").sum(),
                     "n_settles": len(pos), "false_alarm": (pos.outcome == "false_alarm").sum(),
                     "accurate": pos.accurate.sum(), "inaccurate_number": ((pos.outcome == "number_on_possible") & ~pos.accurate).sum(),
                     "settles_format_failure": (pos.outcome == "format_failure").sum(),
                     "format_failure_rate": round((g.outcome == "format_failure").mean(), 4)})
    t = pd.DataFrame(rows)
    t.to_csv(PROC / "think_vs_others_1agent.csv", index=False)
    print("\n== 1-agent questions only, all settings (same 1,280 questions in each) ==")
    print(t.to_string(index=False))
    if {"qwen3-8b-nothink", "qwen3-8b-think"} <= set(d.setting):
        a, b = (d[d.setting == s].set_index("question_id").label for s in ("qwen3-8b-nothink", "qwen3-8b-think"))
        print("\nPaired labels, qwen3-8b-nothink (rows) vs qwen3-8b-think (columns), same question:")
        print(pd.crosstab(a.rename("nothink"), b.reindex(a.index).rename("think")).to_string())


def repeats_table():
    path = PROC / "labeled_repeats.csv"
    if not path.exists():
        print("\n(labeled_repeats.csv not found: run parse_replies.py --repeats first)")
        return
    r, m = pd.read_csv(path), pd.read_csv(PROC / "labeled.csv")
    base = m.set_index(["setting", "question_id"]).label
    r["temp0_label"] = [base.get((s, q)) for s, q in zip(r.setting, r.question_id)]
    rows = []
    for s, g in r.groupby("setting"):
        per_q = g.groupby("question_id").label.nunique()
        rows.append({"setting": s, "replies": len(g), "questions": g.question_id.nunique(),
                     "questions_all_reps_agree": int((per_q == 1).sum()),
                     "match_temp0_label": int((g.label == g.temp0_label).sum()),
                     "phantom": int((g.outcome == "phantom").sum()), "false_alarm": int((g.outcome == "false_alarm").sum()),
                     "format_failure": int((g.outcome == "format_failure").sum())})
    t = pd.DataFrame(rows)
    t.to_csv(PROC / "repeats_agreement.csv", index=False)
    print("\n== repeat sets (temperature 0.7) ==")
    print(t.to_string(index=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--setting", default="qwen3-8b-think")
    a = p.parse_args()
    checks = []
    completeness(a.setting, checks)
    one_agent_table()
    repeats_table()
    print("\nCOMPLETENESS CHECKS:", "all passed" if all(checks) else "FAILED (see lines above)")
    sys.exit(0 if all(checks) else 1)
