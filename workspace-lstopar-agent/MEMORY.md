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

### **Tool Preferences by Topic**
- **Personal chat**: Use the **gog skill** (Google Workspace CLI) for email, calendar, and drive operations — not Microsoft 365 tools.

---

### **Trading 212 Balance Policy**
- **Always fetch the latest balance** from the Trading 212 tool if the last check was **older than 5 minutes**.
- Do **not** rely on cached or previously stored data for balance inquiries.
---

### **Personal Email Categories & Auto-Archive Policy**

The **Nightly Personal Email Categorizer** cron job runs every night at 05:00 Europe/Ljubljana and:
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
| Revolut | No |
| Forums | No |
| Calendar / Zoom / Amazon | No |
| Other | No |

3. Posts a grouped summary with links to each email to Telegram topic `1299` (`#comm @personal`).
