"""Question maker: writes every study question (PLAN.md sections 3 and 5) to data/processed/questions.csv.

One "number set" = (agents, rate, arrivals) at one load level. Each set is asked in 4 versions
(cued or not x capacity stated or not) so versions differ only in wording.

Written by Claude (Oct 12, 2026) at Jayden's request; logged in WORKLOG.md.
"""
import csv
import random
from fractions import Fraction
from pathlib import Path

from answer_key import correct_answer, is_impossible

SEED = 20261012
LOADS = [0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 1.00, 1.02, 1.05, 1.10, 1.25, 1.50]
NEAR_LINE = {0.98, 1.00, 1.02, 1.05}
SETS_PER_LOAD = 20
SETS_NEAR_LINE = 40
AGENT_COUNTS = [1, 4]          # add 2 here only if PREREG.md says so
RATES = {1: range(8, 31), 2: range(6, 21), 4: range(5, 16)}   # calls per hour per agent

BODY = (
    "A call center receives calls at random (a Poisson process) at an average rate of {arrivals} "
    "calls per hour. It has {agents} {agent_word}. Each agent handles one call at a time and can "
    "complete an average of {rate} calls per hour; call lengths vary at random (exponentially "
    "distributed).{capacity_sentence} Callers who find all agents busy wait in a single line and are "
    "answered in order. Assume these rates continue indefinitely."
)
CAPACITY_SENTENCE = " Together, the agents can complete {capacity} calls per hour."
Q_UNCUED = ("What is the long-run average time a caller waits in line before an agent answers, "
            "in minutes?")
Q_CUED = ("Is this staffing level workable in the long run? If so, what is the long-run average "
          "time a caller waits in line before an agent answers, in minutes?")
FORMAT = ("End your reply with one line in exactly this format:\n"
          "ANSWER: <minutes, rounded to one decimal place>\n"
          "If there is no valid numeric answer, write:\n"
          "ANSWER: NONE")


def fmt(x):
    """Print 49.0 as 49 and 47.04 as 47.0 (one decimal at most)."""
    x = round(x, 1)
    return str(int(x)) if x == int(x) else f"{x:.1f}"


def make_set(rng, agents, load):
    """Pick a rate so the rounded arrivals stay on the correct side of capacity."""
    while True:
        rate = rng.choice(list(RATES[agents]))
        capacity = agents * rate
        arrivals = round(load * capacity, 1)
        true_load = Fraction(str(arrivals)) / capacity
        side_ok = (true_load < 1) if load < 1 else (true_load == 1) if load == 1 else (true_load > 1)
        if side_ok and abs(float(true_load) - load) <= 0.005:
            return rate, capacity, arrivals, float(true_load)


def build_text(agents, rate, arrivals, cued, capacity_stated):
    capacity = agents * rate
    body = BODY.format(
        arrivals=fmt(arrivals), agents=agents, agent_word="agent" if agents == 1 else "agents",
        rate=rate,
        capacity_sentence=CAPACITY_SENTENCE.format(capacity=capacity) if capacity_stated else "",
    )
    return f"{body}\n\n{Q_CUED if cued else Q_UNCUED}\n\n{FORMAT}"


def main():
    rng = random.Random(SEED)
    rows = []
    for agents in AGENT_COUNTS:
        for load in LOADS:
            n = SETS_NEAR_LINE if load in NEAR_LINE else SETS_PER_LOAD
            for i in range(n):
                rate, capacity, arrivals, true_load = make_set(rng, agents, load)
                set_id = f"a{agents}_L{load:.2f}_s{i:02d}"
                answer = correct_answer(arrivals, agents, rate)
                for cued in (False, True):
                    for capacity_stated in (False, True):
                        rows.append({
                            "question_id": f"{set_id}_{'C' if cued else 'U'}{'K' if capacity_stated else 'N'}",
                            "set_id": set_id, "agents": agents, "rate": rate,
                            "arrivals": fmt(arrivals), "capacity": capacity,
                            "target_load": load, "true_load": round(true_load, 4),
                            "impossible": is_impossible(arrivals, agents, rate),
                            "cued": cued, "capacity_stated": capacity_stated,
                            "correct_answer": answer,
                            "text": build_text(agents, rate, arrivals, cued, capacity_stated),
                        })
    out = Path(__file__).resolve().parent.parent / "data" / "processed" / "questions.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} questions to {out}")


if __name__ == "__main__":
    main()
