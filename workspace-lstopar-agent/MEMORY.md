### **Telegram Topics and IDs**

| **Topic Name**         | **Topic ID** | **Purpose**                                      | **Associated Cron Jobs**                          | **Allowed User ID** |
|------------------------|--------------|--------------------------------------------------|---------------------------------------------------|---------------------|
| **#openclaw #cron**    | `729`        | Development updates, research, and cron job outputs. | Daily Jira Task Summary, Weekly Context Engineering Research Update, Weekly Trading Portfolio Report | `8403014547` |
| **#openclaw #dev**      | `615`        | Development updates, OpenClaw-related discussions, and reports. | None                                              | `8403014547`        |
| **#docs @edgetech**    | `779`        | Documentation, portfolio updates, macroeconomic context, and investment strategy discussions. | None                                              | `8403014547`        |
| **#comm @all**         | `761`        | General communication, updates, and announcements for all team members. | None                                              | `8403014547`        |
| **#trading @personal** | `701`        | Personal trading discussions, portfolio updates, and investment queries. | None                                              | `8403014547`        |
| **#ops @edgetech**     | `987`        | Operations updates and cron job outputs for EdgeTech. | Daily Jira Task Summary                           | `8403014547`        |
| **#tech #research**    | `945`        | LLM and AI research papers, technical findings, and model updates. | Weekly LLM Research Scan                          | `8403014547`        |
| **#comm @personal**    | `1299`       | Personal Gmail triage summaries, personal email notifications.    | Nightly Personal Email Categorizer                     | `8403014547`        |

---

- **Notes**:
  - Topic IDs are used in OpenClaw cron jobs to post results to specific Telegram topics.
  - If the topic is deleted/recreated, the ID may change and must be updated in cron jobs.
  - **Allowed User ID** ensures only authorized users can interact with specific topics.

---

### **Personal Calendar Policy**
- When fetching personal calendar, **always query all three**:
  1. Microsoft 365 calendar: `node /workspace/skills/microsoft365/index.js calendar list`
  2. Google Workspace primary calendar: `luka@stopar.si`
  3. Google Workspace shared calendar: `pg2acfjes7eufmjmrakim8hka8@group.calendar.google.com` (Jasna & Luka)
- Google account is now `luka@stopar.si` (Google Workspace)
- Merge and sort all events chronologically when presenting

### **GitHub**
- Authenticated via `gh` CLI as user `lstopar`
- Organization: `EdgeTechSolutions` (3 repos: openclaw fork, OpenClawConfig, AITools)
- Auth tokens: `/workspace/.config/gh/hosts.yml`

### **Jira Credential Storage**
- Credentials stored at `/workspace/.config/.jira/.credentials.yml` (login + secret)
- Load token each session: `export JIRA_API_TOKEN=$(grep '^secret:' /workspace/.config/.jira/.credentials.yml | awk '{print $2}')`
- No env var config needed in `openclaw.json`
- **Base URL**: `https://edgetech-atlassian.atlassian.net` (NOT `edgetechsolutions.atlassian.net`)

### **Document Creation Policy**
- When creating documents, **upload to OneDrive** at: `OpenClaw-created` folder
- OneDrive path: `/personal/luka_stopar_edgetech_si/Documents/OpenClaw-created`
- SharePoint URL: `https://edgtch-my.sharepoint.com/my?id=%2Fpersonal%2Fluka%5Fstopar%5Fedgetech%5Fsi%2FDocuments%2FOpenClaw%2Dcreated`
- Always send Luka a link to the uploaded file

### **Tool Preferences by Topic**
- **Default email**: Use the **microsoft365 skill** (`node /workspace/skills/microsoft365/index.js --account edgetech`) for email — this covers work emails, Microsoft 365 emails, and any unspecified email requests.
- **Personal email only**: Use the **gog skill** (Google Workspace CLI) — only when Luka explicitly asks for personal/Gmail emails.
- **Microsoft 365 credentials**: Token stored at `/workspace/skills/microsoft365/tokens/ms365.tokens.edgetech.json` (account name: `edgetech`, NOT `default`). Use `--account edgetech` when calling the skill. For direct Graph API calls, extract the access token from this file. No env file at `~/.openclaw/credentials/ms365.env` — credentials are self-contained in the skill directory.

---

### **Image/Video Generation**
- **Always use Nano Banana Pro skill** (`/workspace/skills/nano-banana-pro/`) for generating images and video materials
- Script: `uv run /workspace/skills/nano-banana-pro/scripts/generate_image.py`
- Workflow: 1K draft → iterate → 4K final
- Output lands in `/workspace/` — file tool can read it but message tool can't send local files (use inline MEDIA or tell user the path)

### **Gantt Chart for Sales Support**
- When Luka asks to prepare a Gantt chart in a sales/presales context, always create an **Excel file** (openpyxl) with:
  - WBS table + visual Gantt bars (colored cells) on one sheet
  - **Relative timeline**: T1, T2, T3... (weeks) — NO calendar dates
  - **Effort in PM** (Person-Month) — always use "PM" abbreviation, even in Slovenian documents
  - Color-coded phases (dark BG for phase rows, light BG for activities, colored Gantt bars)
  - Professional formatting: frozen panes, borders, landscape print setup
  - Spawn von Neumann with detailed task prompt for generation

### **Document Creation Policy**
- When creating documents, **upload to OneDrive** at: `OpenClaw-created` folder
- OneDrive path: `/personal/luka_stopar_edgetech_si/Documents/OpenClaw-created`
- SharePoint URL: `https://edgtch-my.sharepoint.com/my?id=%2Fpersonal%2Fluka%5Fstopar%5Fedgetech%5Fsi%2FDocuments%2FOpenClaw%2Dcreated`
- Organize into appropriate subdirectories (e.g., `ATVP/`, `SIJ/`, etc.)
- Always send Luka a link to the uploaded file
- Do NOT use litterbox/catbox for file delivery

### **Trading 212 Balance Policy**
- **Always fetch the latest balance** from the Trading 212 tool if the last check was **older than 5 minutes**.
- Do **not** rely on cached or previously stored data for balance inquiries.
---

### **Personal Email Categories & Auto-Archive Policy**

The **Nightly Personal Email Categorizer** cron job runs every night at 05:00 Europe/Ljubljana using **Claude Opus** and:
1. Fetches Gmail emails from the last 24 hours via the `gog` skill.
2. Categorizes them into the following buckets:

| Category | Auto-Archived |
|---|---|
| Personal / Work | No |
| Updates & Notifications | **Yes** |
| LinkedIn | **Yes** |
| Promotions | **Yes** |
| Trading 212 | No |
| Qogita (Wholesale) | No |
| Google Workspace | No |
| Google (Other) | No |
| Apple | No |
| Bitstamp | No |
| Wise | No |
| GitHub | No |
| Revolut | **Yes** |
| Forums | No |
| Calendar / Zoom / Amazon | No |
| Other | No |

3. Posts a grouped summary with links to each email to Telegram topic `1299` (`#comm @personal`).

### **Lookup Order for Entity / Relationship Questions**

When asked about entities or relationships (e.g. "where does X work?", "what is X?", "who makes Y?", "what tools does Z use?"):

1. **Knowledge graph first** — `knowledge_graph(action=entity, entity=Name)` or `knowledge_graph(action=search)`
2. **Memory search** — `memory_search` for context from past conversations
3. **Web search** — only if KG + memory come up empty

Never skip straight to web search for entities Luka might have discussed before.

---

### **General Principles**
- **Always verify data before writing to Confluence.** Fetch from source first, write once. Estimates are not acceptable for documented pages — one wrong publish requires a correction and wastes Luka's time.

### **Confluence Mermaid Diagrams**
- Plugin: **Mermaid Macro for Confluence** (by SoftwareTao, Forge-based)
- Storage format uses `ac:adf-extension` (NOT `ac:structured-macro`)
- Must replicate the full Forge macro envelope including app-id, environment-id, license block, extension-properties etc.
- Template IDs from EdgeTech instance:
  - App ID: `a58687c2-03ec-4bfe-b20a-cb78986824c7`
  - Environment ID: `4757bce8-d44b-49b2-80fe-d5bb53917be2`
  - Extension key: `a58687c2-03ec-4bfe-b20a-cb78986824c7/4757bce8-d44b-49b2-80fe-d5bb53917be2/static/Mermaid-Macro`
  - Cloud ID: `07055bb7-c377-4ef8-856e-4f18d616ff4a`
- Mermaid code goes in `guest-params > text` parameter, XML-escaped (`-->` becomes `--&gt;`)
- **Syntax rules** (mermaid 9.3.0):
  - Use `graph TD;` with semicolons after each line
  - **No em-dashes** (`—`) — use regular dashes (`-`)
  - **ASCII-safe labels** recommended (no `š`, `č`, `ž` in node labels — use `s`, `c`, `z`)
  - Newlines are preserved in the XML parameter
- Working build script: `/workspace/tmp/atvp/build_page2.py`
- Fallback approach: render via mermaid.ink API as JPG and attach as image

### **Hugging Face Skill**
- Built locally at `/workspace/skills/huggingface/` (not on ClawHub)
- Three scripts (stdlib only, no pip deps):
  - `search_models.py` — search HF Hub by query/task/sort (`downloads`, `likes`, `lastModified`, `createdAt`); `--new` = alias for lastModified; note: `trending` is **not** a valid sort value (400 error)
  - `leaderboard.py` — Open LLM Leaderboard v2; filters: `--max-params`, `--min-params`, `--no-moe`, `--no-merged`; default scan 500 rows, `--scan 2000` for full coverage
  - `model_info.py` — detailed metadata for a single model
- `HF_TOKEN` env var supported for higher rate limits / gated models

---

### **Microsoft 365 Credential Storage**
- **Config**: `skills/microsoft365/config.default.json`
- **Tokens**: `skills/microsoft365/tokens/ms365.tokens.default.json` (account: `edgetech`)
- Note: Not stored at `~/.openclaw/credentials/ms365.env` — self-contained in skill directory

### **Confluence Skill**
- Skill definition: `/workspace/skills/confluence/`
- Credentials: `/workspace/.confluence-cli/config.json`
- Confluence CLI installed via npm in `/workspace/.npm-global/`
- Atlassian API token: generate at https://id.atlassian.com/manage-profile/security/api-tokens

### **Jira Credentials**
- Stored at `/workspace/.config/.jira/.credentials.yml`
- Load token: `export JIRA_API_TOKEN=$(grep '^secret:' /workspace/.config/.jira/.credentials.yml | awk '{print $2}')`
