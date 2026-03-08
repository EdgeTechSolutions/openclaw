# Knowledge Graph Plugin for OpenClaw

Extracts facts from conversations and emails, stores them as `(subject, relation, object)` triples in a vector-searchable knowledge graph backed by SQLite.

## Features

- **Automatic fact extraction** from conversations via `message:received` and `message:sent` hooks
- **Sliding window buffer** (4 Q&A pairs with 50% overlap) for context-aware extraction
- **Vector embeddings** for semantic search (Gemini or OpenAI)
- **Agent tool** (`knowledge_graph`) for querying, searching, and managing the graph
- **Entity deduplication** (merge duplicate entities)
- **Manual fact addition** via the agent tool
- **SQLite storage** — lightweight, single file, works great on Raspberry Pi

## Installation

1. Copy the plugin to your OpenClaw extensions directory:

```bash
cp -r knowledge-graph ~/.openclaw/extensions/
cd ~/.openclaw/extensions/knowledge-graph
npm install
```

2. Add to your `openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "knowledge-graph": {
        "enabled": true,
        "config": {
          "embeddingProvider": "gemini",
          "embeddingApiKey": "YOUR_GEMINI_API_KEY",
          "embeddingModel": "text-embedding-004",
          "embeddingDimensions": 768,
          "extractionModel": "synthetic/devstral-2512",
          "windowSize": 8,
          "flushTimeoutMs": 300000,
          "minConfidence": 0.6,
          "dbPath": "~/.openclaw/knowledge-graph.db"
        }
      }
    }
  },
  "tools": {
    "alsoAllow": ["knowledge_graph"]
  }
}
```

3. Restart the Gateway:

```bash
openclaw gateway restart
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `embeddingProvider` | `"gemini"` | Embedding API provider (`gemini` or `openai`) |
| `embeddingApiKey` | `""` | API key for embedding provider |
| `embeddingModel` | `"text-embedding-004"` | Embedding model name |
| `embeddingDimensions` | `768` | Vector dimensions |
| `extractionModel` | `"synthetic/devstral-2512"` | LLM model for fact extraction |
| `windowSize` | `8` | Messages to buffer (8 = 4 Q&A pairs) |
| `flushTimeoutMs` | `300000` | Flush buffer after 5 min inactivity |
| `minConfidence` | `0.6` | Min confidence to store a fact |
| `dbPath` | `"~/.openclaw/knowledge-graph.db"` | SQLite database path |

## Agent Tool Usage

The plugin registers a `knowledge_graph` tool with these actions:

### Semantic search
```
knowledge_graph(action="search", query="What tools are we using?")
```

### Look up entity
```
knowledge_graph(action="entity", entity="Luka")
```

### Filter by relation type
```
knowledge_graph(action="relation", relation="decided")
```

### Get stats
```
knowledge_graph(action="stats")
```

### Recent facts
```
knowledge_graph(action="recent", limit=20)
```

### Find similar entities
```
knowledge_graph(action="similar", entity="OpenClaw")
```

### Merge duplicate entities
```
knowledge_graph(action="merge", merge_from="Luka", merge_into="Luka Stopar")
```

### Manually add a fact
```
knowledge_graph(action="add", subject="Luka", subject_type="person", relation="works_at", object="EdgeTech", object_type="organization")
```

## Architecture

```
Messages ──► Buffer (8 msg window) ──► LLM Extract ──► SQLite + Embeddings
                │                           │                    │
                ▼                           ▼                    ▼
         50% overlap              (subject,rel,object)    Vector search
         5min idle flush          + confidence score       Cosine similarity
```

## Storage

- **Entities**: Nodes with name, type, properties
- **Relations**: Edges with subject, relation, object, confidence, source
- **Entity embeddings**: Vector representation of each entity
- **Fact embeddings**: Vector representation of "subject relation object" composite

Database file: `~/.openclaw/knowledge-graph.db` (~1KB per fact, ~3KB per embedding)

## Dependencies

- `better-sqlite3` — SQLite bindings for Node.js
- An LLM provider (via OpenClaw's llm-task tool or direct API)
- An embedding API (Gemini or OpenAI)
