# Phantom Answers Near Capacity: do small language models print a wait time for a waiting line that never settles?

**Draft, Oct 15, 2026 (final wording pass Oct 24, 2026). Not peer-reviewed.**
**Status:** I read and approved the short version and sections 4.1, 4.2, 7, 9 and 11 on Oct 26, 2026; I have not reviewed the other sections, and I did not re-check the numbers myself. I decided the LaTeX scoring question (section 3) and chose a blind AI labeler for the hand-check instead of labeling it myself (section 9); my optional 20-reply spot-check is still open. Who did what: see "Acknowledgments and AI use" in the README.

Scope: the two runs scored on Oct 15 (qwen3:8b with thinking off, and gpt-oss:20b; sections 4 to 7), plus the qwen3:8b thinking-on run (1-agent questions only), which finished Oct 17 and is scored in section 8 (first results, not hand-checked). The hand-check (section 9) covers thinking off only and was done by a blind AI labeler, not by me.

## The short version

This box only repeats results from the sections named; it adds nothing new.

- When a waiting line can never settle, the right answer to "what is the long-run average wait?" is NONE. Printing a number anyway is what this report calls a **phantom answer**.
- gpt-oss:20b gave 0 phantom answers on 1,440 such questions. qwen3:8b (thinking off) gave 19 (1.3%) under the main scoring, or 18 under the original pre-registered scoring program (section 4.1).
- The pre-registered prediction, that qwen3:8b would be fooled often right next to the limit, was wrong (section 4.2). Both models switch from giving a number to saying NONE between loads 0.98 and 1.00 (section 4.3).
- Every phantom answer came from questions without the cue sentence (section 4.4). The models' bigger weakness was arithmetic with 4 agents, on questions that do have an answer (section 4.6).
- With thinking on, qwen3:8b gave the same number of phantom answers (13 of 720 on one-agent questions) but often gave no answer at all (188 of 1,280 replies), and it was about 53 times slower (section 8).
- Main caveats: small local models, one wording, thin counts, a scoring change made after the data were seen, and a hand-check done by a Claude labeler rather than a person (sections 3, 7 and 9).

## How numbers are cited in this draft

Every number carries a tag in square brackets that names the file it came from. All were pulled or recomputed on **Oct 15, 2026** from the files as they stood that day (the processed tables are dated Oct 13, 2026). Anything without a tag, or tagged UNVERIFIED, was not checked against a file. **Since Oct 15, 2026 the main scoring is the LaTeX-fix reader** (section 3), so the main numbers come from the `_LFX` files; the original pre-registered reader's numbers are kept as a labeled check. **Section 8 (thinking on) was pulled and recomputed on Oct 17, 2026**, from the same files after the thinking-on run was added to them.

| Tag | File | How it was used |
|---|---|---|
| [SUM-LFX] | `data/processed/summary_latexfix.csv` | **main scoring (LaTeX-fix reader).** Read directly |
| [SUM] | `data/processed/summary.csv` | check: the original pre-registered reader. Read directly |
| [LAB-LFX] | `data/processed/labeled_latexfix.csv` (6,400 rows since Oct 17: 2,560 for each of the two finished models, 1,280 for thinking on; it had 5,120 on Oct 15) | **main scoring.** Counted by a short script on Oct 15 (sections 4 to 7) and again Oct 17 (section 8) (counts of rows by setting, agents, load, outcome). The old rows did not change when thinking on was added [WORKLOG, Oct 17] |
| [LAB] | `data/processed/labeled.csv` | check: the original pre-registered reader; same counting |
| [OUT] | `data/processed/outcome_shares.csv` (and `outcome_shares_latexfix.csv`) | read directly; the Oct 15 spot-check against [LAB] (qwen3:8b, 1 agent, uncued, capacity not stated, loads 1.00, 1.02, 1.50) was for the original-reader file; those three cells are the same under both readers, see section 4.2 |
| [TRAP-LFX] / [TRAP] | `data/processed/multi_server_trap_latexfix.csv` (main) and `multi_server_trap.csv` (check) | read directly |
| [COST] | `data/processed/miss_costs.csv` | read directly; for thinking off it covers the 18 phantom replies of the original reader only (section 4.5). The 19th thinking-off phantom answer under the main scoring (`a1_L1.02_s28_UK`) was never run through `simulate.py`, so it is not in section 4.5. Since Oct 17 the file also holds 13 thinking-on rows (31 in all, row counts checked Oct 17); they are not summarized in this draft |
| [RAW] | `data/raw/main/qwen3-8b-nothink.jsonl`, `gpt-oss-20b.jsonl` | `done_reason` field counted on Oct 15 |
| [REP] | `data/raw/repeats/*.jsonl`; scored copies `data/processed/labeled_repeats_latexfix.csv` (main) and `labeled_repeats.csv` (check) | scored on Oct 15 with `python3 src/parse_replies.py --repeats --latex-fix` (and `--repeats`), then compared with the matching temperature-0 reply in [LAB-LFX] (or [LAB] for the check); the saved files give the same section 6 numbers |
| [RAW-T] | `data/raw/main/qwen3-8b-think.jsonl` (1,280 records), `data/raw/repeats/qwen3-8b-think.jsonl` (300 records) | thinking-on raw replies, copied from the PC Oct 17 (SHA-256 recomputed Oct 17). Used only for the `done_reason`, `seconds`, `eval_tokens` and `time` fields and an automatic check for empty replies, "answer:" and `\boxed`; joined to [LAB-LFX] by question ID. Counted Oct 17, 2026 |
| [THINK] | `python3 -I src/think_report.py` and the files it writes, `data/processed/think_vs_others_1agent.csv` and `repeats_agreement.csv` | completeness checks ("all passed") and the original-reader 1-agent table, run Oct 17, 2026. It reads the original-reader files, so the main-scoring table in section 8.2 was counted separately from [LAB-LFX] |
| [BOOT] | `src/analyze.py` (`bootstrap` function), run on [LAB] (original reader) | recomputed on Oct 15 for one cell the saved tables do not hold |
| [PREREG] | `PREREG.md` | quoted or paraphrased |
| [PLAN] | `PLAN.md` | quoted or paraphrased |

## 1. Question

When a long-run waiting-line question has **no valid answer** because the load is at or above capacity, how often do small local language models still print a number (a "phantom answer")? How does that rate change with four things, while the wording and answer format stay fixed: the load (0.5 to 1.5), the number of agents (1 or 4), a cue asking whether the staffing is workable, and stating the team's total capacity outright? [PREREG section 1]

**Load** = calls arriving per hour / (agents x calls each agent can handle per hour). Example: 49 / (4 x 12) = 1.02. At a load of 1 or more, the line grows without limit, so the long-run average wait does not exist and the right answer is NONE. Even at exactly 1.00 the line never settles, because the arrivals and call lengths are random: time an agent spends idle during a quiet stretch is lost for good and cannot be used to catch up later. [PLAN section 2]

Words used throughout:
- **Impossible question:** load 1.00 or more, so the only correct answer is NONE. **Settling question:** load below 1.00, so a real average wait exists.
- **Flagged:** the reply's answer is NONE or an infinity word. On an impossible question that is correct; on a settling question it is a **false alarm**.
- **Format failure:** a reply with no readable final answer line. It is neither a phantom answer nor a correct answer, and it is always counted as its own group.
- **Cue:** the extra sentence "Is this staffing level workable in the long run?". **Capacity stated:** the question also writes out the team's total calls per hour.
- **Cell:** one combination of model, agents, load, cue and capacity-stated.

## 2. Method

**Questions.** One fixed template: a call center where calls arrive at random (Poisson arrivals, the standard textbook model of random arrivals) and call lengths are random (exponential call lengths, the matching textbook model); the question says "assume these rates continue indefinitely" and asks for the long-run average wait in line, in minutes. The reply must end with `ANSWER: <minutes to one decimal>` or `ANSWER: NONE`. The template and the cue and capacity-stated variants are in [PLAN section 5]. The questions were generated by `src/make_questions.py` with seed 20261012 (a fixed starting value for the random-number generator, so the same questions come out every time) into `data/processed/questions.csv` (2,560 questions) [PREREG section 3].

- 12 load levels: 0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 1.00, 1.02, 1.05, 1.10, 1.25, 1.50. 1 agent and 4 agents.
- 4 versions of every number set: uncued or cued, capacity stated or not. All 4 versions share the same numbers.
- 20 number sets per (agents, load); 40 at loads 0.98, 1.00, 1.02, 1.05 [PREREG section 3].
- Impossible questions are those with a load of 1.00 or more. Per model that is 1,440 of 2,560; 1,120 settle [LAB-LFX].

**Answer key.** `src/answer_key.py` gives NONE when the load is 1 or more (checked with whole numbers, so 1.00 is exact), the standard one-agent formula for 1 agent, and Erlang C (the standard formula for a line served by several agents) for 4 agents. It was re-checked Oct 13 a second way (state probabilities summed directly): all 280 number sets that settle match within 0.05 minutes [first-results-2026-10-13.md]. It was re-checked again Oct 15 with an independent calculation (direct state probabilities, no Erlang C formula): 0 of the 1,120 settling questions differ by more than 0.05 minutes [audit-2026-10-15.md, row 10]. That second check is on the saved key values in `questions.csv`; `answer_key.py` itself was not re-run.

**Models and settings.** Temperature 0 (the model always picks its most likely next word, so the same question gives the same reply), one reply per question, context 8,192 tokens (how much text the model can hold at once; a token is roughly a word or part of a word), and a cap of 6,000 generated tokens (set in [PREREG section 8] after a thinking-on pilot test ran away).
- qwen3:8b, thinking off, model ID 500a1f067a9f, on Jayden's Windows PC (RTX 3060 Ti 8 GB), Ollama 0.40.3 (Ollama is the program that runs the model locally).
- gpt-oss:20b, reasoning "low", model ID 17052f91a42e, on Jayden's Mac (M5 Pro, 24 GB), Ollama 0.40.3.
- Each model stayed on one machine for all runs, because the same 10 pilot questions gave different replies on the two machines [PREREG section 8].
- Repeat set: 100 questions x 3 repeats at temperature 0.7 (which lets the wording vary from run to run) per model, reported separately in section 6 [PREREG section 3].

**Pre-registration.** A pre-registration is a dated file that fixes the question, predictions and scoring rule before any data are collected, so they cannot be bent to fit the results. `PREREG.md` was first committed Oct 12, 2026 (commit caf71ed) before any study run, and the scoring code was committed as `3ff3c21` the same day ("Study code, fixed at pre-registration") (`git log`, Oct 15). Section 8 of `PREREG.md` lists every later change with its date. The qwen3:8b main run ended Oct 12 at 11:28 pm (its repeats at 11:55 pm); the gpt-oss:20b main run ended Oct 13 at 3:19 am (its repeats at 3:40 am) [the `time` field in `data/raw/main/*.jsonl` and `data/raw/repeats/*.jsonl`]; the scoring ran after.

## 3. Scoring rule as pre-registered, and the change to the main scoring

[PREREG section 4], carried out by the scoring program `src/parse_replies.py` (called "the reader" below):

- Read only the **last** `ANSWER:` line of the final reply. Ignore any thinking text.
- NONE, infinite, infinity, the infinity sign, unbounded, undefined (any capitalization) = **flagged**. Any number = **number**. Missing or unreadable = **format failure**, its own group, never dropped.
  - Note: the scorer (`NONE_WORDS` in `src/parse_replies.py`) also treats a bare "inf" or "+inf" as flagged. [PREREG section 4] does not list those two words. No final answer line in the data starts with a bare "inf" in either model's main or repeat replies (audit-2026-10-15.md, row 19), so no result changes.
- On an impossible question: flagged = correct; number = **phantom answer**.
- On a question that settles: flagged = **false alarm**; a number counts as accurate if it is within 2% of the key or within 0.1 minute.
- A looser second measure, "mentions trouble": the reply contains any phrase from the fixed list `TROUBLE_PHRASES` in `src/parse_replies.py` (for example "unstable", "grows without bound", "exceeds capacity", "cannot keep up").
- A reply that hit the token cap with no `ANSWER:` line is a format failure.

**Main scoring since Oct 15, 2026: the "LaTeX fix" reader (a deviation, logged).** LaTeX is a code for typesetting math; some replies wrapped their final answer line in it. The LaTeX-fix reader follows all the rules above and also reads an answer line wrapped in LaTeX, such as `\boxed{ANSWER: 0.2}`, `\boxed{\text{ANSWER: x minutes}}` or `\text{ANSWER: } x`. It is run through `parse_replies.py --latex-fix`, and every file made with it is tagged `_latexfix`.

Why: the hand-check (section 9) found 3 replies whose final line is wrapped in LaTeX. The original reader called them format failures, although a person reads them as numbers, and the same reader fix brings all 150 hand-check labels into agreement. Jayden approved making it the main scoring on Oct 15 (typed yes in the main session chat), and Claude logged it as a deviation in [PREREG section 8] (the Oct 15 entry that begins "after the qwen3:8b thinking-off and gpt-oss:20b main runs were scored and the hand-check was compared"). That entry classes it as a fix to a bug in the program under section 4, not a change to the rules there. **Whether that classification holds is a judgment, and it was made after seeing the data**, so it is a deviation and is reported as one. Replies with no `ANSWER:` text at all (for example `\boxed{x}` alone) stay format failures.

**In this report the main numbers are the LaTeX-fix numbers; the original pre-registered reader's numbers are shown next to them as a labeled check** (`labeled.csv`, `summary.csv` and the other files without the `_latexfix` tag, kept unchanged). Effect of the change on the two finished runs: 60 of 2,560 qwen3:8b replies change, gpt-oss:20b none (details in section 4.6) [LAB], [LAB-LFX].

## 4. Results

### 4.1 Headline

Both models almost never print a wait for a line that can never settle. That is the opposite of what the pre-registered prediction said for qwen3:8b.

| Model | Impossible questions | Phantom answers, MAIN scoring (LaTeX fix) | Phantom answers, check (original pre-registered reader) |
|---|---|---|---|
| gpt-oss:20b | 1,440 | 0 | 0 |
| qwen3:8b, thinking off | 1,440 | 19 (1.3%) | 18 (1.3%) |

Sources: [LAB-LFX], [LAB]. The `phantom_rate` columns give the same totals: [SUM-LFX] gives 6 + 7 + 6 = 19 for qwen3:8b (three of the eight setting rows, at 3.3%, 3.9% and 3.3% of 180 impossible questions) and 0 for gpt-oss:20b, and [SUM] gives 6 + 6 + 6 = 18 for qwen3:8b and 0 for gpt-oss:20b. Both percentages round to 1.3% (19 of 1,440 is 1.32%, 18 of 1,440 is 1.25%).

### 4.2 The pre-registered prediction, stated plainly

**The prediction for load 1.02 and load 1.00 was wrong. The prediction for 1.50 was right only because it said "rarely" and the result was zero.** Cell: qwen3:8b, thinking off, 1 agent, uncued, capacity not stated [PREREG section 2].

| Load | Predicted phantom rate | Result [LAB-LFX], [OUT] | Verdict |
|---|---|---|---|
| 1.02 | more than 60% | 6 of 40 = 15% (95% range 5% to 27.5%, [BOOT]) | **Wrong.** Far below 60%. |
| 1.00 | 35% to 65% | 0 of 40 = 0% | **Wrong.** Far below 35%. |
| 1.50 | under 20% | 0 of 20 = 0% | Right (but see below) |

The "95% range" is a bootstrap range: the number sets are resampled many times to see how much the rate could move by chance.

- Predicted order (highest at 1.02, lower at 1.00, lowest at 1.50): 1.02 is highest, but 1.00 and 1.50 tie at 0 [LAB-LFX].
- The prediction's "most surprising possible result" (20% or more at 1.50) did not happen [LAB-LFX].
- The choice of reader does not change these three cells: the original pre-registered reader gives the same 6 of 40, 0 of 40, 0 of 20 [LAB]. The 60 replies the reader change moves are all qwen3:8b, none of them in this cell (1 agent, uncued, capacity not stated); the bootstrap range was computed on [LAB] and applies unchanged.
- In short: Jayden predicted the models would be fooled often near the limit. These two models mostly were not. They flag impossible questions even one hundredth above capacity. That is a negative result against the prediction, and it stays in the report.

### 4.3 Flag rate by load (the curve)

Share of replies flagged (NONE or an infinity word) by load, with all four versions pooled within a load level. Each load level is either entirely impossible (1.00 and up) or entirely settling (below 1.00), so pooling versions does not mix the two. Counts are replies; the denominator is in the "n" column. Main scoring [LAB-LFX]; the original reader gives the same table except one cell (qwen3:8b, 4 agents, load 1.00: 153 instead of 154) [LAB].

| Load | n per model-agents cell | qwen3:8b, 1 agent | qwen3:8b, 4 agents | gpt-oss:20b, 1 agent | gpt-oss:20b, 4 agents |
|---|---|---|---|---|---|
| 0.50 | 80 | 0 | 0 | 0 | 0 |
| 0.70 | 80 | 0 | 0 | 0 | 0 |
| 0.80 | 80 | 0 | 0 | 0 | 0 |
| 0.90 | 80 | 0 | 0 | 0 | 0 |
| 0.95 | 80 | 0 | 0 | 0 | 0 |
| 0.98 | 160 | 0 | 0 | 0 | **2** (both false alarms) |
| 1.00 | 160 | **160** | 154 | 160 | 160 |
| 1.02 | 160 | 147 | 160 | 160 | 160 |
| 1.05 | 160 | 160 | 160 | 160 | 160 |
| 1.10 | 80 | 80 | 80 | 80 | 80 |
| 1.25 | 80 | 80 | 80 | 80 | 80 |
| 1.50 | 80 | 80 | 80 | 80 | 80 |

- The models jump from almost never flagging at 0.98 to almost always flagging at 1.00. The switch point (the load where the flagged share first reaches 50%, drawing a straight line between levels) is 0.99 in 14 of the 16 setting rows; the other two are 0.9895 (gpt-oss:20b, 4 agents, cued, capacity not stated) and 0.9918 (qwen3:8b, 4 agents, uncued, capacity stated) [SUM-LFX]. The original reader gives the same values except 0.9921 for the qwen3:8b row [SUM]. Note that 0.99 is just the midpoint between the 0.98 and 1.00 levels: it means "somewhere between 0.98 and 1.00", not a measured 0.99. This is the "dull step" that [PLAN section 8] warned about.
- The 13 non-flagged replies at 1.02 (1 agent, qwen3:8b) are all phantom answers; the 6 non-flagged at 4 agents, load 1.00 are all phantom answers [LAB-LFX]. (With the original reader the 13 are 12 phantom answers and 1 format failure, and the 7 at 4 agents are 6 phantom answers and 1 format failure [LAB]; those two format failures are the replies the reader change recovers.)
- Figures: `figures/flag_rate_vs_load.png`, `figures/number_rate_vs_load.png` (and `_latexfix` versions, which show the main scoring) were built by `src/analyze.py`; this draft did not re-open them.

### 4.4 Where the phantom answers are (all 19, qwen3:8b only)

[LAB-LFX], [COST], [OUT]. Under the original reader the same list has 18; the 19th is the one reply the reader change turns into a number (see the bullets).

- **All 19 are in the uncued versions. The cued versions (720 impossible replies per model) have 0 phantom answers for both models** [LAB-LFX]. For gpt-oss:20b there were none anywhere. For qwen3:8b the cue removed every one. Because there were so few phantom answers to begin with, this is a small effect in absolute terms.
- **13 phantom answers at load 1.02, 1 agent**: 6 in the uncued, capacity-not-stated version and 7 in the uncued, capacity-stated version, spread over 7 number sets (6 sets wrong in both versions) [LAB-LFX]. The 13th, `a1_L1.02_s28_UK`, prints 100.9 minutes; the original reader called it a format failure because its answer line is wrapped in LaTeX. The other 12 are the 12 of the original-reader count [LAB], [COST].
  - From reading two of the original twelve on Oct 15, the pattern is an arithmetic slip: the model divides arrivals by capacity and gets a number just under 1 (for example 9.2 / 9 written as "about 0.9111", when the true value is 1.022), then applies the textbook one-agent formula with no sign of doubt. The slip is "could not divide correctly", not "did not know the rule".
  - This was checked on 2 of the 12 replies; the claim for the other 10 is from the earlier first-results draft and is UNVERIFIED by this draft. The 13th reply (`a1_L1.02_s28_UK`) was not read for this draft: whether it fits the "slip" description is UNVERIFIED.
- **6 phantom answers at load exactly 1.00, 4 agents, uncued, capacity stated.** In the one reply read on Oct 15, the model writes that the load is exactly 1, calls the system "critically loaded" and says the queue "will grow indefinitely", says the usual formula is "not valid", then invents an "approximation" and prints 1.4 minutes. All 6 reply texts contain a phrase from the trouble list [LAB-LFX: `mentions_trouble` is true for 6 of 19 phantom answers, and these are those 6, per [COST]]. This is the "noticed but answered anyway" group. It is the only group of that kind in the data.
- **All 19 phantom replies contain the correct total capacity number** [LAB-LFX `capacity_in_reply`]. That measure tells us nothing for 1 agent (the capacity equals the agent's rate, which is copied from the question), so it supports an "attention, not arithmetic" reading only for the 6 four-agent replies. Even there, "contains the number" does not show that the model compared it with the arrivals. UNVERIFIED.
- With **capacity stated** there were 13 of the 19 phantom answers (7 at 1.02 plus 6 at 1.00 with 4 agents); with capacity not stated, 6 [LAB-LFX]. (Original reader: 12 of 18 versus 6 [LAB].) So in these data stating capacity did **not** reduce phantom answers. With so few events I would not claim it increased them.

### 4.5 Cost of a phantom answer (pre-registered measure 9)

**This section covers the 18 thinking-off phantom answers of the original reader** (the 13 thinking-on rows in [COST] are not summarized; see section 8.3). The 19th (`a1_L1.02_s28_UK`, printed 100.9 minutes) was not simulated; `miss_costs.csv` was not re-made for the main scoring. It is a 1-agent reply, so the 4-agent row below is unaffected; whether it changes the 1-agent row's ranges is UNVERIFIED.

How the cost was measured: for each phantom reply, `src/simulate.py` plays out one 8-hour shift, caller by caller, starting with an empty line, 1,000 times, and saves the result in [COST] [PREREG section 5].

| Group | Printed wait (min) | Real average wait over the shift (min) | Callers still waiting at close |
|---|---|---|---|
| 12 replies at load 1.02, 1 agent (4 distinct printed values) | 37.5 to 598.4 | 24.6 to 38.4 | 8.4 to 17.3 |
| 6 replies at load 1.00, 4 agents | 1.4 to 1.5 | 16.9 to 17.0 (11.3 to 12.1 times the printed wait) | 17.1 to 18.8 |

So a phantom answer can mislead in either direction. The 4-agent answers promise a wait about 11 to 12 times too short. All 12 one-agent answers print a wait **longer** than the 8-hour shift's real average [COST]. The 8-hour shift is a modelling choice from [PLAN D15]; no dollar figures are given.

### 4.6 Questions that settle

[LAB-LFX] (main scoring); original-reader numbers from [LAB] in brackets where they differ.

| Model | Agents | n | False alarms | Accurate (within 2% or 0.1 min) | Format failures |
|---|---|---|---|---|---|
| gpt-oss:20b | 1 | 560 | 0 | 560 (100%) | 0 |
| gpt-oss:20b | 4 | 560 | 2 | 126 (22.5%) | 0 |
| qwen3:8b | 1 | 560 | 0 | 549 (98.0%) | 0 |
| qwen3:8b | 4 | 560 | 0 | 12 (2.1%) | 37 (original reader: 95) |

**A correction to the earlier first-results draft.** `writeup/first-results-2026-10-13.md` lists 1 format failure for qwen3:8b with 1 agent and 96 with 4 agents on questions that settle (that draft used the original reader). Recounting from [LAB] (original reader) on Oct 15: the 1-agent failure and the extra 4-agent failure are both on **impossible** questions (`a1_L1.02_s28_UK` and `a4_L1.00_s19_UK`). On questions that settle the counts are 0 and 95. The model's total of 97 format failures is unchanged (95 + 2). Under the main scoring those two impossible-question failures are gone (one becomes a phantom answer, one a correct flag) and the total is 37, all on questions that settle [LAB-LFX].

- **The multi-server trap barely shows.** (The "trap": every 4-agent question that settles has more calls than one agent could handle, so a model that compares the calls with one agent's speed instead of the whole team's would wrongly call it impossible [PLAN D8; PREREG sections 5 and 6].) False alarms with 4 agents minus 1 agent at matched settings: 0 in 7 of the 8 model x cue x capacity cells. The 8th is gpt-oss:20b, cued, capacity not stated, where 4 agents give 1.4 percentage points more false alarms than 1 agent (2 of 140 versus 0 of 140) [TRAP-LFX]. [TRAP] (original reader) is identical. Those 2 are `a4_L0.98_s03_CN` and `a4_L0.98_s32_CN`, both at a true load of 0.9792 [LAB]. In total, there were 2 false alarms in 2,240 replies to questions that settle, across both models [LAB].
- **The big weakness is somewhere else: the arithmetic of 4 agents.** With 4 agents both models treat the line as settling, but cannot compute the wait (Erlang C). qwen3:8b is accurate on 2.1% and gpt-oss:20b on 22.5% [LAB]. This is not a phantom-answer result; it is an accuracy result on questions that do have an answer.
- **qwen3:8b format failures with 4 agents come from looping** (the reply repeats itself until it is cut off). 38 of its 2,560 main replies hit the 6,000-token cap [RAW]; all 38 are 4-agent questions at load 0.98 (12), 0.50 (15), 0.80 (4), 0.95 (3), 0.70 (2), 0.90 (2) [RAW joined to LAB]; 37 of the 38 are format failures [LAB-LFX]. Under the main scoring **all 37 of its format failures are cap hits** (Oct 15 recount: [RAW] joined to [LAB-LFX]); under the original reader 60 more were format failures only because of LaTeX wrapping. gpt-oss:20b had no replies at the cap [RAW].
- **What the reader change did (main scoring against the original-reader check):** it changes 60 qwen3:8b replies, all of them format failures under the original reader. 58 are 4-agent settling questions (95 to 37 failures; none of the 58 is accurate, so accuracy does not change), 1 becomes a phantom answer (19 instead of 18, the 7th uncued capacity-stated reply at 1.02 with 1 agent), and 1 becomes a correct flag (`a4_L1.00_s19_UK`). gpt-oss:20b has none [LAB], [LAB-LFX], [SUM-LFX].

## 5. Effect of the dials

- **Cue.** 0 of 720 impossible replies are phantom answers when cued, versus 19 of 720 for qwen3:8b when uncued (18 of 720 with the original reader), and 0 and 0 for gpt-oss:20b [LAB-LFX], [LAB]. For gpt-oss:20b there is nothing for the cue to remove, because it had no phantom answers uncued either.
- **Capacity stated.** No reduction in phantom answers (section 4.4). On questions that settle with 4 agents, gpt-oss:20b's accuracy is 28 of 140 uncued with capacity not stated versus 20 of 140 stated, and 49 of 140 cued with capacity not stated versus 29 of 140 stated [LAB-LFX] (the same under the original reader [LAB]). So stating the capacity did not raise its accuracy in either version. No error ranges were computed for these counts, and they are not interpreted further.
- **Number of agents.** Phantom answers appear at both 1 and 4 agents (13 and 6 [LAB-LFX]; 12 and 6 with the original reader [LAB]); false alarms are essentially zero at both.
- **Thinking on (1-agent only).** Same pattern for the cue (0 of 360 cued impossible replies are phantom answers, against 13 of 360 uncued) and the opposite direction for stated capacity (12 of 180 with it, 1 of 180 without); details and the format-failure side are in section 8 [LAB-LFX], [SUM-LFX].
- **Error ranges.** The pre-registered 95% bootstrap ranges (number sets resampled within each load level, the 4 versions of a set kept together, 1,000 resamples) are in [SUM-LFX] (main) and [SUM] (check). Where a range has zero width because the count is zero, read it as "not observed in this sample", not as proof that the true rate is zero.

## 6. Repeat sets (temperature 0.7, reported separately as pre-registered)

These test how stable the answers are when the model is allowed to vary its wording. 100 questions x 3 repeats per model (53 impossible questions; 48 with 1 agent and 52 with 4 agents). Scored Oct 15 with `src/parse_replies.py --repeats --latex-fix` (main scoring) and `--repeats` (original reader, check) [REP].

- gpt-oss:20b: 300 replies. All 100 questions gave the same label in all 3 repeats, and all 300 match the temperature-0 label. 0 phantom answers, 0 false alarms, 0 format failures.
- qwen3:8b, main scoring: 300 replies; all 3 repeats agree on 96 of 100 questions; 293 of 300 match the temperature-0 label (97.7%, compared with [LAB-LFX]). 2 phantom answers, 2 false alarms, 0 format failures. Check, original reader: 91 of 100 agree, 280 of 300 match (93%, compared with [LAB]), 2 phantom answers, 2 false alarms, 6 format failures. All 6 of those format failures become readable under the LaTeX-fix reader (0 left).
- The sample is small and not weighted to resemble the main set.

## 7. Limitations

From [PREREG section 7]:
1. Offering `ANSWER: NONE` in every question is itself a hint. Real-world phantom rates are probably higher than these.
2. The textbook terms (Poisson, exponential) likely help the models. This measures them at their best, not on plain manager wording.
3. Stating capacity is also a hint, so any drop would point to "arithmetic or attention", not arithmetic alone.
4. Only small local models. No frontier or online (API) model.
5. One problem family (waiting lines), one wording.
6. More impossible than settling questions (extra sets near the limit). Rates are therefore reported separately for each, never pooled across them.

What the first results added:

7. **The headline result is a plain step.** Almost all of the signal sits between 0.98 and 1.00 and almost none elsewhere, so the phantom-answer story rests on 19 replies from one model (18 with the original reader), 6 of them from one version at one load. That is thin. The error ranges are wide relative to the counts.
8. **The prediction was wrong, and this is a different finding from "models are fooled".** On this wording the models are mostly correct about impossibility; the failures are slips (the division) and one specific confusion at exactly load 1.00.
9. **4-agent accuracy is poor and format failures are common for qwen3:8b**; that makes its 4-agent results on settling questions partly a story about replies looping until the token cap, not just about understanding. None of the 38 cap hits is on an impossible question [RAW joined to LAB], so the phantom-answer counts are not affected by the loops.
10. **The main scoring was changed after the data were seen.** The LaTeX-fix reader became the main scoring on Oct 15 because of what the hand-check found (sections 3 and 9). The original reader's numbers are kept next to it as a check. The hand-check was done by a blind Claude labeler, not a human, so it is weaker evidence than the pre-registered human check (section 9).
11. **Thinking on has 1-agent questions only,** because 4-agent thinking-on replies mostly hit the token cap in the pilot [PREREG section 8]. No 4-agent result will exist for that setting, so thinking on and off can be compared on 1-agent questions only (section 8). Its results are first results: not hand-checked, and the 13 thinking-on phantom answers and 188 format failures rest on one model, one machine and one run.
12. **Machines differ.** The same pilot questions gave different replies on the PC and the Mac, so the two models' runs are not on identical hardware, and the model comparison is partly a machine comparison [PREREG section 8]. Whether that matters here is UNVERIFIED.
13. **Sample size per cell is small** (20 to 40 number sets). The 4 versions of a set share numbers, so they are not independent; that is why the error ranges resample whole sets. More number sets, not more replies, would add evidence.

## 8. Thinking on (qwen3:8b, 1-agent questions only; first results)

**Status: scored Oct 17, 2026 and not hand-checked. Jayden has not reviewed this section.** "Thinking on" means the model writes out hidden working before its final reply; only the final reply is scored. The hand-check script (`src/handcheck.py`) only reads the thinking-off file, so no thinking-on reply has been checked by a person or by the blind labeler (section 9). Whether to hand-check a sample is Jayden's decision and would need a `PREREG.md` entry first [thinking-on-scoring-runbook.md, section 3]. Every number below was recounted on Oct 17, 2026 from the files named in the tags, and no reply text was read. The counts come from the scored labels and from the `done_reason`, `seconds`, `eval_tokens` and `time` fields of the raw file. The only look inside reply text was an automatic check for the words "answer:" and `\boxed` and for an empty reply, used to split the format failures.

### 8.1 What was run, and what that limits

- Setting `qwen3-8b-think`: qwen3:8b (ID 500a1f067a9f), thinking on, temperature 0, **1-agent questions only: 1,280 of the 2,560** (all 12 loads, all 4 versions; 720 impossible, 560 that settle), generated-token cap **12,000** (not 6,000), context **16,384** (not 8,192), on Jayden's PC [PREREG section 8, Oct 13 entries]. Every record in the raw file has these settings [THINK: `think_report.py` check "settings seen"].
- Main run: 1,280 distinct questions, none missing, none duplicated; replies saved from Oct 13, 8:14 pm to Oct 17, 5:02 am [THINK], [RAW-T `time` field]. Repeat set: 100 one-agent questions x 3 at temperature 0.7 (300 replies), Oct 17, 5:03 am to 5:41 pm [RAW-T] (the 100 are the questions `run_models.py --agents 1 --repeats` draws [THINK]). The SHA-256 fingerprint of both raw files was recomputed on Oct 17 and equals the values logged when they were copied back from the PC (`data/raw/SOURCES.md`; WORKLOG, Oct 17).
- **Limitation: there is no 4-agent thinking-on result.** In the Oct 12 pilot 4 of 5 four-agent replies hit the 6,000-token cap [PREREG section 8], so those questions were left out. All comparisons below use the **same 1,280 one-agent questions** for the thinking-off and gpt-oss:20b settings; never put thinking on next to the 4-agent rows or the pooled tables in section 4.
- Scored with the main-scoring (LaTeX-fix) reader [LAB-LFX], as [PREREG section 8, Oct 15 entry] says it applies to every setting. The original pre-registered reader differs on the main run by one reply (a settling question at load 0.50: a format failure under the original reader, an accurate number under the main one) and on the repeat set by two replies [LAB], [REP].
- **There is no pre-registered prediction for thinking on.** [PREREG section 2] is written for thinking off only. Section 8.7 puts the same cell next to it for reference only.

### 8.2 The three settings on the same 1,280 questions

Main scoring [LAB-LFX], pulled Oct 17, 2026 (rows with `agents == 1`):

| Setting | Impossible n | Phantom answers | Correct flags | Format failures | Settling n | False alarms | Accurate numbers | Inaccurate numbers | Format failures |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss:20b | 720 | 0 | 720 | 0 | 560 | 0 | 560 | 0 | 0 |
| qwen3:8b, thinking off | 720 | 13 (1.8%) | 707 | 0 | 560 | 0 | 549 (98.0%) | 11 | 0 |
| **qwen3:8b, thinking on** | 720 | **13 (1.8%)** | 586 | **121 (16.8%)** | 560 | **0** | 493 (88.0%) | **0** | **67 (12.0%)** |

- Thinking on prints the same number of phantom answers as thinking off (13 each), but it also fails to produce an answer line on 188 of its 1,280 replies (14.7%), against 0 of 1,280 for both other settings [LAB-LFX]. (The original reader gives 12 phantom answers for thinking off, 13 for thinking on, and 189 failures for thinking on, with 68 on the settling side [LAB]; `think_vs_others_1agent.csv` and the table `think_report.py` prints are made from that original-reader file [THINK].)
- When thinking on does answer a settling question, the number is right: 493 of 493 are within the 2% or 0.1-minute tolerance [LAB-LFX]. It also raises no false alarm (0 of 560, as for the other two settings). Its lower accuracy in the table (88.0% against 98.0%) is entirely the 67 format failures.
- Of the 599 thinking-on replies to impossible questions that did produce an answer line, 13 are phantom answers (2.2%) [LAB-LFX; computed from the table].
- Paired on the same question, thinking off (rows) against thinking on (columns), main scoring [LAB-LFX], counted Oct 17:

| Thinking off \ Thinking on | Flagged (correct) | Format failure | Phantom answer | Number (settles) |
|---|---|---|---|---|
| Flagged (707 impossible) | 579 | 116 | **12** | n/a |
| Phantom answer (13 impossible) | 7 | 5 | 1 | n/a |
| Number (560 settle) | n/a | 67 | n/a | 493 |

So the two settings' 13 phantom answers are mostly on **different questions**. Only one question (`a1_L1.02_s03_UK`) is a phantom answer in both. 12 of the 13 thinking-on phantom answers are questions that thinking off flagged correctly, and thinking on flagged 7 of thinking off's 13 phantom questions and failed to answer 5.

### 8.3 Phantom answers with thinking on (13 of 720)

[LAB-LFX], [SUM-LFX], [OUT]:

- **By load** (impossible loads only): 1.00: 2 of 160, 1.02: 3 of 160, 1.05: 2 of 160, 1.10: 4 of 80, 1.25: 1 of 80, 1.50: 1 of 80. Unlike thinking off, where all 13 one-agent phantom answers sit at load 1.02, these are spread over every impossible load, including 1.25 and 1.50. No load stands out; with 13 events the load-by-load rates (1.3% to 5.0%) cannot be told apart.
- **By version:** 0 of 360 impossible questions when cued. Uncued, 12 of 180 when the capacity is stated (6.7%, 95% range 3.3% to 10.6%) and 1 of 180 when it is not (0.6%, range 0% to 1.7%) [SUM-LFX]. **Stating the capacity went with more phantom answers here, not fewer.** For thinking off the same two cells are 7 of 180 and 6 of 180 [LAB-LFX]. Why this differs is UNKNOWN. A guess, not tested: with the capacity written out, the reply may quote it without comparing it with the arrival rate. The sample is 13 events from one model; it could also be chance in where the model happened to slip.
- The 13 replies are 13 different (load, number set) pairs; no number set is wrong in two versions, unlike thinking off, where 6 sets were wrong in both uncued versions (section 4.4) [LAB-LFX].
- The printed waits run from 2.6 to 146.7 minutes [LAB-LFX]. 3 of the 13 contain a phrase from the trouble list (two at load 1.00, one at 1.10) and 10 do not; the capacity number appears in the same 3 (which tells us nothing for 1 agent, section 4.4) [LAB-LFX]. **No thinking-on reply was read, so nothing is claimed about why any of these 13 went wrong.** The cost simulation rows for these 13 are in [COST] (it now holds 18 + 13 = 31 rows) but are not summarized in this draft, and they were made with the original reader's labels.
- 0 of 360 cued impossible replies are phantom answers, as for thinking off. Only 15 of those 360 are format failures (section 8.4).

### 8.4 Replies with no answer: cap hits and other format failures

A format failure is not a phantom answer: no number was printed. It is still not a correct answer, so it is its own group and is never dropped (section 3).

- **118 of the 1,280 replies (9.2%) hit the 12,000-token cap** (`done_reason` = `length`) [RAW-T, counted Oct 17]. All 118 have an empty final reply, so none has an `ANSWER:` line, and all are format failures [LAB-LFX]. **116 are on impossible questions (116 of 720 = 16.1%) and 2 on questions that settle (both at load 0.98).** (The WORKLOG entry of Oct 17 puts all 118 under impossible; the join of [RAW-T] to [LAB-LFX] gives 116 and 2.)
- By load on impossible questions, caps / questions (rate): 1.00: 35 / 160 (21.9%), 1.02: 28 / 160 (17.5%), 1.05: 16 / 160 (10.0%), 1.10: 10 / 80 (12.5%), 1.25: 13 / 80 (16.3%), 1.50: 14 / 80 (17.5%) [RAW-T joined to LAB-LFX]. **The counts are largest at loads 1.00 to 1.05 (79 of the 118) only because those loads have twice as many questions (160 against 80).** By rate, the highest is exactly 1.00 and the rest run from 10% to 18%; cap hits are common at 1.50 too. They are not confined to loads just above the limit.
- By version on impossible questions: cap hits are 52 (uncued, capacity not stated), 49 (uncued, stated), 12 (cued, not stated) and 3 (cued, stated); format failures are 54, 52, 12 and 3 of 180 each (30.0%, 28.9%, 6.7%, 1.7%) [RAW-T joined to LAB-LFX]. Over all 320 questions of each version the failure rate is 23.8%, 28.8%, 4.1% and 2.2% [SUM-LFX, `format_failure_rate`]. **With the cue, the model gave up far less often.** Why is UNKNOWN; this draft did not read the replies.
- **The other 70 format failures are not cap hits** (65 on questions that settle, 5 on impossible ones): 61 end with `\boxed{x}` and no answer line, and 9 contain "answer:" text that the reader cannot parse (the original reader had 10; the LaTeX fix reads one of them) [THINK `think_report.py`; split recomputed Oct 17 on [RAW-T] joined to [LAB-LFX]]. On questions that settle, the format-failure rate rises with load: load 0.50: 0 of 80, 0.70: 6 of 80, 0.80: 3 of 80, 0.90: 6 of 80, 0.95: 12 of 80, 0.98: 40 of 160 [LAB-LFX].
- **How this differs from thinking off.** Thinking off had 0 format failures and 0 cap hits on the same 1-agent questions; all 37 of its format failures (main scoring) are cap hits on 4-agent questions that settle, and none of its 38 cap hits is on an impossible question (section 4.6, limitation 9). With thinking on, the cap hits move to impossible 1-agent questions (116), and a second kind of failure appears: replies that ignore the requested answer format (61 `\boxed{x}`-only).
- Cost in time: the 118 cap-hit replies took 993 s each on average (about 16.6 minutes), 32.6 hours of the 80.8 hours of reply time (section 8.6) [RAW-T].

### 8.5 False alarms

0 of 560 questions that settle got a false alarm (NONE where a number was right) [LAB-LFX], as for the other two settings in the 1-agent rows (section 4.6). At load 0.98, the closest load below the limit, 120 of 160 replies are numbers, 40 are format failures and none are flags [LAB-LFX], [OUT].

### 8.6 Speed

- Mean **227.3 s per reply** (median 122.1 s, longest 1,300.3 s), against 4.2 s for thinking off on the same 1,280 questions (about 53 times slower) [RAW-T], [LAB-LFX]. By version: uncued 304.8 s (capacity not stated) and 356.8 s (stated), cued 130.6 s and 117.0 s [SUM-LFX]. Mean 3,675 output tokens per reply; 16.2 output tokens per second overall [RAW-T: `eval_tokens`, `seconds`].
- The main run took 80.8 hours of reply time, which matches the clock span above. The plan was about 47 hours, based on the 10-question check (133 s per reply, 0 cap hits) [PREREG section 8, Oct 13]. The numbers show two sources for the gap: replies were longer on average than in the check (227 s against 133 s), and the 118 cap-hit replies alone took 32.6 hours (section 8.4). The check also found that the 16,384-token context put about 20% of the model on the processor instead of the graphics card, about 3 times slower than the 8,192 context [PREREG section 8, Oct 13 result entry]; whether the same split held for the whole run was not checked. The repeat set took 12.7 hours (152.0 s per reply) [RAW-T].

### 8.7 Against the pre-registered prediction (thinking off), for reference

[PREREG section 2] makes predictions for **thinking off**; it has no thinking-on version. In the same cell (1 agent, uncued, capacity not stated) [LAB-LFX], [OUT]:

| Load | Predicted phantom rate (thinking off) | Thinking off, result | Thinking on, result |
|---|---|---|---|
| 1.02 | more than 60% | 6 of 40 | **0 of 40** (26 flags, 14 format failures) |
| 1.00 | 35% to 65% | 0 of 40 | **0 of 40** (20 flags, 20 format failures) |
| 1.50 | under 20% | 0 of 20 | **0 of 20** (12 flags, 8 format failures) |

Thinking on does not fit the prediction either, and misses it in the same direction as thinking off: far fewer phantom answers than predicted. In this cell it had no phantom answer at all, but 14 to 20 of every 40 replies at loads 1.00 and 1.02 were not answers (format failures). So "zero phantom answers" here is not "all correct": a manager would get no number, and no warning either. The 13 thinking-on phantom answers are almost all in other cells (section 8.3).

### 8.8 Repeat set (temperature 0.7, 100 one-agent questions x 3)

Reported separately, never pooled with the main run [PREREG section 3]. Main scoring [REP: `labeled_repeats_latexfix.csv`], counted Oct 17; the 100 questions are 58 impossible and 42 that settle:

- All 3 repeats give the same label on **88 of 100 questions**; **251 of 300 replies (83.7%) match the temperature-0 label** of the same question in the main run. 5 phantom answers (of 174 replies to impossible questions, 2.9%), 0 false alarms, 11 format failures (3.7%). Check, original reader [REP: `labeled_repeats.csv`]: 87 agree, 251 match, 5 phantom answers, 0 false alarms, 13 format failures.
- For comparison, thinking off in the same repeat design: 96 of 100 agree and 293 of 300 match with the main scoring (section 6). Thinking on looks less repeatable, but this is a loose comparison: the two settings' 100 questions are different draws (the thinking-off draw includes 4-agent questions; the thinking-on draw cannot).
- **None of the 300 repeat replies hit the cap** (all `done_reason` = `stop`; longest 9,660 tokens) [RAW-T, repeats], while 7 of these same 100 questions hit the cap at temperature 0 in the main run [RAW-T]. For the 12 questions that had a format failure at temperature 0, their 36 repeat replies were 17 flags, 17 numbers and 2 format failures. A guess, not tested: the cap hits may be loops that temperature 0 falls into more easily than temperature 0.7. The data show only that the repeats did not hit the cap.
- Of the 5 phantom answers, 4 are on questions whose temperature-0 reply was a correct flag, and 1 repeats a question that was a phantom answer at temperature 0 (that question's other two repeats were correct flags). The sample is 100 questions, not weighted to resemble the main set.

### 8.9 What this section can and cannot support

- It supports: thinking on does not remove phantom answers (13 of 720, the same count as thinking off) and does not make them common; its main cost on these questions is a large share of replies with no usable answer (14.7%), concentrated where the model hits the 12,000-token cap or ignores the answer format; and it is about 53 times slower.
- It does not support: any claim about why a reply failed, any 4-agent claim, or any claim about thinking on in other models. Counts are small (13 phantom answers; cells of 20 to 40 questions), the ranges are wide, and the capacity-stated difference (12 of 180 against 1 of 180) rests on 13 events.
- The possible reading that thinking on "trades phantom answers for format failures" is only partly in the data: of thinking off's 13 phantom questions, thinking on gave 5 format failures, 7 flags and 1 phantom answer; but thinking on's own failures are mostly on questions thinking off flagged correctly (116 of 121). Treat it as a guess, not a result.

## 9. Hand-check (done by a blind Claude labeler, not by Jayden)

A hand-check tests the scoring program: someone labels a sample of replies without seeing the program's labels ("blind"), and the two sets of labels are compared.

**What was planned.** [PREREG section 4]: Jayden labels 150 randomly chosen qwen3:8b thinking-off replies (50 at load 1.00 or more, 50 at 0.95 to 1.05, 50 that settle) before seeing the program's label, and the percent agreement is reported.

**What was done instead (a deviation, approved by Jayden Oct 15, 2026).** Jayden chose not to hand-label the 150 himself and typed yes to a blind Claude labeler [PREREG section 8, Oct 15 entry; WORKLOG.md, Oct 15 entries]. The 150 are the same draw (seed 20261013, 50 per group; group A load 1.00 and up, group B 0.95 to 1.05, group C settles) [PREREG section 8; `src/handcheck.py`]. A separate Claude session read only the question and reply text in `data/processed/handcheck/sheet.html` and labeled each as NONE, NUMBER or UNCLEAR, plus whether a manager would know what to do. Its labels are in `data/processed/handcheck/labels.csv` (counts, read Oct 15: NONE 79, NUMBER 70, UNCLEAR 1; 150 rows) [WORKLOG.md, Oct 15, blind sub-session entry]. The main session then ran `handcheck.py compare`. This draft did not open the answer key file and did not re-run the comparison, so the agreement figures below are quoted from [WORKLOG.md, Oct 15, 5:36 pm entry] and [PREREG section 8, second Oct 15 entry], not recomputed here.

**Result.**

| Scoring | Agree | Group A (load 1.00+) | Group B (0.95 to 1.05) | Group C (settles) |
|---|---|---|---|---|
| Original pre-registered reader (check) | 147 of 150 = 98.0% | 50 of 50 | 50 of 50 | 47 of 50 |
| MAIN scoring (LaTeX-fix reader) | 150 of 150 | 50 of 50 | 50 of 50 | 50 of 50 |

The 3 disagreements (items 83, 115, 136) are all 4-agent questions that settle, and all three replies end in a LaTeX-wrapped answer line (`\boxed{\text{ANSWER: x minutes}}` or `\text{ANSWER: } 0.0`): the labeler read them as numbers, and the original reader called them format failures. The LaTeX-fix reader labels all three as numbers, which is where the 150 of 150 comes from (computed from `labeled_latexfix.csv` per [PREREG section 8]; not recomputed here). The per-group split of 50, 50, 50 follows from all 3 disagreements being in group C; no source lists it directly. That finding is why the LaTeX-fix reader became the main scoring (section 3). With 150 of 150 agreeing, the hand-check found no other problem with the scoring program in these 150 replies. It cannot rule one out in replies it did not sample.

**Limits, stated plainly.**
- **This is weaker evidence than a human check.** The labeler is a Claude model, and the scorer was also written by Claude (same model family), so the two can make the same mistakes. Agreement between them does not show that a person would agree.
- **Blindness is self-reported, not proven.** The labeler's own log says it never opened the answer key file. But the key file's last-access time (5:33 pm, Oct 15) falls inside the labeler's working window, and the cause is unknown; another session's file scan is possible [WORKLOG.md, Oct 15, 5:36 pm entry].
- 150 replies out of 2,560 is a sample, and it covers only qwen3:8b with thinking off; no gpt-oss:20b replies were hand-checked [`src/handcheck.py`, which draws from `data/raw/main/qwen3-8b-nothink.jsonl` only].
- Jayden's optional spot-check (he labels a random 20 of the 150 himself) is **still open**; it is not a blocker [PREREG section 8].

## 10. Related work

Source table with links and dates: `writeup/prior-work.md` (pages opened Oct 17, 2026 by a fetch tool that summarizes them: abstracts and landing pages, not the full papers; Jayden still re-opens each before it is cited; **not yet reviewed by Jayden**).

- **Models answering questions that cannot be answered.** AbstentionBench (Kirichenko et al., arXiv 2506.09038, 2025) tests whether LLMs decline to answer across 20 datasets and reports that declining to answer when they should is an unsolved problem across 20 frontier models; reasoning fine-tuning lowered abstention by 24% on average, and a careful system prompt helped. UMWP (Sun et al., arXiv 2403.03558, 2024) is a set of 5,200 unanswerable math word problems for measuring made-up answers. Liu et al. (arXiv 2508.18760, 2025) find that large reasoning models often fail to abstain on unanswerable questions although they can recognize the flaw internally, and Du and Hu (arXiv 2608.29109, 2026) report a similar recognition-without-refusal pattern for impossible math and code prompts. "Recognizing Limits" (Zhang, Xu, Cai, Findings of EMNLP 2025) builds a benchmark of infeasible tasks and tests fine-tuning for refusal. [PW]
- **Operations-research settings.** ORLoopBench (Ao, Simchi-Levi, Wang, arXiv 2601.21008, 2026) is about repairing infeasible optimization models in a solver loop, and Wang et al. (arXiv 2604.01455, 2026) train a model to judge when a combinatorial instance has no valid solution. Kumar, Peng, Wu and Zeevi (arXiv 2506.23924, 2025) evaluate LLMs on stochastic-modeling problems; their abstract does not mention unstable queues or unanswerable cases. [PW]
- **The rule behind our answer key.** An M/M/1 queue (one agent, random arrivals, random service times) has a stationary distribution, meaning it settles into a steady long-run pattern, only when arrivals are slower than service; otherwise the line grows without bound (Wikipedia, "M/M/1 queue", opened Oct 17, 2026). That load exactly 1.00 has no long-run average wait when arrivals and service are random is the project's own reasoning (`PLAN.md` section 2); the Wikipedia page does not discuss equality, so a textbook citation is **UNVERIFIED** and still to be found.
- **What we did not find.** In three short web searches (Oct 17, 2026) we did not find a study that gives LLMs waiting-line questions whose load is at or above capacity and varies the load across the 1.00 boundary, the number of servers, a feasibility cue and a stated-capacity control. This is "not found in a short search", not a claim that none exists; a fuller literature search is **UNVERIFIED** and should be done before any claim of novelty.

[PW] = `writeup/prior-work.md`, pulled Oct 17, 2026.

## 11. What is still UNVERIFIED or waiting on Jayden

Waiting on Jayden:
1. (Done Oct 26: he read the short version and sections 4.1, 4.2, 7, 9 and 11 and approved them as written.) The other sections are not reviewed by him.
2. Optional: label a random 20 of the 150 hand-check replies himself (the blind Claude labeler did all 150; section 9).
3. (Done Oct 15: he decided the LaTeX question; the LaTeX-fix reader is the main scoring and the original reader is the labeled check, section 3.) He still has to review the wording of that section.
4. First-results review (the Oct 13 draft is superseded by this one for the numbers here, but he has not read either).
5. Thinking-on run: finished, copied back, scored and written up as section 8 (Oct 17). He has to review it, decide whether any thinking-on replies get a hand-check (it needs a `PREREG.md` entry first), and decide whether the cost simulation is re-made with the main-scoring labels.
6. Say whether to publish.

UNVERIFIED or not re-run by this draft:
- Section 10 (related work): sources were read as abstracts and landing pages through a summarizing fetch tool on Oct 17, not as full papers; the search for a closer match was three short searches; Jayden has not re-opened any source.
- The answer-key check (280 of 280) was redone on Oct 15 by the audit session on the saved key values, not by re-running `answer_key.py`; Jayden has not reviewed that check.
- That the other 10 original one-agent phantom replies, the 13th one-agent reply (`a1_L1.02_s28_UK`, not read at all) and the other 5 four-agent ones fit the "division slip" and "invented approximation" descriptions (3 replies were read in full: 2 and 1).
- The hand-check agreement figures (147 of 150, 150 of 150) are quoted from WORKLOG and PREREG, not recomputed here (that needs the answer key file, which was not opened). Blindness of the labeler is self-reported. The cost simulation (section 4.5) was not re-made for the 19th phantom answer.
- The charts in `figures/`.
- Section 8 (thinking on): every number was recounted Oct 17 from the scored files, but no thinking-on reply was read and none was hand-checked, so why a reply failed or went wrong is UNVERIFIED. The two guesses in sections 8.3 and 8.8 (capacity written out; loops at temperature 0) are untested. The effect of the 16,384 context on speed over the whole run was not checked (only in the 10-question check). The WORKLOG Oct 17 sentence "118 replies hit the cap" under impossible questions is 116 impossible plus 2 settling by this draft's join. The cost simulation for the 13 thinking-on phantom answers was not summarized or re-made with main-scoring labels.
- The model licenses (Qwen3 and gpt-oss licenses are UNVERIFIED in `data/raw/SOURCES.md`).
- Any explanation of why the models behave this way. The "slip" description is a reading of a few replies, not a tested mechanism.
- Whether the PC vs Mac difference affects any result.
- Whether the study date and model download dates in `data/raw/SOURCES.md` are complete (the original pull date of the models is not logged there).
