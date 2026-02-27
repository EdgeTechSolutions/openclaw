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

### **Lobster (Workflow Engine)**
- Source zip persists at `/workspace/tmp/lobster-main.zip`
- Needs rebuild after container restarts (extract, npm install, tsc)
- Not yet enabled as OpenClaw tool (`tools.alsoAllow: ["lobster"]`)

### **Document Creation Policy**
- When creating documents, **upload to OneDrive** at: `OpenClaw-created` folder
- OneDrive path: `/personal/luka_stopar_edgetech_si/Documents/OpenClaw-created`
- SharePoint URL: `https://edgtch-my.sharepoint.com/my?id=%2Fpersonal%2Fluka%5Fstopar%5Fedgetech%5Fsi%2FDocuments%2FOpenClaw%2Dcreated`
- Always send Luka a link to the uploaded file

### **Tool Preferences by Topic**
- **Default email**: Use the **microsoft365 skill** (`node /workspace/skills/microsoft365/index.js --account default`) for email — this covers work emails, Microsoft 365 emails, and any unspecified email requests.
- **Personal email only**: Use the **gog skill** (Google Workspace CLI) — only when Luka explicitly asks for personal/Gmail emails.
- **Microsoft 365 credentials**: Token stored at `/workspace/skills/microsoft365/tokens/ms365.tokens.default.json`. No env file at `~/.openclaw/credentials/ms365.env` — credentials are self-contained in the skill directory.

---

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
