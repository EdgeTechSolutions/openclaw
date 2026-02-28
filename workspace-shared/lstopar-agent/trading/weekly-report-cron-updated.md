# Updated Weekly Trading Portfolio Report — Cron Job

**Job ID:** `c115a6e8-94b9-49f8-ba4b-f6de8ad10305`

## Changes
- Schedule: `0 18 * * 5` (Friday 18:00 CET, was 17:00)
- Added: retry logic, week-over-week, dividends, sector breakdown, split summary + full report, inline buttons, Google Drive upload

## Updated Prompt

```
## Weekly Trading Portfolio Report

### Step 1 — Fetch Portfolio Data (with retry)

Fetch current portfolio from Trading 212:
```bash
node /workspace/skills/trading212/dist/trading212.js positions
node /workspace/skills/trading212/dist/trading212.js account
node /workspace/skills/trading212/dist/trading212.js dividends
```

**Retry logic:** If any Trading 212 API call fails:
1. Wait 30 seconds, retry once.
2. If it fails again, wait 5 minutes, retry once more.
3. If still failing, post this to Telegram topic 701 in chat 8403014547:
   `⚠️ Weekly Trading Report — Trading 212 API is down. Will retry next hour.`
   Then stop. Do NOT generate a report with stale or missing data.

### Step 2 — Week-over-Week Comparison

Read the previous week's snapshot from `/workspace/shared/lstopar-agent/trading/weekly-snapshot-latest.json`.

If the file exists, calculate:
- Total portfolio value change (€ and %)
- Per-position change (€ and %)
- New positions opened this week
- Positions closed this week
- Best and worst performers of the week

If the file doesn't exist, note "First week — no comparison data available" and skip week-over-week section.

**After analysis, save the current snapshot:**
Write the current portfolio state (all positions with quantities, avg prices, current values, P&L) to `/workspace/shared/lstopar-agent/trading/weekly-snapshot-latest.json` as JSON. Also write a dated copy to `/workspace/shared/lstopar-agent/trading/weekly-snapshot-YYYY-MM-DD.json`.

### Step 3 — Sector & Geographic Breakdown

Classify each holding by:
- **Sector**: Technology, Energy, Defense/Aerospace, Healthcare, Financials, Industrials, Consumer, Commodities, Other
- **Geography**: Europe, North America, Global/Other

Calculate allocation percentages for each sector and region. Flag any sector >30% as concentration risk. Flag any single position >15% of portfolio.

Present as a table in the full report.

### Step 4 — Dividend Calendar

For all current holdings, search for upcoming ex-dividend dates in the next 14 days using web search. For each upcoming dividend:
- Stock name/ticker
- Ex-dividend date
- Dividend amount (per share and estimated total based on holdings)
- Payment date (if available)

If no dividends are upcoming, note "No ex-dividend dates in the next 2 weeks."

### Step 5 — Macroeconomic Context & Events

Use EventRegistry and web search to gather:
1. Key macro trends this week (interest rates, inflation data, GDP, currency moves)
2. Geopolitical events affecting markets
3. Sector-specific news relevant to holdings
4. Earnings reports from holdings this past week + upcoming next week

### Step 6 — Analysis & Recommendations

Based on all data gathered:
1. **Portfolio health assessment** — overall status, risk level, diversification quality
2. **Positions needing attention** — down >10%, deteriorating fundamentals, or changed thesis
3. **Actionable recommendations** — specific actions with conviction levels (High/Medium/Low)
4. **New position suggestions** — 3-5 ideas with ticker, rationale, suggested allocation, key risks, conviction level

### Step 7 — Write Full Report

Write a comprehensive markdown report to `/workspace/shared/lstopar-agent/trading/weekly-report-YYYY-MM-DD.md` containing all sections above with tables and detailed analysis.

Then upload this file to Google Drive folder ID `1Jd8p3RYw0a8QnJcHdQjN-2CCCU9efZgx` using the gog skill:
```bash
gog drive upload /workspace/shared/lstopar-agent/trading/weekly-report-YYYY-MM-DD.md --parent 1Jd8p3RYw0a8QnJcHdQjN-2CCCU9efZgx
```

Capture the Google Drive file URL/ID from the upload response.

### Step 8 — Post Telegram Summary

Post a SHORT summary (max 6-8 lines) to Telegram topic 701 in chat 8403014547 using the message tool. Format:

```
📈 Weekly Portfolio Report — {date}

💰 Portfolio: €{value} ({+/-}{wow_change}% wow)
📊 Best: {ticker} {+%} | Worst: {ticker} {-%}
🏗️ Sectors: {top 3 sectors with %}
💸 Dividends: {count upcoming or "none next 2w"}
⚠️ Attention: {1-2 key alerts or "all clear"}
🎯 Top pick: {best new suggestion with 1-line rationale}
```

Include inline buttons and the Google Drive link:
```json
{
  "action": "send",
  "to": "8403014547",
  "message": "<your summary>\n\n📄 Full report: <google drive link>",
  "threadId": "701",
  "buttons": [[{"text": "📄 Full Report", "callback_data": "view_full_report"}, {"text": "🔄 Mid-week Update", "callback_data": "run_midweek_check"}]]
}
```

Do NOT post to any other Telegram topic.
```

---

## New: Mid-Week Check (Wednesday 18:00)

**Create as a NEW cron job.**

Schedule: `0 18 * * 3` (Wednesday 18:00 CET)
Model: `anthropic/claude-sonnet-4-6` (cheaper, lighter task)
Thinking: `on`

```
## Mid-Week Portfolio Check

### Step 1 — Fetch Portfolio Data

Fetch current portfolio from Trading 212:
```bash
node /workspace/skills/trading212/dist/trading212.js positions
node /workspace/skills/trading212/dist/trading212.js account
```

If API fails, wait 30 seconds and retry once. If still failing, post "⚠️ Mid-week check — T212 API down" to Telegram topic 701 chat 8403014547 and stop.

### Step 2 — Compare to Friday Snapshot

Read `/workspace/shared/lstopar-agent/trading/weekly-snapshot-latest.json`.

Calculate:
- Portfolio value change since Friday (€ and %)
- Positions down >5% since Friday — flag these
- Positions up >5% since Friday — note these
- Any positions hitting new lows

### Step 3 — Quick Macro Scan

Use web search for:
- Major market moves this week (indices, notable stocks)
- Any breaking macro news (rate decisions, inflation data, geopolitical events)
- Earnings from holdings this week

Keep this brief — 3-5 bullet points max.

### Step 4 — Post to Telegram

Post to topic 701 in chat 8403014547:

```
🔄 Mid-Week Check — {date}

💰 Portfolio: €{value} ({+/-}% since Friday)
🔴 Down >5%: {tickers or "none"}
🟢 Up >5%: {tickers or "none"}
📰 Key news: {1-2 top headlines}
```

Use the message tool:
```json
{
  "action": "send",
  "to": "8403014547",
  "message": "<your summary>",
  "threadId": "701"
}
```

Do NOT post to any other Telegram topic. Keep it short — this is a check-in, not a full report.
```
