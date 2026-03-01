#!/usr/bin/env python3
"""
Fetch detailed info about a specific Hugging Face model.

Usage:
  python3 model_info.py --model meta-llama/Llama-3.1-8B-Instruct
  python3 model_info.py --model mistralai/Mistral-7B-Instruct-v0.3
"""

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime

HF_TOKEN = os.environ.get("HF_TOKEN", "")


def fetch_model_info(model_id):
    url = f"https://huggingface.co/api/models/{model_id}"
    headers = {"User-Agent": "OpenClaw-HF-Skill/1.0"}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)


def format_number(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def format_date(iso):
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return iso[:10] if iso else "?"


def print_model_info(m):
    mid = m.get("modelId") or m.get("id", "?")
    print(f"\n{'─'*60}")
    print(f"  {mid}")
    print(f"{'─'*60}")

    # Basic info
    task = m.get("pipeline_tag", "—")
    library = m.get("library_name", "—")
    dl = format_number(m.get("downloads", 0))
    likes = format_number(m.get("likes", 0))
    created = format_date(m.get("createdAt", ""))
    updated = format_date(m.get("lastModified", ""))
    private = "Private" if m.get("private") else "Public"
    gated = " · Gated" if m.get("gated") else ""

    print(f"  Task:      {task}")
    print(f"  Library:   {library}")
    print(f"  Downloads: {dl}  ♥ {likes}")
    print(f"  Created:   {created}  Updated: {updated}")
    print(f"  Access:    {private}{gated}")

    # License
    tags = m.get("tags", [])
    license_tag = next((t.replace("license:", "") for t in tags if t.startswith("license:")), None)
    if license_tag:
        print(f"  License:   {license_tag}")

    # Languages
    langs = [t.replace("language:", "") for t in tags if len(t) == 2 or t in
             ("en", "fr", "de", "es", "it", "zh", "ja", "ko", "pt", "ru", "ar")]
    if not langs:
        langs = m.get("cardData", {}).get("language", [])
    if langs:
        print(f"  Languages: {', '.join(langs[:10])}")

    # Base model
    base = next((t.replace("base_model:finetune:", "").replace("base_model:", "")
                 for t in tags if t.startswith("base_model:")), None)
    if base:
        print(f"  Base:      {base}")

    # Model card excerpt
    card = m.get("cardData", {})
    if card.get("model_type"):
        print(f"  Type:      {card['model_type']}")

    # Eval results
    eval_results = m.get("cardData", {}).get("eval_results", [])
    if eval_results:
        print(f"\n  Eval results ({len(eval_results)} tasks):")
        for er in eval_results[:5]:
            task_name = er.get("task", {}).get("name", "?")
            dataset_name = er.get("dataset", {}).get("name", "?")
            metrics = er.get("metrics", [{}])
            val = metrics[0].get("value", "?") if metrics else "?"
            print(f"    · {task_name} / {dataset_name}: {val}")
        if len(eval_results) > 5:
            print(f"    … and {len(eval_results)-5} more")

    # Siblings (files)
    siblings = m.get("siblings", [])
    safetensors = [s for s in siblings if s.get("rfilename", "").endswith(".safetensors")]
    gguf = [s for s in siblings if s.get("rfilename", "").endswith(".gguf")]
    if safetensors:
        print(f"\n  Safetensors: {len(safetensors)} shard(s)")
    if gguf:
        print(f"  GGUF:        {len(gguf)} file(s): {', '.join(g['rfilename'] for g in gguf[:3])}")
        if len(gguf) > 3:
            print(f"               … and {len(gguf)-3} more")

    print(f"\n  🔗 https://huggingface.co/{mid}")
    print(f"{'─'*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Get detailed info about a HF model")
    parser.add_argument("--model", "-m", required=True, help="Model ID (e.g. org/name)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    try:
        info = fetch_model_info(args.model)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Model not found: {args.model}", file=sys.stderr)
        else:
            print(f"HTTP error {e.code}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(info, indent=2))
    else:
        print_model_info(info)


if __name__ == "__main__":
    main()
