"""Send questions to a local Ollama model and save every reply with its timing.

The models were run by Claude under Jayden's direction, on his computers and only for runs his approved plan covers.

  Timing pilot (10 questions, saved under data/raw/pilot/, never study data):
    python3 src/run_models.py --setting qwen3-8b-nothink --pilot 10
  Same pilot on another machine, saved to its own file:
    python3 src/run_models.py --setting qwen3-8b-nothink --pilot 10 --pilot-tag pc --host http://127.0.0.1:11501
  Main run (only after PREREG.md is committed; safe to stop and restart, it skips finished questions):
    python3 src/run_models.py --setting qwen3-8b-nothink
  Randomness repeat set (100 questions x 3 at temperature 0.7):
    python3 src/run_models.py --setting qwen3-8b-nothink --repeats
  Thinking-on check, run on the PC itself (added Oct 13, 2026; only after Jayden's yes and a PREREG entry):
    python src/run_models.py --setting qwen3-8b-think --agents 1 --num-predict 12000 --num-ctx 16384 --pilot 10 --pilot-tag pc-cap12000
  --agents, --num-predict and --num-ctx default to the settings every earlier run used (all agents, 6,000, 8,192).

Written by Claude (Oct 12, 2026) at Jayden's request; logged in WORKLOG.md.
"""
import argparse
import csv
import json
import random
import time
from pathlib import Path

try:
    import requests
except ImportError:          # the PC's Python may not have it; fall back to the standard library
    requests = None
    import urllib.request

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS = ROOT / "data" / "processed" / "questions.csv"

# think: False/True for Qwen3; gpt-oss takes "low"/"medium"/"high" and cannot be fully switched off.
# UNVERIFIED until the timing pilot shows the switch works on your Ollama version.
SETTINGS = {
    "qwen3-8b-nothink": {"model": "qwen3:8b", "think": False},
    "qwen3-8b-think": {"model": "qwen3:8b", "think": True},
    "gpt-oss-20b": {"model": "gpt-oss:20b", "think": "low"},
}


def post_json(host, path, body, timeout):
    if requests is not None:
        r = requests.post(f"{host}{path}", json=body, timeout=timeout)
        r.raise_for_status()
        return r.json()
    req = urllib.request.Request(f"{host}{path}", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def get_json(host, path, timeout):
    if requests is not None:
        r = requests.get(f"{host}{path}", timeout=timeout)
        r.raise_for_status()
        return r.json()
    with urllib.request.urlopen(f"{host}{path}", timeout=timeout) as r:
        return json.loads(r.read())


def ask(host, model, think, text, temperature, seed, num_predict=6000, num_ctx=8192):
    body = {
        "model": model,
        "messages": [{"role": "user", "content": text}],
        "stream": False,
        "think": think,
        # Context window and a hard cap on generated tokens (thinking + reply), so a thinking model
        # cannot loop forever. A reply cut off by the cap with no ANSWER line is a format failure.
        "options": {"temperature": temperature, "seed": seed, "num_ctx": num_ctx, "num_predict": num_predict},
    }
    start = time.time()
    data = post_json(host, "/api/chat", body, timeout=3600)
    msg = data.get("message", {})
    return {
        "reply": msg.get("content", ""),
        "thinking": msg.get("thinking", ""),
        "seconds": round(time.time() - start, 2),
        "eval_tokens": data.get("eval_count"),
        "done_reason": data.get("done_reason"),     # "length" = hit the token cap
    }


def model_digest(host, model):
    """The model's full ID on this Ollama server; `ollama list` shows its first 12 characters."""
    for m in get_json(host, "/api/tags", timeout=30).get("models", []):
        if m.get("name") == model:
            return m["digest"]
    raise SystemExit(f"{model} is not installed on {host}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--setting", required=True, choices=SETTINGS)
    p.add_argument("--host", default="http://localhost:11434")
    p.add_argument("--pilot", type=int, default=0, help="run N random questions as a timing pilot")
    p.add_argument("--pilot-tag", default="", help="keeps a pilot on another machine in its own file, e.g. pc")
    p.add_argument("--repeats", action="store_true", help="100 questions x 3 at temperature 0.7")
    p.add_argument("--agents", type=int, choices=[1, 4], help="only questions with this many agents")
    p.add_argument("--num-predict", type=int, default=6000, help="cap on generated tokens (thinking + reply)")
    p.add_argument("--num-ctx", type=int, default=8192, help="context window; must hold the prompt plus the cap")
    args = p.parse_args()
    cfg = SETTINGS[args.setting]
    if args.num_predict + 500 > args.num_ctx:
        raise SystemExit(f"--num-ctx {args.num_ctx} is too small for --num-predict {args.num_predict} plus the prompt")

    with QUESTIONS.open() as f:
        questions = list(csv.DictReader(f))
    if args.agents:
        questions = [q for q in questions if int(q["agents"]) == args.agents]
    rng = random.Random(7)
    if args.pilot:
        jobs = [(q, 0.0, 0) for q in rng.sample(questions, args.pilot)]
        tag = f"-{args.pilot_tag}" if args.pilot_tag else ""
        out = ROOT / "data" / "raw" / "pilot" / f"{args.setting}{tag}.jsonl"
    elif args.repeats:
        picked = rng.sample(questions, 100)
        jobs = [(q, 0.7, rep + 1) for q in picked for rep in range(3)]
        out = ROOT / "data" / "raw" / "repeats" / f"{args.setting}.jsonl"
    else:
        jobs = [(q, 0.0, 0) for q in questions]
        out = ROOT / "data" / "raw" / "main" / f"{args.setting}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)

    done = set()
    if out.exists():
        for line in out.open():
            rec = json.loads(line)
            done.add((rec["question_id"], rec["rep"]))

    todo = [j for j in jobs if (j[0]["question_id"], j[2]) not in done]
    digest = model_digest(args.host, cfg["model"])
    print(f"{args.setting}: {len(todo)} to run, {len(done)} already saved -> {out}")
    print(f"{cfg['model']} ID {digest[:12]} on {args.host}")
    with out.open("a") as f:
        for i, (q, temp, rep) in enumerate(todo, 1):
            for attempt in range(3):            # retry a failed call after a pause instead of stopping
                try:
                    res = ask(args.host, cfg["model"], cfg["think"], q["text"], temp, seed=1000 + rep,
                              num_predict=args.num_predict, num_ctx=args.num_ctx)
                    break
                except Exception as e:  # noqa: BLE001
                    if attempt == 2:
                        raise
                    print(f"call failed ({e}); retrying in 30 s")
                    time.sleep(30)
            rec = {"question_id": q["question_id"], "rep": rep, "setting": args.setting,
                   "model": cfg["model"], "model_digest": digest, "think": cfg["think"],
                   "temperature": temp, "num_predict": args.num_predict, "num_ctx": args.num_ctx,
                   "time": time.strftime("%Y-%m-%d %H:%M:%S"), **res}
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print(f"[{i}/{len(todo)}] {q['question_id']} {res['seconds']}s")


if __name__ == "__main__":
    main()
