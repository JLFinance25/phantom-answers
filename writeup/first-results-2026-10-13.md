# First results: qwen3:8b (thinking off) and gpt-oss:20b

**Drafted with Claude (AI) on Oct 13, 2026; not yet reviewed or approved by Jayden Ling.**
Status: first scoring of two finished main runs. The 150-reply hand-check (PREREG section 4) is not done
yet, so every number below could still move if the hand-check finds a scoring bug.

## Where the numbers come from

- Raw replies: `data/raw/main/qwen3-8b-nothink.jsonl` (commit 78fcdcf, PC, model ID 500a1f067a9f) and
  `data/raw/main/gpt-oss-20b.jsonl` (commit 00e5076, Mac, model ID 17052f91a42e). 2,560 replies each.
- Scored Oct 13, 2026 with `src/parse_replies.py` as committed with PREREG.md (20/20 tests pass) ->
  `data/processed/labeled.csv`; analysis `src/analyze.py` -> `data/processed/summary.csv`,
  `outcome_shares.csv`, `multi_server_trap.csv`, `figures/flag_rate_vs_load.png`,
  `figures/number_rate_vs_load.png`; cost of misses `src/simulate.py` -> `data/processed/miss_costs.csv`.
- **Two scorings.** "Pre-registered" is the scorer exactly as committed. "LaTeX fix" (EXPLORATORY, not
  pre-registered) also reads an answer line wrapped in LaTeX, like `\boxed{ANSWER: 0.2}`
  (`parse_replies.py --latex-fix`, files tagged `_latexfix`). Whether that counts as a program-bug fix
  under PREREG section 4 is Jayden's decision. It changes 60 qwen replies, all of them format failures
  before; gpt-oss has none. Where the two scorings differ, both are shown.
- Answer key re-checked Oct 13: every one of the 280 number sets that settle was solved a second way
  (the waiting line's state probabilities summed directly, no Erlang C formula). All 280 match to within
  0.05 minutes (one sits on a rounding edge, 33.75).

## Headline

Both models almost never print a wait for a line that can never settle. That is the opposite of the
prediction for qwen3:8b.

| Model | Impossible questions | Phantom answers (pre-registered) | Phantom answers (LaTeX fix) |
|---|---|---|---|
| gpt-oss:20b | 1,440 | 0 | 0 |
| qwen3:8b, thinking off | 1,440 | 18 (1.3%) | 19 (1.3%) |

## The prediction (PREREG section 2) against the result

qwen3:8b thinking off, 1 agent, uncued, capacity not stated. Ranges are 95% bootstrap ranges (number
sets resampled, 1,000 times). Both scorings give the same numbers here.

| Load | Predicted phantom rate | Result | Verdict |
|---|---|---|---|
| 1.02 | more than 60% | 6 of 40 = 15% (5% to 28%) | **wrong** |
| 1.00 | 35% to 65% | 0 of 40 = 0% | **wrong** |
| 1.50 | under 20% | 0 of 20 = 0% | right |

- Order "highest at 1.02, lower at 1.00, lowest at 1.50": 1.02 is highest, but 1.00 and 1.50 tie at 0.
- The "most surprising" result (20% or more at 1.50) did not happen.
- Claude's own guess in PLAN.md (1.00 would do better than half) was right, but Claude also expected
  more phantoms near the line than this.

## What the phantom answers look like

All 18 are in **uncued** versions; adding the cue ("Is this staffing level workable...?") removed every one.

- **12 at load 1.02, 1 agent** (7 number sets; 5 of them wrong in both uncued versions). Each is an arithmetic
  slip: the model divides arrivals by capacity and gets a number under 1, for example "9.2 / 9 ≈ 0.9111"
  (the true value is 1.022), then uses the textbook formula with confidence. These are "could not
  divide", not "did not know the rule". (The LaTeX fix adds a 13th of the same kind.)
- **6 at load exactly 1.00, 4 agents, capacity stated.** The model writes that the load is exactly 1 and
  that the usual formula "is not valid", then invents an "approximation" and prints about 1.4 minutes.
  These are the "noticed but answered anyway" group (PREREG section 5, measure 6).
- **Cost (PREREG measure 9, 8-hour shift simulated 1,000 times):** at load 1.00 with 4 agents, the
  printed 1.4 to 1.5 minutes compares with a real shift average of about 17 minutes (11 to 12 times
  longer), with about 17 to 19 callers still waiting at closing. The 1.02 one-agent phantoms printed
  waits *longer* than an 8-hour shift's real average (37.5 to 598.4 minutes printed vs 24.6 to 38.4 real), with
  8 to 17 callers still waiting at close. So a phantom answer can mislead in either direction.
- Measure 7 ("phantom replies that already contain the correct capacity") is 100%, but it is not
  informative for 1 agent: capacity equals the one agent's rate, which is copied from the question.

## Questions that settle

| Model | Agents | False alarms (NONE on a line that settles) | Accurate within 2% or 0.1 min | Format failures |
|---|---|---|---|---|
| gpt-oss:20b | 1 | 0 of 560 | 560 of 560 (100%) | 0 |
| gpt-oss:20b | 4 | 2 of 560 | 126 of 560 (22.5%) | 0 |
| qwen3:8b | 1 | 0 of 560 | 549 of 560 (98.0%) | 1 (LaTeX fix: 0) |
| qwen3:8b | 4 | 0 of 560 | 12 of 560 (2.1%) | 96 (LaTeX fix: 37) |

- The multi-server trap (PREREG measure 4) barely shows: 4-agent false alarms are 2 of 2,240 replies
  across both models. Models do not mistake a 4-agent team that can keep up for an overloaded one.
- **The big weakness is somewhere else:** with 4 agents, both models know the line settles but cannot
  compute the wait (Erlang C). qwen3:8b gets 2% right and loops until it hits the 6,000-token cap on
  38 replies (37 of them with no answer line), mostly at loads 0.50 (15) and 0.98 (12); gpt-oss:20b gets
  22.5% right.
- The 58 `\boxed{}` replies the LaTeX fix rescues are all 4-agent questions that settle, and none of them
  is accurate, so the fix changes the format-failure rate but not accuracy.

## Shape of the curve

- Switch point (flag rate first reaches 50%): 0.99 in every version for both models. That is just the
  midpoint between the 0.98 and 1.00 load levels. The models jump from never flagging at 0.98 to always
  flagging at 1.00, so the real switch point is "somewhere between 0.98 and 1.00" and the bootstrap range
  has no width.
- This is the "dull step" PLAN.md section 8 warned about. The findings are in where it breaks: the
  division slips at 1.02, the made-up approximations at exactly 1.00, the cue removing all phantoms, and
  4-agent accuracy.

## Repeat sets (temperature 0.7; reported separately, PREREG section 3)

- gpt-oss:20b: 300 replies (100 questions x 3). Every repeat gave the same label as the temperature-0
  reply. 0 phantoms, 0 false alarms, 0 format failures.
- qwen3:8b: 300 replies. All 3 repeats agree on 91% of questions and match the temperature-0 label 93% of
  the time. 2 phantoms, 2 false alarms, 6 format failures (4 `\boxed{}`, 2 `\text{ANSWER: NONE}`).

## What this does not show yet

- Not hand-checked yet (150 replies, Jayden).
- Two models only. qwen3:8b thinking on has not run.
- Offering `ANSWER: NONE` in every question is itself a hint (PREREG section 7); with that hint and
  textbook wording, these models do well on the stability rule. That may not hold for plain manager
  wording.
