# Pre-registration: Phantom Answers Near Capacity

**DRAFT written by Claude on Oct 12, 2026 at Jayden's request.** Jayden reads it, changes anything he
disagrees with, fills the two `[FILL]` lines after the timing pilot, and commits it. The commit date is
the pre-registration date. No study run (`data/raw/main/`) happens before that commit.

## 1. Question

When a long-run waiting-line question has no valid answer because load is at or above capacity, how often
do small local language models still print a number? How does that rate change with load (0.5 to 1.5),
the number of agents (1 vs 4), a cue asking whether the setup is workable, and stating total capacity
outright, with wording and answer format held fixed?

## 2. Predictions (written before any study run)

For qwen3:8b with thinking off, 1 agent, uncued, capacity not stated (phantom = a number printed on an
impossible question):

| Load | Prediction |
|---|---|
| 1.02 | phantom answers most of the time (more than 60%) |
| 1.00 | about half (35% to 65%) |
| 1.50 | rarely (under 20%) |

- Order: phantom rate highest at 1.02, lower at 1.00, lowest at 1.50.
- Most surprising possible result: phantom answers common (20% or more) even at 1.50, which would mean
  the model is not comparing calls to capacity at all.
- Expected overall shape: flag rate jumps sharply near 1.00 for textbook-worded questions; the
  interesting results are where that jump breaks (0.95 to 1.10, 4 agents, cue, capacity stated).

## 3. Materials

- Questions: `src/make_questions.py`, seed 20261012, template in PLAN.md section 5, saved to
  `data/processed/questions.csv` (2,560 questions).
- Loads: 0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 1.00, 1.02, 1.05, 1.10, 1.25, 1.50.
- Agents: 1 and 4. `[FILL after pilot: add 2 agents? yes/no]`
- Versions: uncued or cued x capacity not stated or stated; all 4 versions of a number set share numbers.
- Number sets: 20 per (agents, load); 40 at 0.98, 1.00, 1.02, 1.05.
- Answer key: `src/answer_key.py` (one-agent formula and Erlang C; NONE when load >= 1, exact check).
- Model settings (Ollama, temperature 0, one answer each): qwen3:8b thinking off, qwen3:8b thinking on,
  gpt-oss:20b (reasoning "low"). Each setting stays on one machine.
  `[FILL after pilot: machine per setting, Ollama version, model digests, seconds per answer]`
- Repeat set: 100 random questions x 3 at temperature 0.7 per setting, reported separately.
- Pilot: 10 questions per setting for timing only (`data/raw/pilot/`); not study data.

## 4. Scoring (fixed now; `src/parse_replies.py`)

- Read only the last `ANSWER:` line of the final reply; ignore thinking text.
- NONE, infinite, infinity, ∞, unbounded, undefined -> **flagged**. Any number -> **number**.
  Missing or unreadable -> **format failure** (own group, never dropped).
- Impossible question (load >= 1.00, including exactly 1.00): flagged = correct; number = **phantom**.
- Question that settles: flagged = **false alarm**; number = accurate if within 2% of the key or within
  0.1 minute (the rounding the template asks for).
- Looser measure, "mentions trouble": the reply contains any phrase in `TROUBLE_PHRASES` in
  `src/parse_replies.py` as committed with this file.
- "Capacity in reply": the reply contains the correct total capacity number.
- Hand-check: Jayden labels a random 150 replies (50 at load >= 1.00, 50 at 0.95 to 1.05, 50 that
  settle) before seeing the program's label; percent agreement is reported. Program bugs found this way
  may be fixed; the scoring rules above may not change.

## 5. Measures and analysis (`src/analyze.py`)

Per model setting x agents x cue x capacity stated:
1. Phantom rate on impossible questions, and by load.
2. False-alarm rate on questions that settle, and by load.
3. Switch point: the load where the flagged share first reaches 50% (straight line between levels).
4. Multi-server trap: false-alarm rate with 4 agents minus 1 agent at matched loads.
5. Cue effect: cued minus uncued phantom rate. Capacity effect: stated minus not stated.
6. "Noticed but answered anyway": impossible questions with a phantom answer that mention trouble.
7. Among phantom answers without capacity stated, the share that already contain the correct capacity
   (a miss of attention, not arithmetic).
8. Accuracy on questions that settle; format failure rate.
9. Cost of each phantom answer (`src/simulate.py`): 8-hour shift starting empty, 1,000 repeats; the
   real average wait divided by the printed wait, and callers still waiting at close.

Error ranges: 95% bootstrap, 1,000 resamples of number sets within each load level, keeping each set's
4 versions together. No significance tests beyond these ranges; differences whose ranges overlap are
described as unclear.

## 6. What results would mean

- Phantom rates low at all loads >= 1.00: models notice impossibility on textbook-worded questions; the
  findings become false alarms, the near-line band and the cue.
- Phantom rates high just above 1.00 but low at 1.50: models notice big overloads and miss close ones.
- Phantom rates fall a lot when capacity is stated: misses come from working out or attending to
  capacity, not from not knowing the rule. The capacity-in-reply measure separates the two partly.
- 4-agent false alarms above 1-agent: models compare calls to one agent's speed (the multi-server trap).
- Cue closes most of the gap: the failure is not checking, not inability.

## 7. Limitations known in advance

Offering `ANSWER: NONE` is itself a hint; textbook terms (Poisson, exponential) likely help models;
stating capacity is also a hint; only small local models; one problem family (waiting lines); one
wording. More impossible than possible questions (because of extra sets near the line), so rates are
reported separately for each, never pooled across them.

## 8. Changes after commit

Any change after this file is committed is listed here with its date and reason, and analyses affected
by it are labeled exploratory.
