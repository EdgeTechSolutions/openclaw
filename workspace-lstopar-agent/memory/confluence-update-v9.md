## Overview

OpenClaw agents can install and configure skills themselves inside their sandbox. You don't need terminal access — just tell your agent what to do via chat.

This page covers the general installation process and skill-specific setup instructions.

---

## General Installation Process

### 1. Search for the skill

Ask your agent:

> *"Search ClawHub for a [skill name] skill"*

The agent will search ClawHub and present available options.

### 2. Install the skill

Tell the agent which one to install:

> *"Install the [skill name] skill"*

The agent will install the skill definition (via ClawHub) and the required CLI tool (via npm or binary download) inside the sandbox.

### 3. Provide credentials

The agent will ask for any required credentials. Always send credentials in a **direct/private chat**, never in group channels.

### 4. Verify

Ask the agent to perform a simple operation to confirm the skill works.

---

## Skill: Confluence

### What it does

Read, create, search, and update Confluence pages and spaces.

### Installation

Tell your agent:

> *"Search ClawHub for a Confluence skill and install it"*

The agent installs the `confluence` skill definition via ClawHub and the `confluence-cli` npm package.

### Credentials

You need:

- **Email**: Your Atlassian account email
- **API Token**: Generate at https://id.atlassian.com/manage-profile/security/api-tokens

Send to the agent in a private chat:

> *"CONFLUENCE_EMAIL=you@company.com CONFLUENCE_API_TOKEN=your-token-here"*

### Verification

> *"Read this Confluence page: https://edgetech-atlassian.atlassian.net/wiki/spaces/Tools/pages/..."*

### What gets stored

- Skill definition: `/workspace/skills/confluence/`
- CLI tool: `/workspace/.npm-global/` (installed via npm)
- Credentials: `/workspace/.confluence-cli/config.json`

---

## Skill: Jira

### What it does

View, create, update, and transition Jira issues. List sprints, search with JQL, manage assignments and comments.

### Installation

Tell your agent:

> *"Search ClawHub for a Jira skill and install it"*

The agent installs the `jira` skill definition via ClawHub and downloads the `jira-cli` binary from GitHub (Go binary, not an npm package).

### Credentials

You need:

- **Email**: Your Atlassian account email
- **API Token**: Same token as Confluence — generate at https://id.atlassian.com/manage-profile/security/api-tokens

Send to the agent in a private chat:

> *"JIRA_EMAIL=you@company.com JIRA_API_TOKEN=your-token-here"*

**Note:** The `JIRA_API_TOKEN` environment variable must be available in every session. Ask the agent to add it to the sandbox env config, or configure it in `~/.openclaw/openclaw.json` under `agents.defaults.sandbox.docker.env`.

### Verification

> *"Read the latest 10 Jira tasks"*

### What gets stored

- Skill definition: `/workspace/skills/jira/`
- CLI binary: `/workspace/.npm-global/bin/jira` (downloaded from GitHub releases)
- Config: `/workspace/.config/.jira/.config.yml`
- Credentials: via `JIRA_API_TOKEN` env variable (not stored in a file)

---

## Skill: EventRegistry (NewsAPI.ai)

### What it does

Search news articles, discover trending topics, and find events from 150,000+ news sources worldwide. Powered by the EventRegistry / NewsAPI.ai platform.

### Capabilities

- **Search articles** — by keyword, concept, source, category, location, sentiment, date
- **Search events** — clustered groups of articles about the same real-world event
- **Trending concepts** — currently trending people, organizations, locations, topics
- **Trending categories** — which news categories are trending
- **Top headlines** — most shared articles from the last 24 hours

### Installation

This is a custom skill (not on ClawHub). Tell your agent:

> *"Create an EventRegistry skill using the NewsAPI.ai API"*

The agent creates a TypeScript-based skill at `/workspace/skills/eventregistry/` with a REST API client. No external CLI needed — it uses the EventRegistry HTTP API directly.

### Credentials

You need:

- **API Key**: Register for free at https://newsapi.ai/register, then find your key at https://newsapi.ai/dashboard

Send to the agent in a private chat:

> *"EVENT_REGISTRY_API_KEY=your-api-key-here"*

### Free Plan Limits

- Last **30 days of content only** (no archive access)
- Article search: **1 token** per page (max 100 articles/page)
- Event search: **5 tokens** per page (max 50 events/page) — use sparingly
- No commercial use on the free plan
- Monitor your usage at https://newsapi.ai/dashboard

### Verification

> *"List the latest 10 news headlines from EventRegistry"*

### What gets stored

- Skill definition + TypeScript source: `/workspace/skills/eventregistry/`
- Compiled JS: `/workspace/skills/eventregistry/dist/`
- Credentials: `/workspace/.eventregistry-config.json`

---

## Skill: Microsoft 365

### What it does

Access Outlook emails, Calendar events, Contacts, and OneDrive files via Microsoft Graph API. Uses the Device Code Flow for authentication (no browser redirect needed in the sandbox).

### Prerequisites (you do this once in Azure Portal)

Before telling your agent anything, set up an Azure AD app:

1. Go to [Azure Portal > App registrations](https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/RegisteredApps) and click **New registration**
2. Fill in:
   - **Name**: `OpenClaw Microsoft 365` (or anything you like)
   - **Supported account types**: *Accounts in any organizational directory and personal Microsoft accounts*
   - **Redirect URI**: Leave empty
3. Click **Register** and copy the **Application (client) ID** and **Directory (tenant) ID**
4. Go to **Authentication** > under *Advanced settings*, set **Allow public client flows** to **Yes** > click **Save**

**Important**: The "Allow public client flows" setting is required. Without it, the device code flow will fail with error `AADSTS7000218: The request body must contain client_assertion or client_secret`.

### What to tell your agent

**Step 1 — Install the skill:**

> *"Install the Microsoft 365 skill from ClawHub"*

**Step 2 — Provide your Azure app credentials (in a private chat):**

> *"Here are my Microsoft 365 credentials: Client ID: YOUR_CLIENT_ID, Tenant ID: YOUR_TENANT_ID"*

The agent saves these to `skills/microsoft365/config.default.json`.

**Step 3 — Authenticate:**

> *"Authenticate Microsoft 365"*

The agent will start the device code flow and give you a code like `DESW8HGF2`. You then:

1. Open https://microsoft.com/devicelogin in your browser
2. Enter the code
3. Sign in with your Microsoft account
4. Tell the agent "Done" when finished

**Important**: The agent needs to keep the process running long enough for you to complete the browser login. If the code expires (after ~15 minutes), just ask the agent to try again.

**Step 4 — Verify:**

> *"Show me my last 10 emails from Microsoft 365"*

### Troubleshooting

- **"client_assertion or client_secret" error**: Go to Azure Portal > your app > Authentication > enable "Allow public client flows"
- **Code expired**: Just ask the agent to retry authentication — it will generate a new code
- **Token expired after setup**: The agent auto-refreshes tokens using the stored refresh token. If refresh fails, re-authenticate
- **Tokens not persisting**: Make sure the `skills/microsoft365/tokens/` directory exists. The skill stores tokens in the skill directory, **not** in `~/.openclaw/credentials/`

### What gets stored

- Skill definition: `/workspace/skills/microsoft365/`
- Config: `skills/microsoft365/config.default.json` (client ID + tenant ID)
- Tokens: `skills/microsoft365/tokens/ms365.tokens.default.json` (access + refresh tokens)

**For other sessions**: Tokens are stored in the skill directory (`skills/microsoft365/tokens/`), not in `~/.openclaw/credentials/`. Ensure the `tokens/` directory exists.

---

## Skill: Gmail (gog CLI Alternative)

### What it does

Read, search, and send emails via Gmail API. This is a custom TypeScript wrapper that replaces the `gog` CLI, which doesn't work inside a Docker sandbox (OAuth redirect to `127.0.0.1` fails in containers).

### Prerequisites (you do this once in Google Cloud Console)

1. Go to [Google Cloud Console > APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)
2. Create an **OAuth 2.0 Client ID** with application type **Desktop app**
3. Download the credentials JSON file

### What to tell your agent

**Step 1 — Send the OAuth credentials JSON file** to the agent in a private chat.

The agent saves it to `.config/gogcli/credentials.json`.

**Step 2 — Start the OAuth flow:**

> *"Authenticate Gmail"*

The agent will generate an auth URL. You then:

1. Open the auth URL in your browser
2. Sign in and authorize
3. The browser will redirect to `http://127.0.0.1:XXXXX/oauth2/callback?code=...&state=...` — this page will fail to load (that's normal)
4. **Copy the full URL from the address bar** and paste it back to the agent

The agent extracts the auth code from the URL and exchanges it for tokens.

**Step 3 — Verify:**

> *"Show me my latest Gmail emails"*

### What gets stored

- Skill definition + TypeScript source: `/workspace/skills/gmail/`
- Compiled JS: `skills/gmail/dist/gmail.js`
- OAuth credentials: `.config/gogcli/credentials.json`
- Tokens: `.config/gogcli/tokens/token-luka.stopar@gmail.com.json`

---

## Sandbox Requirements

For skill installation to work, the sandbox needs:

- **Network access** — sandbox network must not be `"none"` in the OpenClaw config
- **npm available** — Node.js and npm must be present in the sandbox image (for npm-based CLIs)
- **PATH configured** — the install directory must be in PATH

### PATH Configuration

The agent installs tools to `/workspace/.npm-global/` which persists across container reboots. To make them available automatically, add to your OpenClaw config (`~/.openclaw/openclaw.json`):

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "docker": {
          "env": {
            "JIRA_API_TOKEN": "your-jira-api-token",
            "PATH": "/workspace/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
          }
        }
      }
    }
  }
}
```

## Persistence

Everything lives in `/workspace/` (bind-mounted to the host), so it survives container reboots and recreations:

- **Skill definitions**: `/workspace/skills/<skill-name>/`
- **CLI tools**: `/workspace/.npm-global/`
- **Credentials**: tool-specific config files in the workspace

## Security Notes

- Always send credentials in a **private/direct chat**, never in group channels
- The agent stores credentials only in tool-specific config files, not in memory or log files
- You can find more skills at clawhub.com