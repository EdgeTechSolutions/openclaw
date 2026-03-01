#!/usr/bin/env python3
"""
Search Hugging Face Hub for open-source models.
Uses the public HF API — no API key required.

Usage:
  python3 search_models.py --query "llama" --task text-generation --sort downloads --limit 10
  python3 search_models.py --trending --task text-generation --limit 10
  python3 search_models.py --query "embedding" --task feature-extraction --sort likes
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime

HF_TOKEN = os.environ.get("HF_TOKEN", "")

PIPELINE_TAGS = {
    "text-generation": "text-generation",
    "chat": "text-generation",
    "llm": "text-generation",
    "instruct": "text-generation",
    "embedding": "feature-extraction",
    "embeddings": "feature-extraction",
    "feature-extraction": "feature-extraction",
    "text2text": "text2text-generation",
    "summarization": "summarization",
    "translation": "translation",
    "image": "text-to-image",
    "text-to-image": "text-to-image",
    "asr": "automatic-speech-recognition",
    "speech": "automatic-speech-recognition",
    "vision": "image-classification",
    "multimodal": "image-text-to-text",
}

SORT_OPTIONS = ["downloads", "likes", "lastModified", "createdAt"]


def fetch_models(query=None, task=None, sort="downloads", limit=10, language=None,
                 min_downloads=None, library=None):
    params = {
        "limit": min(limit, 100),
        "direction": "-1",
        "sort": sort,
        "full": "false",
    }
    if query:
        params["search"] = query
    if task:
        resolved = PIPELINE_TAGS.get(task.lower(), task)
        params["filter"] = resolved
    if language:
        params["language"] = language
    if library:
        params["library"] = library

    url = "https://huggingface.co/api/models?" + urllib.parse.urlencode(params)
    headers = {"User-Agent": "OpenClaw-HF-Skill/1.0"}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        models = json.load(resp)

    if min_downloads:
        models = [m for m in models if m.get("downloads", 0) >= min_downloads]

    return models


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


def print_results(models, sort, limit):
    if not models:
        print("No models found.")
        return

    models = models[:limit]
    print(f"\n{'─'*72}")
    print(f"  {'MODEL':<42} {'TASK':<18} {'↓DL':>7}  {'♥':>6}  {'UPDATED'}")
    print(f"{'─'*72}")
    for m in models:
        mid = m.get("modelId") or m.get("id", "?")
        task = m.get("pipeline_tag", "—")
        dl = format_number(m.get("downloads", 0))
        likes = format_number(m.get("likes", 0))
        updated = format_date(m.get("lastModified", ""))
        # Truncate long IDs
        mid_disp = mid if len(mid) <= 42 else mid[:39] + "…"
        print(f"  {mid_disp:<42} {task:<18} {dl:>7}  {likes:>6}  {updated}")

    print(f"{'─'*72}")
    print(f"  Sorted by: {sort} | Showing {len(models)} result(s)")
    print(f"  🔗 https://huggingface.co/models?sort={sort}\n")


def main():
    parser = argparse.ArgumentParser(description="Search Hugging Face models")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--task", "-t", help=f"Pipeline task: {', '.join(set(PIPELINE_TAGS.values()))}")
    parser.add_argument("--sort", "-s", default="downloads",
                        choices=SORT_OPTIONS,
                        help="Sort order: downloads, likes, lastModified, createdAt (default: downloads)")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Number of results")
    parser.add_argument("--language", help="Language filter (e.g. en, fr)")
    parser.add_argument("--min-downloads", type=int, help="Minimum download count")
    parser.add_argument("--library", help="Library filter (e.g. transformers, gguf)")
    parser.add_argument("--new", "--recent", dest="recent", action="store_true",
                        help="Show recently updated models (alias for --sort lastModified)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    if args.recent:
        args.sort = "lastModified"

    try:
        models = fetch_models(
            query=args.query,
            task=args.task,
            sort=args.sort,
            limit=args.limit,
            language=args.language,
            min_downloads=args.min_downloads,
            library=args.library,
        )
    except Exception as e:
        print(f"Error fetching models: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(models, indent=2))
    else:
        print_results(models, args.sort, args.limit)


if __name__ == "__main__":
    main()
