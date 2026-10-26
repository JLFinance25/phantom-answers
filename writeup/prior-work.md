# Prior work check (Claude, Oct 17, 2026) — not yet re-opened by Jayden

Drafted with Claude (AI); directed by Jayden Ling. **Not yet reviewed by Jayden.**

How this was done: on Oct 17, 2026 Claude opened each page below with a fetch tool (arXiv abstract pages, the
ACL Anthology page, Wikipedia) and a few web searches. The fetch tool summarizes the page, so this is a read of
abstracts and landing pages, **not of the full papers**. Jayden still re-opens every source before it is cited
(project rule: every number and source is traced before it is cited). "Pulled" = date the page was opened.

| # | Source | What it is (from the page) | Pulled | Status |
|---|---|---|---|---|
| 1 | Kirichenko, Ibrahim, Chaudhuri, Bell, **AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions**, arXiv 2506.09038 (v1 Jun 10, 2025). https://arxiv.org/abs/2506.09038 | Benchmark of 20 datasets on whether LLMs decline to answer; abstention is "an unsolved problem" across 20 frontier models; reasoning fine-tuning lowers abstention by 24% on average; a careful system prompt can raise it. The page does not say models "rarely" abstain (the older note's wording), so that phrasing is dropped. | Oct 17, 2026 | opened (abstract) |
| 2 | Sun, Yin, Guo, Wu, Qiu, Zhao, **Benchmarking Hallucination in LLMs based on Unanswerable Math Word Problem (UMWP)**, arXiv 2403.03558 (Mar 6, 2024). https://arxiv.org/abs/2403.03558 | 5,200 unanswerable math word problems in 5 categories; 31 models; in-context learning and RLHF help models avoid made-up answers. Was UNVERIFIED (snippet only); now opened. | Oct 17, 2026 | opened (abstract) |
| 3 | Zhang, Xu, Cai, **Recognizing Limits: Investigating Infeasibility in LLMs**, Findings of EMNLP 2025, pp. 10092-10112. https://aclanthology.org/2025.findings-emnlp.535/ | Four categories of infeasible tasks, a benchmark of infeasible and feasible tasks, and fine-tuning to improve refusal. Was UNVERIFIED (snippet only); now opened. | Oct 17, 2026 | opened (abstract) |
| 4 | Liu, Liu, Sun, Hu, **Answering the Unanswerable Is to Err Knowingly: Analyzing and Mitigating Abstention Failures in Large Reasoning Models**, arXiv 2508.18760 (v1 Aug 26, 2025; v3 Jan 19, 2026; AAAI listing seen in search). https://arxiv.org/abs/2508.18760 | Large reasoning models often fail to abstain on unanswerable questions (math problems missing conditions) even though they can recognize the flaw internally; an inference-time method raises abstention. Found this session. | Oct 17, 2026 | opened (abstract) |
| 5 | Du, Hu, **Recognition-Refusal Misalignment in LLMs: Why Models Answer Structurally Unanswerable Questions**, arXiv 2608.29109 (Aug 29, 2026; EMNLP 2026 main per the page). https://arxiv.org/abs/2608.29109 | Instruction-tuned models (1.7B to 70B) internally represent that a math or code prompt is impossible yet still answer; framed as a routing failure. Math and code prompts only, not queueing. Found this session. | Oct 17, 2026 | opened (abstract) |
| 6 | Ao, Simchi-Levi, Wang, **ORLoopBench**, arXiv 2601.21008 (v1 Jan 28, 2026). https://arxiv.org/abs/2601.21008 | Repair of infeasible LP/MILP models in a solver loop (5,362 instances) plus an inventory-decision benchmark of behavioral rationality; an 8B model trained with solver feedback beats frontier APIs on LP repair. Infeasible *optimization models*, not word problems with a missing answer. | Oct 17, 2026 | opened (abstract) |
| 7 | Wang, Chen, Wu, Liu, Zhang, Shao, **Infeasibility Aware LLMs for Combinatorial Optimization**, arXiv 2604.01455 (Apr 1, 2026). https://arxiv.org/abs/2604.01455 | Fine-tunes an 8B model to both solve minor-embedding instances and judge when none is valid. Combinatorial optimization, not queueing. | Oct 17, 2026 | opened (abstract) |
| 8 | Kumar, Peng, Wu, Zeevi, **Performance of LLMs on Stochastic Modeling Operations Research Problems: From Theory to Practice**, arXiv 2506.23924 (Jun 30, 2025). https://arxiv.org/abs/2506.23924 | Evaluates LLMs on graduate-level stochastic-modeling homework and exam questions and SimOpt tasks; leading models do about as well as human experts. The abstract does not mention unstable queues or unanswerable cases. | Oct 17, 2026 | opened (abstract) |
| 9 | **M/M/1 queue**, Wikipedia. https://en.wikipedia.org/wiki/M/M/1_queue | Stable only when arrival rate < service rate (rho < 1); if arrivals outpace service the queue grows without bound and no stationary distribution exists. The page does not explicitly discuss rho exactly 1 (as read by the fetch tool). | Oct 17, 2026 | opened |

Search for a closer match (web searches, Oct 17, 2026; three queries, standard depth): looked for a study asking
LLMs queueing questions whose load is at or above capacity, and for LLM studies of infeasible operations-research
word problems. **None found in these searches.** That is "not found in a short search", not "does not exist":
completeness is UNVERIFIED. Adjacent hits: arXiv 2605.04595 (queueing theory *of* LLM inference, a different
topic, seen in search results only, not opened), arXiv 2508.03406 (infeasibility diagnosis for routing models,
seen in search results only, not opened).

Not verified at source: the claim that load exactly 1.00 has no long-run average wait *when arrivals and service
are random* (our template says so). The M/M/1 page does not discuss equality; a search result mentioned that a
deterministic (D/D/1) queue is the usual exception at utilization 1. The project's reasoning is in `PLAN.md`
section 2; a textbook citation for the equality case is still to be found. **UNVERIFIED.**
