# MEMORY.md - Darwin's Long-Term Memory

_Updated weekly from nightly run logs._

## First Run

Darwin came online in March 2026. The knowledge graph plugin was refactored to remove the real-time message-hook extraction pipeline — Darwin replaced it with a nightly batch scan.

## Knowledge Graph State

- DB path: `/home/lstopar/.openclaw/knowledge-graph.db`
- Embeddings: Gemini `text-embedding-004` (768d)
- Initial facts seeded from prior Haiku extraction (task list / OpenClaw context)

## Known Agents & Sessions

| Agent | Session pattern | Notes |
|---|---|---|
| Agamemnon | `agent:main:telegram:group:-5247564907` | Main group chat |
| Cyril | `agent:lstopar-agent:telegram:...` | Luka's personal DM agent |
| Galileo | `agent:galileo:subagent:...` | Research sub-agent |
| von Neumann | `agent:von-neumann:subagent:...` | Engineering sub-agent |
| Homer | `agent:homer:subagent:...` | Writing sub-agent |
| Keynes | `agent:keynes:subagent:...` | Trading/finance sub-agent |

## Extraction Rules (confirmed)

- Skip plans, designs, hypotheticals
- Deduplicate: check entity before insert
- Only store facts about existing things
- Source tag: `"darwin"` on all inserted facts
