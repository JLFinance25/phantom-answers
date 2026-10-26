# Phantom Answers Near Capacity

**Status: work in progress. Draft, not peer-reviewed.** All three planned model runs are finished and scored, but the numbers could still change.

## The question

Picture a call center where more calls arrive each hour than the agents can answer. The line of waiting callers grows forever, so a "long-run average wait" does not exist, and the right answer to "how long does a caller wait?" is **none**. If you ask a language model anyway, does it say so, or does it print a confident number? I call that confident number a **phantom answer**: a wait time for a line that never settles.

The key quantity is the **load**: calls arriving per hour divided by the calls per hour the whole team can handle. Below 1.00 (100%) the line settles and has a real average wait. At 1.00 or above it never settles. The study asks how often models give phantom answers as the load crosses that line.

Example: 49 calls an hour, and 4 agents who each handle 12 an hour, so the team handles 48. The load is 49 / 48 = 1.02. The line grows without limit, and the correct answer is `NONE`.

## What I did

- **One fixed question template (my design).** Calls arrive at random (the textbook "Poisson" pattern), call lengths are random (the textbook "exponential" pattern), and the question says to "assume these rates continue indefinitely". The reply must end with `ANSWER: <minutes>` or `ANSWER: NONE`.
- **Four dials.** 12 load levels from 0.5 to 1.5; 1 or 4 agents; with or without a **cue** (the extra sentence "Is this staffing level workable in the long run?"); and with or without the team's total capacity written out in the question. That makes 2,560 questions per model.
- **Correct answers come from exact formulas**, not from another AI: the standard one-agent waiting-line formula, and the Erlang C formula (the standard formula for a line served by several agents) for 4 agents. The answer key was checked a second way.
- **Rules written down first.** The scoring rule, my predictions and what each result would mean were written down and committed to the project's history (`PREREG.md`, short for pre-registration, first committed Oct 12, 2026) **before** any study run; I approved that file on Oct 12. I made one scoring change afterwards, and it is logged in `PREREG.md` section 8 (see "First results"). See also the history note at the end of this page.
- **Models run locally** on my own computers, at temperature 0 (a setting that makes the model pick its most likely wording every time, instead of varying it): qwen3:8b with thinking off, gpt-oss:20b, and qwen3:8b with thinking on (one-agent questions only). "Thinking on" means the model writes out hidden working before its final reply.

## First results (two finished runs)

An "impossible question" here means one whose load is 1.00 or more, so the only correct answer is NONE.

| Model | Impossible questions | Phantom answers |
|---|---|---|
| gpt-oss:20b | 1,440 | 0 |
| qwen3:8b, thinking off | 1,440 | 19 (1.3%) |

- **My pre-registered prediction was wrong.** It said qwen3:8b would give a number most of the time at load 1.02, and about half the time at load 1.00 (for 1 agent, no cue, capacity not stated). The result was 6 of 40 (15%) at 1.02 and 0 of 40 at 1.00.
- **Both models switch from "give a number" to "say NONE" between loads 0.98 and 1.00,** and almost never get it wrong after that. So the headline is a plain step. The interesting findings are in the few places where the step breaks.
- **The cue removed every phantom answer.** All 19 come from qwen3:8b with no cue; with the cue there were 0 of 720 phantom answers on impossible questions.
- **Where the 19 are.** 13 of the 19 are at load 1.02. At least 2 of the ones that were read look like an arithmetic slip: the model divides wrongly and gets a load just under 1. The 13th was not read. The other 6 are at load exactly 1.00 with 4 agents: there the model says the usual formula "is not valid", then makes up an approximation and prints about 1.4 minutes.
- **What a phantom answer would cost.** A computer simulation of an 8-hour shift puts the real average wait for those six 4-agent cases at about 17 minutes. For 12 of the one-agent phantom answers it is 24.6 to 38.4 minutes; the 13th was not simulated.
- **A separate accuracy result.** On questions that do have an answer, both models are good with 1 agent (98% to 100% accurate) and weak with 4 agents (qwen3:8b 2%, gpt-oss:20b 22.5%). That is about getting the arithmetic right, not about phantom answers.
- **Which scoring is the main one.** The scoring program reads the reply's last `ANSWER:` line. Some qwen3:8b replies wrapped that line in LaTeX (a math typesetting code, for example `\boxed{ANSWER: 0.2}`), and the original program could not read them, so it counted them as **format failures** (replies with no readable answer). On Oct 15 the main scoring was changed to also read LaTeX-wrapped answer lines. I decided this after seeing the data, so it is a logged deviation from the plan (`PREREG.md` section 8). It turns 60 qwen3:8b format failures into readable answers: one becomes a 19th phantom answer and one a correct NONE. The original pre-registered reader gave 18 phantom answers and is kept as a labeled check (`labeled.csv`, `summary.csv`; the main-scoring files end in `_latexfix`). gpt-oss:20b is the same under both.
- **Hand-check of the scoring program.** 150 randomly drawn qwen3:8b replies were labeled "blind" (without seeing the program's labels) by a separate AI labeler, **not by me or any other person**. I chose that. It is weaker evidence, because the labeler and the scoring program come from the same model family, and its blindness is self-reported: the answer key file's last-access time fell inside the labeler's working window, and the cause is unknown. With the original reader 147 of 150 agree (98.0%). The 3 disagreements are LaTeX-wrapped answer lines, and with the main scoring all 150 agree. My own 20-reply spot-check is still open.

## Thinking on (qwen3:8b, one-agent questions only; first results, not hand-checked; finished Oct 17)

This run covers only the 1,280 one-agent questions, because in a pilot test most 4-agent replies hit the **token cap** (the most words the model is allowed to write before it is cut off). Its cap was 12,000 tokens. So it is compared with the other two settings on those same 1,280 questions. Counted Oct 17, 2026 from `data/processed/labeled_latexfix.csv` and the raw replies; no reply was read, and I have not reviewed this section.

- **Phantom answers: 13 of 720 impossible questions (1.8%), the same count as thinking off, but mostly on different questions.** Only one question is a phantom answer in both settings. The 13 are spread over every impossible load from 1.00 to 1.50, not bunched at 1.02. With the cue: 0 of 360. Without the cue: 12 of 180 when the capacity is stated, and 1 of 180 when it is not. So writing out the capacity went with *more* phantom answers here; why is unknown.
- **The big difference is replies with no answer: 188 of 1,280 (14.7%),** against 0 for both other settings. 118 replies ran out the 12,000-token cap with no answer (116 on impossible questions, 2 on questions that settle). Another 70 ended without a readable answer line, mostly `\boxed{x}` alone. A reply with no answer is not a phantom answer (no number was printed), but it is not a correct answer either. These failures were far more common without the cue (about 29% of uncued impossible questions, against 4% cued).
- **No false alarms** (a false alarm is saying NONE when a real answer exists): 0 of 560 questions that settle. Every number it printed on those was accurate (493 of 493). Its lower accuracy (88%, against 98% for thinking off) is entirely the 67 replies with no answer.
- **About 53 times slower:** 227 seconds per reply on average, against 4.2 for thinking off; the run took 80.8 hours of reply time. In the repeat set (temperature 0.7, which lets the wording vary; 100 questions asked 3 times each), all three repeats agreed for 88 of 100 questions, and none of the 300 replies hit the cap.
- **No prediction was made for thinking on.** The pre-registered prediction was written for thinking off only. In the same cell (1 agent, uncued, capacity not stated), thinking on printed 0 phantom answers at loads 1.00, 1.02 and 1.50, but 35% to 50% of the replies in those three cells were no-answer replies instead.

Details, sources and what is unchecked: section 8 of the draft report.

Full tables, sources for every number, limitations and the list of what is still unchecked: `writeup/draft-report-2026-10-15.md`. An earlier, shorter draft is `writeup/first-results-2026-10-13.md` (superseded where the two differ; the new draft corrects one miscount).

## Limits to keep in mind

- Offering `ANSWER: NONE` in every question is itself a hint, and the textbook wording (Poisson, exponential) probably helps the models. Real-world phantom rates are likely higher than these.
- Only small local models, one problem family (waiting lines), one wording.
- 20 to 40 sets of numbers per cell, so rates near zero have wide uncertainty.
- 19 phantom answers is a thin base for conclusions.
- The hand-check was done by an AI labeler, not a person, and covers thinking off only. The thinking-on run covers one-agent questions only and is not hand-checked.

## What is in this repo

```
PREREG.md           pre-registration: question, predictions, scoring rule, analysis, later changes
WORKLOG.md          work log, by date
src/                question maker, answer key, model runner, reply scorer, analysis, cost simulation
data/raw/           saved model replies (never edited by hand) and SOURCES.md
data/processed/     questions.csv, scored replies, summary tables
figures/            charts
writeup/            draft report, earlier first-results draft, number audit, prior-work list, thinking-on runbook
prereg/             PREREG.md as first committed (see the history note)
```

To re-run the scoring: `python3 src/parse_replies.py --test` (20 hand-made test replies), then `python3 src/parse_replies.py` and `python3 src/analyze.py`. These need Python 3 with numpy, pandas and matplotlib (not tested from a clean install). Re-running overwrites the tables in `data/processed/` and `figures/`. Model runs (`src/run_models.py`) need Ollama (a program that runs language models on your own computer) and the exact model files listed in `PREREG.md`; running them is not needed to check the scoring.

## Data and license

All questions are generated by code from fixed seeds (starting values for the random-number generator, so the same questions come out every time); there is no outside dataset. Model downloads are logged in `data/raw/SOURCES.md` (model license details there are still marked unverified). Reference formulas: the standard M/M/1 (one agent) and M/M/c (several agents, Erlang C) waiting-line results. A short related-work section is in section 10 of the draft report; it was written from abstracts and landing pages only, and I have not yet re-opened those sources.

License: MIT for this repository's code and text (see `LICENSE`). It does not cover the Qwen3 or gpt-oss models themselves, which are not included here.

## History note (read this if you are checking the pre-registration date)

This repository is a **single-commit copy**, made on Oct 22, 2026, of a private development repository. The copy has one commit, so its own history cannot show *when* `PREREG.md` was written. In the private repository, `PREREG.md` was first committed on Oct 12, 2026 at 4:10 pm (commit `caf71ed`) and the study code at 4:12 pm (commit `3ff3c21`); the first study reply was saved at 6:08 pm that day (the `time` field of `data/raw/main/qwen3-8b-nothink.jsonl`). Those commit times are from the author's computer clock, with no outside timestamp, so treat them as the project's own record, not independent proof.

- `prereg/PREREG-as-first-committed-2026-10-12.md` is the file exactly as first committed (SHA-256 `b513ac17391d2c27b4b4abbca4c2ff19056fcf184151618b4c4f986a9c1f454d`; git blob `b309a4b4ab3ebd08f5372f4dbec5f2cc2ce1992c`). `PREREG.md` is the later version with the dated changes in section 8.
- Left out of this copy: private working notes, run logs that contain machine paths (`data/raw/main/console*.log`, `data/raw/pilot/console*.log`), the staging file for pre-registration entries, and the original working log (replaced by the trimmed `WORKLOG.md`).
- Edited in this copy only for privacy: `PLAN.md` (the schedule in section 7 and a few personal lines removed), `data/raw/SOURCES.md`, `writeup/thinking-on-scoring-runbook.md` and `writeup/prior-work.md` (a machine path and pointers to private files replaced), `writeup/audit-2026-10-15.md` (one table row's text), and the last waiting-on item in `writeup/draft-report-2026-10-15.md`. No result, number or scoring rule was changed. Also edited in this copy, for wording only: the AI-use wording (now one acknowledgments section at the end), and the first lines of `src/run_models.py` (the models were run by Claude under my direction).

## Acknowledgments and AI use

I chose the question and designed the study: the question template, the rule for what counts as a flagged answer, the 1-agent and 4-agent setups, the three models, the number of questions per setting and the two cost-of-a-miss numbers. I wrote my prediction before any run, approved every model run, and made the one scoring change. Claude (Anthropic's AI assistant) wrote the code and drafted this text, and ran the models under my direction. On Oct 26, 2026 I read and approved this README and the report's short version and sections 4.1, 4.2, 7, 9 and 11. The numbers were checked against the result files by Claude, not re-audited line by line by me.
