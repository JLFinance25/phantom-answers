# Runbook: scoring the qwen3:8b thinking-on run

Written by Claude (Oct 15, 2026) at Jayden's request; **not yet reviewed by Jayden.**
Setting name: `qwen3-8b-think`. Questions: the 1,280 one-agent questions only (PREREG section 8, Oct 13 entry).
Scoring rules are the pre-registered ones (PREREG section 4); nothing below changes how any reply is scored.

**How this was tested:** every command below was run end to end in a scratch copy of the project on
**fake** thinking-on replies (1,280 main + 300 repeat records in the real file format, with deliberate cap hits,
`\boxed{x}`-only replies and LaTeX-wrapped answer lines). The two finished real runs were copied into the scratch
copy as read-only inputs. No real thinking-on reply was read and no model was run. The numbers in this runbook
that come from that test (marked FAKE) mean nothing about the study.

## 0. Before you start (the main session does this, not this runbook)

1. Job #13 is finished: the main run (1,280 replies) **and** the repeat set (300 replies) are both done. Do not
   copy a file that is still being written (a half-written last line breaks the reader).
2. Copy both files back from the PC (over SSH) into exactly these paths:
   - `data/raw/main/qwen3-8b-think.jsonl`
   - `data/raw/repeats/qwen3-8b-think.jsonl`

   (`run_models.py` writes them under these names on the PC, relative to its project folder
   `<project folder on the PC>`. The exact PC paths are UNVERIFIED; I did not touch the PC.)
   Compare SHA-256 on both ends, log the copy in `data/raw/SOURCES.md`, and never edit these files.
3. Scoring reads **every** `.jsonl` in `data/raw/main/`, so no other file may sit in that folder, and the
   file name does not matter, only the `setting` field inside each record.

## 1. Commands, in order

Run from the project folder: `cd ~/Documents/Research/phantom-answers`

```bash
python3 src/parse_replies.py --test
```
Expect `20/20 test replies labeled correctly`.

```bash
python3 src/parse_replies.py
python3 src/parse_replies.py --latex-fix
python3 src/parse_replies.py --repeats
python3 src/parse_replies.py --repeats --latex-fix
```
Expect `labeled 6400 replies` for the first two (2,560 + 2,560 + 1,280) and `labeled 900 replies` for the last
two (300 x 3 settings). The first one is the pre-registered scoring; `--latex-fix` is the labeled-exploratory one.

```bash
python3 src/analyze.py
python3 src/analyze.py --tag _latexfix
python3 src/simulate.py
python3 src/think_report.py
```
`think_report.py` ends with `COMPLETENESS CHECKS: all passed` (exit code 0) or `FAILED` (exit code 1). If it says
FAILED, stop and look before using any number.

Last, check that the new run only **added** rows and did not change the two finished runs:

```bash
git diff --numstat -- data/processed
```
Expect 0 in the "deleted" column for `labeled.csv`, `summary.csv`, `outcome_shares.csv`, `multi_server_trap.csv`
and `miss_costs.csv`. (In the FAKE test: 0 lines changed, 1,280 / 4 / 48 / 4 / 108 lines added.) The existing
`figures/*.png` will be redrawn: the bootstrap error bars on the older panels can shift very slightly because the
random-number stream now has more draws before the chart (the scores and tables are unaffected).

## 2. What each output is

| File | What it is | Pre-registered? |
|---|---|---|
| `data/processed/labeled.csv` | one row per reply (all 3 settings), label, outcome, accurate, mentions_trouble, capacity_in_reply | yes |
| `data/processed/labeled_latexfix.csv` | same, also reading LaTeX-wrapped ANSWER lines | **exploratory** |
| `data/processed/labeled_repeats.csv`, `labeled_repeats_latexfix.csv` | same for the repeat sets, with a `rep` column | yes / exploratory |
| `data/processed/outcome_shares.csv` (+ `_latexfix`) | outcome shares per setting x agents x cue x capacity x load | yes / exploratory |
| `data/processed/summary.csv` (+ `_latexfix`) | phantom rate, false-alarm rate, switch point (each with 95% bootstrap range), accuracy, format-failure rate, noticed-but-answered, capacity-in-reply, mean seconds | yes / exploratory |
| `data/processed/multi_server_trap.csv` (+ `_latexfix`) | false alarms with 4 agents minus 1 agent. **The thinking-on rows will say `NaN` for 4 agents and for the difference: it has no 4-agent questions.** | yes / exploratory |
| `data/processed/miss_costs.csv` | cost simulation for every phantom answer (all settings) | yes |
| `figures/flag_rate_vs_load.png`, `figures/number_rate_vs_load.png` (+ `_latexfix`) | charts; thinking-on panel has one line (1 agent) | yes / exploratory |
| `data/processed/think_vs_others_1agent.csv` | **new.** 1-agent questions only, one row per setting, plain counts (phantom, correct flag, false alarm, accurate, format failures), plus a printed nothink-vs-think paired table | descriptive |
| `data/processed/repeats_agreement.csv` | **new.** per setting: questions where all 3 repeats agree, replies matching the temperature-0 label, phantoms, false alarms, format failures | descriptive |

## 3. How to read the thinking-on results (PREREG section 4 and the Oct 13 entry)

- **Compare with thinking off using 1-agent rows only.** In `summary.csv`, take the rows with `agents == 1` for
  `qwen3-8b-nothink` and `qwen3-8b-think` (summary is already split by agents, so nothing is pooled across 1 and 4).
  `think_vs_others_1agent.csv` gives the same comparison as counts on the identical 1,280 questions. Never put
  thinking-on next to the thinking-off 4-agent rows or the pooled trap table. State the missing 4-agent result
  as a limitation in the write-up.
- **Format failures are their own group and are large for this setting** (never dropped). They come from three
  sources, all counted as failures under section 4, and `think_report.py` prints the split:
  1. hit the 12,000-token cap with no `ANSWER:` line (`done_reason` = `length`, usually an empty reply);
  2. ended with `\boxed{x}` and no `ANSWER:` line;
  3. an `ANSWER:` line the reader cannot parse (the exploratory `--latex-fix` run rescues LaTeX-wrapped ones).

  A reply that hit the cap **but** has a readable `ANSWER:` line is scored normally, as PREREG says ("hits the
  cap without an ANSWER line").
- **Charts:** `number_rate_vs_load.png` counts a format failure as "not a number", so the thinking-on line will sag
  below 1.00 where the answer should be a number, only because of format failures. Read it next to
  `outcome_shares.csv` (the `format_failure` column), not alone.
- **Repeat set:** 100 one-agent questions x 3 at temperature 0.7, reported separately, never pooled with the main run.
- **Hand-check:** `src/handcheck.py` is hard-wired to the thinking-off file (`REPLIES`, line 36), as PREREG section 4
  describes, so no hand-check sheet exists for thinking-on. This runbook does not change that. Whether to hand-check
  a sample of thinking-on replies is Jayden's decision (it would need a new PREREG entry first).
- Every number in a write-up from this run still needs its source file and date (Rule 2). Nothing here has been
  checked by Jayden yet: label results UNVERIFIED until he reviews.

## 4. Gaps found, and what was done

| # | Gap | What was done |
|---|---|---|
| 1 | **No committed command scored the repeat sets.** `parse_replies.py` only read `data/raw/main/`; the Oct 15 draft's repeat numbers came from an ad-hoc run. | Added `--repeats` to `parse_replies.py` (new option, defaults unchanged) and `src/think_report.py` (new file). Reproduced the draft's repeat numbers for the finished runs exactly: qwen3:8b thinking off 91 of 100 questions agree, 280 of 300 match temperature 0, 2 phantom, 2 false alarm, 6 format failures; gpt-oss:20b 100 of 100 and 300 of 300. |
| 2 | No check that the run is complete (1,280 distinct questions, no duplicates, only 1-agent, the pre-registered settings, the repeat set = the 100 questions `run_models.py --agents 1 --repeats` draws). | `think_report.py` checks all of these and exits 1 on failure (tested with a truncated file plus a duplicate). |
| 3 | Cap hits (`done_reason`) are not in `labeled.csv`, so cap hits cannot be counted from the scored file. | `think_report.py` counts them from the raw file and splits the format failures by cause. `labeled.csv` columns left as they were. |
| 4 | No ready side-by-side of thinking on vs off on the same 1-agent questions. | `think_vs_others_1agent.csv` (plain counts, no error ranges; use `summary.csv` for the bootstrap ranges). |
| 5 | `analyze.py` draws one shared random stream; new setting sorts last (`qwen3-8b-think` after `qwen3-8b-nothink`), so earlier tables did not change (checked). Chart error bars may move slightly. | Nothing to fix; noted above. If a setting ever sorted earlier, older bootstrap ranges would shift. |
| 6 | `handcheck.py` covers thinking-off only. | Left as is (see section 3). |

Checked and **no change needed:** empty 4-agent groups (`analyze.py` simply has no such rows; the trap table gives `NaN`,
the chart draws one line); comparisons restricted to 1-agent (summary is split by agents); repeat draw from 1-agent
questions only (`run_models.py` already does this); cap hits and `\boxed{x}`-only replies already come out as
format failures; `simulate.py` prices thinking-on phantoms like any other.

## 5. FAKE-data test results (not study results)

Fake main file: 1,280 records, 35 cap hits, 133 plain `\boxed{x}`-only replies, 176 LaTeX-wrapped answer lines
(`\boxed{ANSWER: x}`). All of them scored `format_failure` in the default scoring (344 in total); with
`--latex-fix` the 176 LaTeX-wrapped ones are read, leaving 168. The 1,280 rows split into 720 impossible and 560 that settle,
as in the real question set. `summary.csv`, `outcome_shares.csv`, the trap table, `miss_costs.csv` and both charts
were produced without errors; the two finished runs' rows were identical before and after.
