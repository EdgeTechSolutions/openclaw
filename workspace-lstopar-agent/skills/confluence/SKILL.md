---
name: confluence
description: Search and manage Confluence pages and spaces using confluence-cli and CQL. Read documentation, create pages, and navigate spaces.
homepage: https://github.com/pchuri/confluence-cli
metadata: {"clawdbot":{"emoji":"📄","primaryEnv":"CONFLUENCE_TOKEN","requires":{"bins":["confluence"],"env":["CONFLUENCE_TOKEN"]},"install":[{"id":"npm","kind":"node","package":"confluence-cli","bins":["confluence"],"label":"Install confluence-cli (npm)"}]}}
---

# Confluence

Search and manage Confluence pages using confluence-cli and CQL (Confluence Query Language).

## REQUIRED: First-Time Setup

Before using this skill, complete these steps:

**Step 1: Install the CLI**

```bash
npm install -g confluence-cli
```

**Step 2: Get an API token**

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a label (e.g., "confluence-cli")
4. Copy the token

**Step 3: Configure the CLI**

```bash
confluence init
```

When prompted, enter:
- **Domain**: `yourcompany.atlassian.net` (without https://)
- **Email**: Your Atlassian account email
- **API token**: Paste the token from Step 2

**Step 4: Verify setup**

```bash
confluence spaces
```

If you see your spaces listed, you're ready to use Confluence.

---

## CQL Search (Preferred)

Use the CQL search script for advanced queries. Script location: `scripts/cql-search.sh` (relative to this skill directory).

```bash
bash <skill-dir>/scripts/cql-search.sh '<CQL query>' [--limit N] [--start N] [--expand fields]
```

### CQL Examples

**Search by text content:**
```bash
bash <skill-dir>/scripts/cql-search.sh 'text ~ "deployment guide"'
```

**Search in a specific space:**
```bash
bash <skill-dir>/scripts/cql-search.sh 'type = page AND space = DEV'
```

**Search by label:**
```bash
bash <skill-dir>/scripts/cql-search.sh 'label = "architecture" AND type = page'
```

**Search by creator or date:**
```bash
bash <skill-dir>/scripts/cql-search.sh 'creator = currentUser() AND created > "2025-01-01"'
```

**Recently modified pages:**
```bash
bash <skill-dir>/scripts/cql-search.sh 'type = page AND lastModified > "2025-06-01" ORDER BY lastModified DESC' --limit 10
```

**Full-text with body expansion (to read content inline):**
```bash
bash <skill-dir>/scripts/cql-search.sh 'text ~ "API reference"' --limit 5 --expand body.storage
```

**Pagination:**
```bash
bash <skill-dir>/scripts/cql-search.sh 'space = DEV' --limit 25 --start 25
```

### CQL Quick Reference

| Field | Operators | Example |
|---|---|---|
| `text` | `~` (contains) | `text ~ "search term"` |
| `title` | `=`, `~` | `title = "Exact Title"` or `title ~ "partial"` |
| `space` | `=`, `in` | `space = DEV` or `space in (DEV, PROD)` |
| `type` | `=` | `type = page`, `type = blogpost`, `type = attachment` |
| `label` | `=`, `in` | `label = "important"` |
| `creator` | `=` | `creator = currentUser()` |
| `created` | `>`, `<`, `>=`, `<=` | `created > "2025-01-01"` |
| `lastModified` | `>`, `<`, `>=`, `<=` | `lastModified > now("-7d")` |
| `ancestor` | `=` | `ancestor = 123456` (pages under a parent) |
| `parent` | `=` | `parent = 123456` (direct children only) |
| `id` | `=`, `in` | `id = 123456` or `id in (111, 222)` |

**Operators:** `AND`, `OR`, `NOT`, `ORDER BY ... ASC/DESC`

**Functions:** `currentUser()`, `now()`, `now("-7d")`, `now("+1M")`

**Text modifiers:** `~` fuzzy, `"exact phrase"`, `*` wildcard

Full CQL docs: https://developer.atlassian.com/server/confluence/advanced-searching-using-cql/

---

## Basic CLI Commands

### Search Pages (simple keyword)

```bash
confluence search "deployment guide"
```

### Read Page

```bash
confluence read <page-id>
```

Page IDs are in the URL: `https://yoursite.atlassian.net/wiki/spaces/SPACE/pages/123456/Title` → ID is `123456`

### Get Page Info

```bash
confluence info <page-id>
```

### Find Page by Title

```bash
confluence find "Page Title"
```

### List Spaces

```bash
confluence spaces
```

### Create Page

```bash
confluence create "Page Title" SPACEKEY --body "Page content here"
```

### Create Child Page

```bash
confluence create-child "Child Page Title" <parent-page-id> --body "Content"
```

Or from a file:

```bash
confluence create-child "Page Title" <parent-id> --file content.html --format storage
```

### Update Page

```bash
confluence update <page-id> --body "Updated content"
```

Or from a file:

```bash
confluence update <page-id> --file content.html --format storage
```

### List Child Pages

```bash
confluence children <page-id>
```

### Export Page with Attachments

```bash
confluence export <page-id> --output ./exported-page/
```

## Tips

- Domain in config should NOT include `https://` - just `yourcompany.atlassian.net`
- Use `--format storage` when content is in Confluence storage format (HTML-like)
- Page IDs are numeric and found in page URLs
- Config is stored at `~/.confluence-cli/config.json`
- **Prefer CQL search** over basic `confluence search` for better control and filtering
- CQL `text ~` searches page body content; `title ~` searches titles only
- Use `--expand body.storage` to get page content inline with search results (heavy — use small `--limit`)
