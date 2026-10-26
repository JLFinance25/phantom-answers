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

- **Oct 12, 2026 (before any study run), filled after the qwen3:8b thinking-off pilot:** 2 agents NOT
  added (pilot: about 25 s per answer, roughly 18 hours per setting, so no room). qwen3:8b thinking off
  runs on the Mac (M5 Pro, 24 GB), not the PC as PLAN.md D10 said, because the PC is not set up yet.
  Ollama 0.40.3; model qwen3:8b, ID 500a1f067a9f. Timing for the other two settings is added here
  before they run. Main runs started by Claude at Jayden's request.
- **Oct 12, 2026 (before any study run):** the qwen3:8b thinking-on pilot ran away (one reply passed
  19,500 tokens and never ended, at Ollama's default context of 4,096). Every run now uses a context of
  8,192 tokens and a hard cap of 6,000 generated tokens (thinking plus reply). A reply that hits the cap
  without an `ANSWER:` line counts as a format failure under section 4. The cap is recorded per reply
  (`done_reason`). Pilot timing so far was measured while two other projects shared the same Mac, so
  it overstates time per answer.
- **Oct 12, 2026 (before any study run). Drafted by Claude; approved by Jayden on Oct 12, 2026.** The
  qwen3:8b thinking-off main run started earlier today was stopped along with the runaway thinking-on
  pilot, before it saved any reply (`data/raw/main/` was never created), so no study data exists yet.
  This corrects "Main runs started" in the first entry above. Both qwen3:8b settings (thinking off and
  on) now run on Jayden's Windows PC instead of the Mac, as PLAN.md D10 first planned, because the Mac
  is shared with other projects (which also inflated the Mac pilot timing). PC: RTX 3060 Ti 8 GB,
  Ollama 0.40.3 on default server settings; model qwen3:8b, ID 500a1f067a9f, a byte-for-byte copy of
  the Mac's (SHA-256 checked Oct 12). Every request still sets temperature 0, a context of 8,192 tokens
  and a 6,000-token cap. A new 10-question timing pilot runs on the PC first; its seconds per answer
  are added here before the main run. All qwen3:8b study runs stay on the PC; gpt-oss:20b stays on
  the Mac.
- **Oct 12, 2026 (before any study run), PC timing pilot. Drafted by Claude; approved by Jayden on
  Oct 12, 2026.** Same 10 questions as the Mac pilot, saved in `data/raw/pilot/*-pc.jsonl` (not study
  data); the PC's Ollama log showed no other requests during the pilot. **qwen3:8b thinking off:**
  6.2 s per answer once the model is loaded (the first answer, 18 s, includes loading), 0 format
  failures, so the main run of 2,560 questions takes about 4.5 hours, plus about 30 minutes for the
  repeat set. **qwen3:8b thinking on:** about 60 s per answer; 5 of 10 replies hit the 6,000-token
  cap while still thinking (at least one was looping), and 1 ended with `\boxed{}` instead of an
  `ANSWER:` line, so 6 of 10 would be format failures. Thinking on does not run until Jayden decides
  how to handle this, recorded here first. **2 agents stay out:** the first entry's reason (25 s
  per answer) was inflated by the shared Mac, but the 1- and 4-agent question set is already fixed and
  thinking-on time is now the tighter limit. **Machines differ:** the PC's and the Mac's replies to the
  same 10 questions were word-for-word identical on only 3 and gave different numbers on 2 (both wrong
  on both machines; every reply fell in the same scoring group), so each setting keeps all its runs on
  one machine (PLAN.md D10). The `model_digest` field now saves the model's real ID (commit b0b8866).
  The main run is driven from the Mac through an SSH tunnel to the PC's Ollama.
- **Oct 12, 2026 (before any gpt-oss study run), Mac timing pilot for gpt-oss:20b. Drafted by Claude;
  approved by Jayden on Oct 13, 2026 (in the research orchestrator chat: "you can run those in the session", confirmed "yes you have permission. get it done").** Same 10 questions as the qwen3:8b pilots, saved in
  `data/raw/pilot/gpt-oss-20b.jsonl` (not study data). Mac (M5 Pro, 24 GB), Ollama 0.40.3, model
  gpt-oss:20b ID 17052f91a42e, reasoning "low", context 8,192, cap 6,000 tokens; no other model was
  loaded on the Mac during the pilot. 4.8 s per answer once loaded (the first answer, 17 s, includes
  loading); 0 replies hit the cap; 0 format failures; every reply included reasoning text, so the
  "low" setting is applied. The main run (2,560 questions plus the 300-call repeat set) stays on the
  Mac and goes through the shared waiting line; at the pilot's pace it takes about 4 to 5 hours
  (estimate: in the qwen3:8b main run, 4-agent questions ran much slower than its pilot suggested).
- **Oct 13, 2026 (before any thinking-on study run). Drafted by Claude; approved by Jayden on
  Oct 13, 2026 (in the main session chat: "approve PREREG-PENDING.md for the 10-question thinking-on
  check (1-agent, cap 12,000) and run it on the PC once it's reachable").** qwen3:8b thinking on runs on **1-agent questions only** (1,280 of the 2,560; all loads,
  both cue versions, both capacity versions), with the generated-token cap raised from 6,000 to
  **12,000** and the context window from 8,192 to **16,384** so the cap fits. Reason: in the PC timing
  pilot (Oct 12), 4 of 5 four-agent replies hit the 6,000 cap while still thinking, so 4-agent questions
  would mostly be format failures at any affordable cap; 1 of 5 one-agent replies hit the cap (at load
  exactly 1.00). The repeat set for this setting draws its 100 questions from the 1-agent questions only.
  Same machine (Jayden's PC), model qwen3:8b ID 500a1f067a9f, temperature 0, Ollama 0.40.3 and server
  settings as in the earlier entries. Run on the PC itself (`src/run_models.py --setting
  qwen3-8b-think --agents 1 --num-predict 12000 --num-ctx 16384`), so the Mac is not needed. Before
  the main run, a **10-question check** at the new settings (`--pilot 10 --pilot-tag pc-cap12000`, not
  study data) records seconds per answer, cap hits and format failures here. The main run goes ahead
  only if Jayden approves after seeing that check. Because thinking on covers only 1-agent questions,
  comparisons with thinking off use 1-agent questions only, and no 4-agent result exists for this
  setting (a limitation, stated in the write-up).
- **Oct 13, 2026, result of the 10-question thinking-on check (not study data). Recorded by Claude, as
  the entry above requires.** Run on the PC itself, started by the research orchestrator at 5:27 pm, ended
  5:55 pm; saved in `data/raw/pilot/qwen3-8b-think-pc-cap12000.jsonl` (SHA-256 5dfa56c3..., same on the PC
  and the Mac). qwen3:8b ID 500a1f067a9f, thinking on, 1-agent questions, cap 12,000, context 16,384.
  **0 of 10 hit the cap** (longest reply 5,046 tokens); **0 format failures**; all 10 scored correct
  (5 flagged at loads 1.00 to 1.25, 5 accurate waits). **133 s per answer on average** (57 to 256 s), at
  19 to 24 tokens per second: with the 16,384 context, `ollama ps` showed the model 20% on the processor
  and 80% on the graphics card, so it ran about 3 times slower than in the Oct 12 pilot (about 66 to 70
  tokens per second, context 8,192). At this pace the 1,280-question main run takes about 47 hours and the
  300-call repeat set about 11 hours (estimate). The main run waits for Jayden's decision.
- **Oct 13, 2026: thinking-on main run approved.** After seeing the check above, Jayden approved in the
  main session chat: "run the full qwen3:8b thinking-on main run (1-agent, cap 12,000) plus its repeat
  set on the PC itself." Settings unchanged from the entry above (context 16,384); about 47 hours plus
  about 11 hours for the repeat set (estimate from the check).
- **Oct 15, 2026 (after the qwen3:8b thinking-off and gpt-oss:20b main runs were scored). Drafted by Claude;
  approved by Jayden on Oct 15, 2026 (typed "yes" in the main session chat to: "Should the labeling go to a
  blind Claude sub-session?").** Deviation from section 4: the 150-reply hand-check is labeled by a Claude
  sub-session ("Phantom: blind labels"), not by Jayden. Reason: Jayden chose not to hand-label 150 replies and
  wants the project to keep moving. How it stays blind: that session reads only the question and reply text in
  `data/processed/handcheck/sheet.html` and may not open the key (`key_DO_NOT_OPEN.csv`), the scorer's output
  or any results file; the main session runs `handcheck.py compare` afterwards. Same draw (seed 20261013),
  same three groups, same labels (NONE / NUMBER / UNCLEAR plus "would a manager know"). **What this changes:**
  the agreement percentage measures Claude's reading against Claude's scorer (same model family, so errors
  can be shared), which is weaker evidence than a human check; the report must say so. Jayden may label a random
  20 of the 150 himself later as an optional spot-check; that is not a blocker. The scoring rules in section 4
  do not change, and the LaTeX-wrapped answer lines stay a labeled exploratory check (main numbers use the
  pre-registered scoring).
- **Oct 15, 2026 (after the qwen3:8b thinking-off and gpt-oss:20b main runs were scored and the hand-check
  was compared). Drafted by Claude; approved by Jayden on Oct 15, 2026 (typed in the main session chat: "Yes,
  make the LaTeX-fix scoring the main scoring and log it as a section 8 deviation").** Deviation from section
  4: the **main scoring now also reads an `ANSWER:` line wrapped in LaTeX** (`\boxed{ANSWER: x}`,
  `\boxed{\text{ANSWER: x minutes}}`, `\text{ANSWER: } x`), as the reader already did for other formatting
  (`**`, `$`, `\boxed{}` after `ANSWER:`). It is a program-bug fix under section 4, not a change to the rules
  there (last `ANSWER:` line; NONE-words flagged; any number = number; missing or unreadable = format failure).
  Reason: the hand-check (Oct 15, blind Claude labeler, 147 of 150 agree) found that all 3 disagreements are
  LaTeX-wrapped answer lines the labeler read as numbers and the committed reader called format failures; with
  the fix, agreement is 150 of 150 (computed from `labeled_latexfix.csv`). **Effect on the finished runs:** 60
  of 2,560 qwen3:8b thinking-off replies change (58 become numbers on 4-agent questions that settle, none of
  them accurate; 1 becomes a phantom answer at load 1.02, 1 agent; 1 becomes a correct flag); phantom answers
  go from 18 to 19 of 1,440; gpt-oss:20b has none. Replies with no `ANSWER:` text at all (for example `\boxed{x}`
  alone) stay format failures. **Which file is which from now on:** `data/processed/*_latexfix.csv` (made with
  `parse_replies.py --latex-fix` and `analyze.py --tag _latexfix`) is the MAIN scoring; the original
  pre-registered-reader files (`labeled.csv`, `summary.csv`, and so on) are kept unchanged and reported as a
  labeled check next to it. The code defaults are not changed, so both can be re-made. Applies to every setting,
  including thinking on.
