"""Answer key: the correct long-run average wait in line (minutes) for an M/M/c call center.

Returns "NONE" when load >= 1 (the line grows without end, so no long-run average exists).
Arrivals may carry one decimal; the impossible check uses exact fractions, never floats.

Written by Claude (Oct 12, 2026) at Jayden's request; logged in WORKLOG.md.
"""
from fractions import Fraction
from math import factorial


def is_impossible(arrivals, agents, rate):
    """True when arrivals per hour >= agents x rate. Exact, so load 1.00 is exactly 1.00."""
    return Fraction(str(arrivals)) >= agents * Fraction(str(rate))


def one_agent_wait(arrivals, rate):
    if arrivals >= rate:
        return "NONE"
    load = arrivals / rate
    hours = load / (rate - arrivals)
    return round(hours * 60, 1)


def erlang_c_wait(arrivals, agents, rate):
    """Long-run average wait in line, in minutes, for `agents` agents (Erlang C)."""
    if is_impossible(arrivals, agents, rate):
        return "NONE"
    a = arrivals / rate                       # offered load in "agents' worth" of work
    top = (a ** agents / factorial(agents)) * (agents / (agents - a))
    bottom = sum(a ** k / factorial(k) for k in range(agents)) + top
    p_wait = top / bottom                     # chance a caller has to wait at all
    hours = p_wait / (agents * rate - arrivals)
    return round(hours * 60, 1)


def correct_answer(arrivals, agents, rate):
    return erlang_c_wait(arrivals, agents, rate)


if __name__ == "__main__":
    checks = [
        (one_agent_wait(8, 10), 24.0),
        (one_agent_wait(10, 12), 25.0),
        (one_agent_wait(6, 12), 5.0),
        (one_agent_wait(12, 12), "NONE"),
        (one_agent_wait(13, 12), "NONE"),
        (erlang_c_wait(8, 1, 10), 24.0),      # Erlang C with 1 agent must match the 1-agent formula
        (erlang_c_wait(48, 4, 12), "NONE"),   # exactly load 1.00
        (erlang_c_wait(49, 4, 12), "NONE"),   # load 1.02
        (erlang_c_wait(47.9, 4, 12), None),   # load 0.998: must be a number
    ]
    for got, want in checks:
        ok = (got == want) if want is not None else isinstance(got, float)
        print("ok  " if ok else "FAIL", got, "expected", want if want is not None else "a number")
