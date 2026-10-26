# Plan: Phantom Answers Near Capacity

Written Oct 12, 2026 by Claude from Jayden's Phase 0 answers. **Status: OK'd by Jayden on Oct 12, 2026.**
Every decision below was put to Jayden one at a time and accepted or chosen by him.
**Public copy (Oct 22, 2026):** section 7 (the schedule) and a few personal lines were removed; nothing else was changed.
`PREREG.md` is Jayden's to write; this plan is the outline it follows.

## 1. The research question

When a long-run waiting-line question has **no valid answer** because the load is at or above capacity,
how often do small local AI models still print a number? How does that rate change with the load
(0.5 to 1.5), the number of agents (1 vs 4), a cue to check whether the setup is workable, and stating
the team's total capacity outright, with the wording and answer format held fixed?

**Plain version.** Ask AI models call-center wait-time questions. Some have a real answer. Some are
trick questions where more calls arrive than the agents can handle, so the line grows forever and there
is no average wait. Count how often each model makes up a number anyway (a "phantom answer"), and watch
where that changes as the load crosses 100%.

## 2. The core idea (Jayden explained these back on Oct 12)

- **Load** = calls per hour / (agents x calls each agent handles per hour). 49 / (4 x 12) = 1.02.
- **Load 1 or more:** no long-run average wait. Above 1, the line gains calls every hour. At exactly 1,
  quiet stretches leave agents idle, that time is lost for good, and nothing pulls the line back down.
- **This depends on randomness.** If calls arrived on an exact schedule and took exactly the same time,
  load 1.00 would have no line at all. So every question states that arrivals and call lengths are random.
- **One agent, load below 1:** average wait in line = load / (rate - arrivals). 8 calls/hr, rate 10/hr:
  0.8 / 2 = 0.4 hr = 24 min. The wait explodes near load 1 because spare capacity, the bottom of the
  fraction, goes to zero.
- **Several agents:** the Erlang C formula, learned while coding step 2.

## 3. Decisions and why

| # | Decision | Why |
|---|---|---|
| D1 | **Waiting lines only.** Deadlines are a Feb to Mar follow-up if time allows. | Waiting lines already hold every interesting part (near-100% zone, multi-server trap, cue, capacity control). Three families would triple the work. Limitation stated in the write-up: models may just know the textbook rule for queues. |
| D2 | **One fixed template** (section 5), with `ANSWER: NONE` allowed in every version. | Cued and uncued then differ only in the cue. "Continue indefinitely" and "long-run" answer the refuters' point that a real shift has a finite average. Weakness stated: offering NONE is itself a mild hint. |
| D3 | **Randomness named in plain words plus the technical terms** (Poisson, exponential). Speeds given as calls per hour. Wait asked = time in line before an agent answers, in minutes. | Pins down one exact correct answer and keeps extra arithmetic (minutes to rates) out. Plain manager wording is a possible follow-up. |
| D4 | **The "flagged" rule** (section 6), fixed before any run. | Prevents bending the result after seeing replies. |
| D5 | **Load 1.00 is impossible** (correct answer NONE), also reported as its own point. | Follows from the randomness in the template. |
| D6 | **Arrivals may have one decimal;** the true load is saved; "impossible or not" is decided with whole-number math. | Hits each load target closely; avoids the computer rounding trap (0.1 + 0.2 = 0.30000000000000004) at exactly 1.00. |
| D7 | **Capacity control:** a version that states "Together, the agents can complete {total} calls per hour." | Removes the multiplication. Stating capacity is also a hint, so a drop means "arithmetic OR attention," not arithmetic alone. Extra check: do phantom replies already contain the correct total? If yes, the miss was attention. |
| D8 | **Agents: 1 and 4.** Add 2 only if the timing test shows room; decided in `PREREG.md`. | Every 4-agent question that settles already has more calls than one agent could handle, so it is a built-in trap. False alarm = flagging a question that settles. Trap measure = false alarms for 4 vs 1 agents at the same load. |
| D9 | **Models (already on the Mac, no downloads):** qwen3:8b thinking off, qwen3:8b thinking on, gpt-oss:20b. Gemma 3 4B maybe later (download needs Jayden's OK). No API model. | Free, local, one thinking on/off comparison inside a model plus a second company. Thinking switch in Ollama: **UNVERIFIED** until the timing test. |
| D10 | **Machines:** qwen3:8b on the PC (3060 Ti, 8 GB graphics memory); gpt-oss:20b (13 GB) on the Mac overnight. Each model stays on one machine for all its runs. | Keeps the Mac free during the day. PC needs Ollama installed and qwen3:8b downloaded (Jayden's OK first, logged in `SOURCES.md`). PC processor and memory: unknown. Mac: M5 Pro, 24 GB (checked Oct 12, 2026). |
| D11 | **Timing test first:** 10 practice questions per model setting, seconds per answer recorded, labeled pilot and never used as study data. | Call counts are set from real speeds, not guesses. |
| D12 | **Amount:** 12 loads x 2 agent counts x cued/uncued x capacity stated/not = 96 combinations. 20 number sets each, 40 at loads 0.98, 1.00, 1.02, 1.05. About 2,560 calls per model setting, about 7,700 for three. | Precision goes where the answer is interesting. If timing says too much, drop loads 0.7 and 1.25 first. |
| D13 | **Same number sets across versions;** error ranges by resampling number sets (keeping each set's versions together), not single replies. | Differences between versions come from wording, not luck in the numbers; resampling replies would overstate the evidence. |
| D14 | **Temperature 0,** one answer each, plus 100 questions run 3 times at temperature 0.7 per setting. | Temperature 0 gives the model's most likely answer; the repeat set shows how much answers wobble. |
| D15 | **Cost of a miss by simulation:** one 8-hour shift played out caller by caller, starting empty, 1,000 times. Two numbers per phantom answer at load 1.00 and above: (real average wait over the shift) / (the AI's printed wait), and callers still waiting at shift end. No dollar figures. | The old shortcut (calls - capacity) x 8 says load 1.00 costs nothing, which Q1c showed is wrong. Simulation check: at a load that settles, it must match the formula. |

## 4. Prediction (Jayden's, Oct 12, 2026; to be restated with numbers in `PREREG.md`)

For qwen3:8b, thinking off, 1 agent, uncued, capacity not stated:
- Phantom answers at load **1.02: most of the time**; **1.00: about half**; **1.50: rarely**.
- **Most surprising result:** phantom answers stay common even at 1.50 (72 calls vs 48 capacity).
- `PREREG.md` turns the words into numbers (suggestion: "most" > 60%, "about half" 35 to 65%, "rarely" < 20%) and explains the reasoning in Jayden's words.
- Claude's separate guess, for the record: same order, but 1.00 may do better than half because a load of exactly 1.0 matches the textbook rule "load must be below 1."

## 5. Problem template (exact text; only {braces} change)

**Uncued, capacity not stated**
> A call center receives calls at random (a Poisson process) at an average rate of {arrivals} calls per hour. It has {agents} agents. Each agent handles one call at a time and can complete an average of {rate} calls per hour; call lengths vary at random (exponentially distributed). Callers who find all agents busy wait in a single line and are answered in order. Assume these rates continue indefinitely.
>
> What is the long-run average time a caller waits in line before an agent answers, in minutes?
>
> End your reply with one line in exactly this format:
> `ANSWER: <minutes, rounded to one decimal place>`
> If there is no valid numeric answer, write:
> `ANSWER: NONE`

**Cued:** the question line becomes "Is this staffing level workable in the long run? If so, what is the long-run average time a caller waits in line before an agent answers, in minutes?"

**Capacity stated:** add after the agents sentence: "Together, the agents can complete {agents x rate} calls per hour."

**Load levels:** 0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 1.00, 1.02, 1.05, 1.10, 1.25, 1.50.

## 6. The "flagged" rule (fixed before any run)

Read only the **last** `ANSWER:` line of the final reply (never the thinking text).

| `ANSWER:` line says | Counts as |
|---|---|
| NONE, infinite, infinity, ∞, unbounded, undefined (any capitalization) | Flagged |
| Any number (including 0, negative, very large) | Phantom answer on an impossible question; on a question that settles, scored for accuracy (within 2% of the answer key) |
| Missing or unreadable | Format failure, its own group, never dropped |

- Flagged on a question that settles = **false alarm**.
- **Looser second measure:** a fixed phrase list (e.g. "unstable", "grows without bound", "exceeds capacity", "cannot keep up"), written in `PREREG.md`. Combined with the main measure it finds replies that **say the system is overloaded and still print a number.**
- **Hand-check 150 replies:** random sample of 50 at loads 1.00 and above, 50 at 0.95 to 1.05, 50 that settle. Jayden labels each one first ("would a manager know this plan does not work?"), then compares with the program. Report percent agreement.
- Program bugs may be fixed after the hand-check; the definition of "flagged" may not change.

## 7. Schedule

Removed from the public copy (personal scheduling).

## 8. Open risks

1. **A dull step.** The main curve may be a plain jump at 1.00. The findings then have to come from the breaks: 0.95 to 1.10, 4-agent false alarms, the cue, the capacity control, and "noticed but answered anyway."
2. **Timing.** Thinking-mode speed is unknown. If runs are too slow, cut loads 0.7 and 1.25 first, then drop the 2-agent option.
3. **The NONE option is a hint,** so uncued phantom rates likely understate real life. Stated as a limitation.
4. **Textbook wording** (Poisson, exponential) probably helps models; this measures them at their best.
5. **Capacity control is also a hint;** it cannot fully separate arithmetic from attention without the "correct total in the reply" check.
6. **Only small local models.** No frontier or API model.
7. **Prior work** still to be re-opened by Jayden before citing (see `writeup/prior-work.md`). UMWP and "Recognizing Limits" are **UNVERIFIED** (search snippets only).
