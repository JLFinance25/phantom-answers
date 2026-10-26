"""Cost of a miss: play out an 8-hour shift caller by caller (PLAN.md decision D15).

  python3 src/simulate.py --check     # validation: long runs at loads that settle must match the formula
  python3 src/simulate.py             # cost for every phantom answer in data/processed/labeled.csv

Each shift starts with an empty line. Every caller who arrives during the shift is served, even after
closing time, so their full wait counts. "Still waiting" = callers who arrived but were not yet answered
when the 8 hours end.

Written by Claude (Oct 12, 2026) at Jayden's request; logged in WORKLOG.md.
"""
import argparse
import csv
import heapq
import random
from pathlib import Path
from statistics import mean

from answer_key import erlang_c_wait

ROOT = Path(__file__).resolve().parent.parent


def simulate_shift(arrivals, agents, rate, hours, rng):
    """Return (average wait in minutes, callers still waiting at the end of the shift)."""
    free_at = [0.0] * agents                 # when each agent next becomes free (hours)
    t, waits, still_waiting = 0.0, [], 0
    while True:
        t += rng.expovariate(arrivals)       # random gap to the next caller
        if t > hours:
            break
        agent_free = heapq.heappop(free_at)  # the agent who frees up soonest
        start = max(t, agent_free)
        waits.append(start - t)
        if start > hours:
            still_waiting += 1
        heapq.heappush(free_at, start + rng.expovariate(rate))
    return (mean(waits) * 60 if waits else 0.0), still_waiting


def shift_cost(arrivals, agents, rate, reps=1000, hours=8, seed=1):
    rng = random.Random(seed)
    results = [simulate_shift(arrivals, agents, rate, hours, rng) for _ in range(reps)]
    return mean(r[0] for r in results), mean(r[1] for r in results)


def check():
    rng = random.Random(2)
    for arrivals, agents, rate in [(8, 1, 10), (10, 1, 12), (40, 4, 12), (43.2, 4, 12)]:
        sim = mean(simulate_shift(arrivals, agents, rate, 20000, rng)[0] for _ in range(3))
        print(f"{arrivals}/hr, {agents} agents x {rate}: formula {erlang_c_wait(arrivals, agents, rate)} min, "
              f"simulation {sim:.1f} min")


def costs():
    with (ROOT / "data" / "processed" / "labeled.csv").open() as f:
        rows = [r for r in csv.DictReader(f) if r["outcome"] == "phantom"]
    with (ROOT / "data" / "processed" / "questions.csv").open() as f:
        qs = {q["question_id"]: q for q in csv.DictReader(f)}
    cache, out_rows = {}, []
    for r in rows:
        q = qs[r["question_id"]]
        key = (float(q["arrivals"]), int(q["agents"]), int(q["rate"]))
        if key not in cache:
            cache[key] = shift_cost(*key)
        sim_wait, backlog = cache[key]
        printed = float(r["value"])
        out_rows.append({**r, "printed_wait": printed, "shift_avg_wait": round(sim_wait, 1),
                         "times_longer": round(sim_wait / printed, 1) if printed > 0 else "",
                         "still_waiting_at_close": round(backlog, 1)})
    out = ROOT / "data" / "processed" / "miss_costs.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0]))
        w.writeheader()
        w.writerows(out_rows)
    print(f"{len(out_rows)} phantom answers priced -> {out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    check() if p.parse_args().check else costs()
