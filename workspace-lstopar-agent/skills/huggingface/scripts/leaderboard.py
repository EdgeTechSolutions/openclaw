#!/usr/bin/env python3
"""
Query the Open LLM Leaderboard (v2) — open-llm-leaderboard/contents dataset.
Fetches top models by average benchmark score.

Benchmarks tracked:
  IFEval  — instruction following
  BBH     — BIG-Bench Hard (reasoning)
  MATH Lvl 5 — advanced mathematics
  GPQA    — graduate-level science Q&A
  MUSR    — multi-step reasoning
  MMLU-PRO — massive multitask language understanding (pro)

Usage:
  python3 leaderboard.py --top 20
  python3 leaderboard.py --top 10 --max-params 8
  python3 leaderboard.py --query "llama" --top 10
  python3 leaderboard.py --top 15 --no-moe --max-params 13
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse
import re

HF_TOKEN = os.environ.get("HF_TOKEN", "")

BASE_URL = "https://datasets-server.huggingface.co"
DATASET = "open-llm-leaderboard/contents"
BENCHMARKS = ["IFEval", "BBH", "MATH Lvl 5", "GPQA", "MUSR", "MMLU-PRO"]

FETCH_BATCH = 100  # rows per request
MAX_FETCH = 500    # default rows to scan (dataset has 4576 entries; use --scan for more)


def strip_html(text):
    """Strip HTML tags from leaderboard model names."""
    return re.sub(r"<[^>]+>", "", str(text)).strip()


def fetch_rows(query=None, offset=0, length=100):
    params = {
        "dataset": DATASET,
        "config": "default",
        "split": "train",
        "offset": offset,
        "length": length,
    }
    if query:
        endpoint = "/search"
        params["query"] = query
    else:
        endpoint = "/rows"

    url = BASE_URL + endpoint + "?" + urllib.parse.urlencode(params)
    headers = {"User-Agent": "OpenClaw-HF-Skill/1.0"}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.load(resp)
        return data.get("rows", [])
    except Exception as e:
        return []


def collect_all_rows(query=None, max_rows=MAX_FETCH):
    """Paginate through the dataset to collect enough rows for meaningful sorting."""
    all_rows = []
    offset = 0
    while offset < max_rows:
        batch = fetch_rows(query=query, offset=offset, length=FETCH_BATCH)
        if not batch:
            break
        all_rows.extend(batch)
        offset += FETCH_BATCH
        # If query search returns fewer than batch, we got everything
        if query and len(batch) < FETCH_BATCH:
            break
        # Small pause to avoid rate limiting between pagination requests
        if offset < max_rows:
            time.sleep(0.3)
    return all_rows


def parse_row(r):
    row = r.get("row", {})
    return {
        "model": strip_html(row.get("fullname", row.get("Model", "?"))),
        "avg": round(float(row.get("Average ⬆️") or 0), 2),
        "params": row.get("#Params (B)"),
        "arch": row.get("Architecture", "?"),
        "license": row.get("Hub License", "?"),
        "type": row.get("Type", "?"),
        "moe": bool(row.get("MoE", False)),
        "merged": bool(row.get("Merged", False)),
        "flagged": bool(row.get("Flagged", False)),
        "ifeval": round(float(row.get("IFEval") or 0), 1),
        "bbh": round(float(row.get("BBH") or 0), 1),
        "math": round(float(row.get("MATH Lvl 5") or 0), 1),
        "gpqa": round(float(row.get("GPQA") or 0), 1),
        "musr": round(float(row.get("MUSR") or 0), 1),
        "mmlu_pro": round(float(row.get("MMLU-PRO") or 0), 1),
        "generation": row.get("Generation"),
        "base_model": row.get("Base Model", ""),
    }


def print_leaderboard(models, top, show_benchmarks=False, total_scanned=0):
    if not models:
        print("No models found matching the criteria.")
        return

    models = models[:top]
    print(f"\n{'─'*80}")
    if show_benchmarks:
        print(f"  {'#':<4} {'MODEL':<40} {'AVG':>5}  {'IFEval':>6} {'BBH':>5} {'MATH':>5} {'GPQA':>5} {'MUSR':>5} {'MMLU':>5}")
    else:
        print(f"  {'#':<4} {'MODEL':<48} {'AVG':>5}  {'PARAMS':>8}  {'LICENSE':<14} {'ARCH'}")
    print(f"{'─'*80}")

    for i, m in enumerate(models, 1):
        model_disp = m["model"] if len(m["model"]) <= 48 else m["model"][:45] + "…"
        avg = f"{m['avg']:.1f}"
        flags = ""
        if m["moe"]:
            flags += " [MoE]"
        if m["merged"]:
            flags += " [merged]"

        if show_benchmarks:
            model_disp = m["model"] if len(m["model"]) <= 40 else m["model"][:37] + "…"
            print(f"  {i:<4} {model_disp:<40} {avg:>5}  {m['ifeval']:>6} {m['bbh']:>5} {m['math']:>5} {m['gpqa']:>5} {m['musr']:>5} {m['mmlu_pro']:>5}")
        else:
            params = f"{m['params']:.1f}B" if m["params"] else "?"
            lic = (m["license"] or "?")[:14]
            arch = (m["arch"] or "?")[:20]
            print(f"  {i:<4} {(model_disp + flags):<48} {avg:>5}  {params:>8}  {lic:<14} {arch}")

    print(f"{'─'*80}")
    scanned_note = f" (scanned {total_scanned} entries)" if total_scanned else ""
    print(f"  Sorted by Average score | Top {len(models)}{scanned_note}")
    print(f"  🔗 https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard\n")


def main():
    parser = argparse.ArgumentParser(description="Query Open LLM Leaderboard")
    parser.add_argument("--top", "-n", type=int, default=20, help="Number of top models to show")
    parser.add_argument("--query", "-q", help="Search for specific model or org")
    parser.add_argument("--max-params", type=float, help="Max parameter count (B), e.g. 8 for ≤8B")
    parser.add_argument("--min-params", type=float, help="Min parameter count (B)")
    parser.add_argument("--no-moe", action="store_true", help="Exclude Mixture-of-Experts models")
    parser.add_argument("--no-merged", action="store_true", help="Exclude merged models")
    parser.add_argument("--no-flagged", action="store_true", default=True,
                        help="Exclude flagged models (default: True)")
    parser.add_argument("--benchmarks", "-b", action="store_true",
                        help="Show individual benchmark scores instead of model metadata")
    parser.add_argument("--scan", type=int, default=MAX_FETCH,
                        help=f"Max rows to scan for top-N ranking (default: {MAX_FETCH}; use 2000+ for full coverage)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    print(f"Fetching leaderboard data...", file=sys.stderr)
    raw_rows = collect_all_rows(query=args.query, max_rows=args.scan)

    if not raw_rows:
        print("Failed to fetch leaderboard data.", file=sys.stderr)
        sys.exit(1)

    models = [parse_row(r) for r in raw_rows]

    # Filters
    if args.no_flagged:
        models = [m for m in models if not m["flagged"]]
    if args.no_moe:
        models = [m for m in models if not m["moe"]]
    if args.no_merged:
        models = [m for m in models if not m["merged"]]
    if args.max_params is not None:
        models = [m for m in models if m["params"] is not None and m["params"] <= args.max_params]
    if args.min_params is not None:
        models = [m for m in models if m["params"] is not None and m["params"] >= args.min_params]

    # Sort by average score descending
    models.sort(key=lambda m: m["avg"], reverse=True)

    if args.json:
        print(json.dumps(models[:args.top], indent=2))
    else:
        print_leaderboard(models, top=args.top, show_benchmarks=args.benchmarks,
                          total_scanned=len(raw_rows))


if __name__ == "__main__":
    main()
