"""Analysis: rates by load, agents, cue and capacity, with bootstrap error ranges (PLAN.md section 3).

  python3 src/analyze.py      # reads data/processed/labeled.csv, writes tables and figures/
  python3 src/analyze.py --tag _latexfix
      # EXPLORATORY: reads labeled_latexfix.csv (see parse_replies.py --latex-fix); every output name
      # gets the same tag, so the pre-registered outputs are never overwritten.

Error ranges resample number sets (set_id), keeping each set's 4 versions together.
Written by Claude (Oct 12, 2026) at Jayden's request; logged in WORKLOG.md.
"""
import argparse
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
B = 1000
RNG = np.random.default_rng(20261012)


def bootstrap(df, stat, b=B):
    """95% range for stat(df) by resampling whole number sets within each load level."""
    by_load = [[g.index.to_numpy() for _, g in lg.groupby("set_id")]
               for _, lg in df.groupby("target_load")]
    vals = []
    for _ in range(b):
        idx = np.concatenate([np.concatenate([sets[i] for i in RNG.integers(0, len(sets), len(sets))])
                              for sets in by_load])
        vals.append(stat(df.loc[idx]))
    return np.nanpercentile(vals, [2.5, 97.5])


def phantom_rate(d):
    d = d[d.impossible]
    return (d.outcome == "phantom").mean() if len(d) else np.nan


def false_alarm_rate(d):
    d = d[~d.impossible]
    return (d.outcome == "false_alarm").mean() if len(d) else np.nan


def switch_point(d):
    """Lowest load where the flag rate first reaches 50% (straight-line between load levels)."""
    flag = (d.label == "flagged").groupby(d.target_load).mean().sort_index()
    loads, rates = flag.index.to_numpy(), flag.to_numpy()
    for i in range(1, len(loads)):
        if rates[i - 1] < 0.5 <= rates[i]:
            return loads[i - 1] + (0.5 - rates[i - 1]) / (rates[i] - rates[i - 1]) * (loads[i] - loads[i - 1])
    return loads[0] if len(rates) and rates[0] >= 0.5 else np.nan


def number_rate_chart(d, path, note):
    """Share of replies that print a number, by load, uncued and capacity not stated (added Oct 13, 2026).

    Load levels are evenly spaced so the near-capacity band is readable. Bars: 95% bootstrap range."""
    loads = sorted(d.target_load.unique())
    pos = {l: i for i, l in enumerate(loads)}
    settings = sorted(d.setting.unique())
    colors = {1: "#2a78d6", 4: "#eb6834"}
    shift = {1: -0.09, 4: 0.09}               # small sideways offset so identical lines stay visible
    fig, axes = plt.subplots(1, len(settings), figsize=(6 * len(settings), 4.2), sharey=True, squeeze=False)
    for ax, s in zip(axes[0], settings):
        g = d[(d.setting == s) & (~d.cued) & (~d.capacity_stated)]
        ax.axvspan(pos[1.0] - 0.5, len(loads) - 0.5, color="#000000", alpha=0.06, lw=0)
        ax.text(pos[1.0] - 0.35, 1.03, "no valid answer: any number here is a phantom",
                fontsize=8, color="#52514e", va="bottom")
        for agents, gg in g.groupby("agents"):
            x, y, lo, hi = [], [], [], []
            for load, lg in gg.groupby("target_load"):
                rate = lambda q: (q.label == "number").mean()
                a, b = bootstrap(lg, rate, b=500)
                x.append(pos[load] + shift[agents]), y.append(rate(lg)), lo.append(a), hi.append(b)
            y, lo, hi = np.array(y), np.array(lo), np.array(hi)
            ax.errorbar(x, y, yerr=[y - lo, hi - y], color=colors[agents], lw=2,
                        marker="o" if agents == 1 else "s", ms=5,
                        capsize=0, elinewidth=1, label=f"{agents} agent{'s' if agents > 1 else ''}")
        ax.set_xticks(range(len(loads)), [f"{l:.2f}" for l in loads], fontsize=8)
        ax.set_ylim(-0.03, 1.12)
        ax.set_title(s, fontsize=11)
        ax.set_xlabel("load (calls per hour / total capacity)")
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.grid(axis="y", color="#e5e5e2", lw=0.6)
        ax.set_axisbelow(True)
    axes[0][0].set_ylabel("share of replies that print a number")
    axes[0][-1].legend(fontsize=9, frameon=False, loc="center right")
    fig.text(0.01, 0.005, note, fontsize=7, color="#52514e")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, dpi=150)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tag", default="", help="EXPLORATORY variant, e.g. _latexfix")
    tag = p.parse_args().tag
    d = pd.read_csv(ROOT / "data" / "processed" / f"labeled{tag}.csv")
    for col in ("cued", "capacity_stated", "impossible"):
        d[col] = d[col].astype(str) == "True"
    tables = ROOT / "data" / "processed"
    figs = ROOT / "figures"
    figs.mkdir(exist_ok=True)

    # 1. Outcome shares in every combination
    keys = ["setting", "agents", "cued", "capacity_stated", "target_load"]
    shares = d.groupby(keys).outcome.value_counts(normalize=True).unstack(fill_value=0).reset_index()
    shares.to_csv(tables / f"outcome_shares{tag}.csv", index=False)

    # 2. Headline numbers with error ranges, per setting x agents x cue x capacity
    rows = []
    for k, g in d.groupby(["setting", "agents", "cued", "capacity_stated"]):
        lo, hi = bootstrap(g, phantom_rate)
        flo, fhi = bootstrap(g, false_alarm_rate)
        slo, shi = bootstrap(g, switch_point)
        imp, pos = g[g.impossible], g[~g.impossible]
        rows.append(dict(zip(["setting", "agents", "cued", "capacity_stated"], k),
                         phantom_rate=phantom_rate(g), phantom_lo=lo, phantom_hi=hi,
                         false_alarm_rate=false_alarm_rate(g), false_alarm_lo=flo, false_alarm_hi=fhi,
                         switch_point=switch_point(g), switch_lo=slo, switch_hi=shi,
                         accuracy_on_possible=(pos.outcome == "number_on_possible").pipe(
                             lambda m: pos.accurate[m].mean() if m.any() else np.nan),
                         format_failure_rate=(g.outcome == "format_failure").mean(),
                         noticed_but_answered=(imp.mentions_trouble & (imp.outcome == "phantom")).mean(),
                         phantom_with_capacity_in_reply=imp[imp.outcome == "phantom"].capacity_in_reply.mean(),
                         mean_seconds=g.seconds.mean()))
    summary = pd.DataFrame(rows)
    summary.to_csv(tables / f"summary{tag}.csv", index=False)
    print(summary.round(3).to_string(index=False))

    # 3. Multi-server trap: false alarms, 4 agents minus 1 agent, matched loads, per setting x cue x capacity
    trap = []
    for k, g in d[~d.impossible].groupby(["setting", "cued", "capacity_stated"]):
        fa = g.groupby("agents").apply(lambda x: (x.outcome == "false_alarm").mean())
        trap.append(dict(zip(["setting", "cued", "capacity_stated"], k),
                         false_alarm_1=fa.get(1, np.nan), false_alarm_4=fa.get(4, np.nan),
                         difference=fa.get(4, np.nan) - fa.get(1, np.nan)))
    pd.DataFrame(trap).to_csv(tables / f"multi_server_trap{tag}.csv", index=False)

    # 4. Chart: flag rate vs load, one panel per setting, lines for agents x cue (capacity not stated)
    settings = sorted(d.setting.unique())
    fig, axes = plt.subplots(1, len(settings), figsize=(5 * len(settings), 4), sharey=True, squeeze=False)
    for ax, s in zip(axes[0], settings):
        g = d[(d.setting == s) & (~d.capacity_stated)]
        for (agents, cued), gg in g.groupby(["agents", "cued"]):
            r = (gg.label == "flagged").groupby(gg.target_load).mean()
            ax.plot(r.index, r.values, marker="o", ms=3,
                    label=f"{agents} agent{'s' if agents > 1 else ''}, {'cued' if cued else 'uncued'}")
        ax.axvline(1.0, color="grey", lw=0.8, ls="--")
        ax.set_title(s)
        ax.set_xlabel("load (calls / capacity)")
    axes[0][0].set_ylabel("share of replies flagged (NONE)")
    axes[0][-1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(figs / f"flag_rate_vs_load{tag}.png", dpi=150)

    # 5. Chart: share of replies that print a number, by load (uncued, capacity not stated)
    note = ("Uncued, capacity not stated. 20 number sets per point (40 at 0.98 to 1.05); bars = 95% bootstrap "
            "range. Below 1.00 a number is expected; format failures count as not a number.")
    if tag:
        note = f"EXPLORATORY scoring ({tag.strip('_')}), not pre-registered. " + note
    number_rate_chart(d, figs / f"number_rate_vs_load{tag}.png", note)
    print(f"tables in {tables}, charts in {figs}")


if __name__ == "__main__":
    main()
