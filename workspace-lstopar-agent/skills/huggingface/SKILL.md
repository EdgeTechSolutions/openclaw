---
name: huggingface
description: Search and explore open-source models on Hugging Face Hub. Use when searching for LLMs, embedding models, or other open-source models by task/size/license; browsing trending or most-downloaded models; fetching detailed model metadata; or querying the Open LLM Leaderboard for benchmark rankings.
---

# Hugging Face Skill

Search the Hugging Face Hub for open-source models and query the Open LLM Leaderboard.

No API key required. Set `HF_TOKEN` env var for higher rate limits or access to gated models.

## Scripts

All scripts live at `{baseDir}/scripts/`. Use `python3` to run them — no extra packages needed (stdlib only).

---

## 1. Search Models — `search_models.py`

Search the HF Hub by keyword, task type, and sort order.

```bash
# Most downloaded LLMs matching "llama"
python3 {baseDir}/scripts/search_models.py --query "llama" --task text-generation --sort downloads --limit 10

# Top liked embedding models
python3 {baseDir}/scripts/search_models.py --task feature-extraction --sort likes --limit 10

# Recently updated instruction models from mistral
python3 {baseDir}/scripts/search_models.py --query "mistral instruct" --new --limit 8

# Most liked models with GGUF files (runs locally via llama.cpp / ollama)
python3 {baseDir}/scripts/search_models.py --query "gguf" --sort likes --limit 10

# English text-generation models with at least 100K downloads
python3 {baseDir}/scripts/search_models.py --task text-generation --language en --min-downloads 100000 --limit 15
```

### `--task` shortcuts

| Input | Resolves to |
|-------|------------|
| `llm`, `chat`, `instruct`, `text-generation` | `text-generation` |
| `embedding`, `embeddings`, `feature-extraction` | `feature-extraction` |
| `text2text` | `text2text-generation` |
| `image`, `text-to-image` | `text-to-image` |
| `speech`, `asr` | `automatic-speech-recognition` |
| `multimodal` | `image-text-to-text` |

### `--sort` options

`downloads` · `likes` · `lastModified` · `createdAt` — or use `--new` as an alias for `lastModified`

---

## 2. Open LLM Leaderboard — `leaderboard.py`

Query the Open LLM Leaderboard v2 (`open-llm-leaderboard/contents`). Sorts by **Average** benchmark score.

Benchmarks: **IFEval** (instruction following) · **BBH** (reasoning) · **MATH Lvl 5** (maths) · **GPQA** (graduate science) · **MUSR** (multi-step reasoning) · **MMLU-PRO** (language understanding)

```bash
# Top 20 models overall (scans 500 entries)
python3 {baseDir}/scripts/leaderboard.py --top 20

# Top 10 small models (≤8B params), no MoE
python3 {baseDir}/scripts/leaderboard.py --top 10 --max-params 8 --no-moe

# Top 15 mid-range models (7B–14B)
python3 {baseDir}/scripts/leaderboard.py --top 15 --min-params 7 --max-params 14

# Search for a specific model or family
python3 {baseDir}/scripts/leaderboard.py --query "llama" --top 10

# Show individual benchmark scores (instead of params/license)
python3 {baseDir}/scripts/leaderboard.py --query "qwen" --top 10 --benchmarks

# Broader scan for more comprehensive top-N (slower)
python3 {baseDir}/scripts/leaderboard.py --top 20 --scan 2000
```

### Flags

| Flag | Effect |
|------|--------|
| `--no-moe` | Exclude Mixture-of-Experts models |
| `--no-merged` | Exclude merged/frankenmerge models |
| `--max-params N` | Only models with ≤N billion parameters |
| `--min-params N` | Only models with ≥N billion parameters |
| `--benchmarks` | Show IFEval/BBH/MATH/GPQA/MUSR/MMLU-PRO columns |
| `--scan N` | Rows to scan for top-N ranking (default 500; use 2000 for full coverage) |

> **Note**: The leaderboard dataset has ~4 500 entries sorted alphabetically. The default scan of 500 rows gives a representative sample. Use `--scan 2000` for more complete coverage, or `--query` to search a specific model/org (fast, no scan limit).

---

## 3. Model Details — `model_info.py`

Get detailed metadata for a specific model.

```bash
python3 {baseDir}/scripts/model_info.py --model meta-llama/Llama-3.1-8B-Instruct
python3 {baseDir}/scripts/model_info.py --model mistralai/Mistral-7B-Instruct-v0.3
python3 {baseDir}/scripts/model_info.py --model Qwen/Qwen2.5-7B-Instruct
```

Shows: task, library, downloads, likes, license, languages, base model, eval results, available GGUF files, safetensor shards.

---

## Workflow examples

### "What's the best open-source LLM I can run locally on 16GB VRAM?"

```bash
# 1. Check leaderboard for 7–13B models (fits in 16GB)
python3 {baseDir}/scripts/leaderboard.py --top 10 --min-params 7 --max-params 13 --no-moe

# 2. Check if top results have GGUF versions
python3 {baseDir}/scripts/model_info.py --model <top-result>
```

### "Find the best embedding model"

```bash
python3 {baseDir}/scripts/search_models.py --task embeddings --sort downloads --limit 10
```

### "What's new in open-source AI this week?"

```bash
python3 {baseDir}/scripts/search_models.py --task text-generation --new --limit 15
```

### "How does Qwen2.5 rank on the leaderboard?"

```bash
python3 {baseDir}/scripts/leaderboard.py --query "qwen2.5" --top 10 --benchmarks
```

---

## Rate limits

The HF API is free and unauthenticated. Heavy use (many leaderboard pages) may trigger rate limiting.
Set `HF_TOKEN` in the environment to authenticate and get higher limits:

```bash
export HF_TOKEN="hf_..."
```

The scripts will automatically use it when set.
