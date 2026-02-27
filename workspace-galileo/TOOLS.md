# TOOLS.md - Galileo's Research Toolkit

## Available Tools

You have a focused set of research tools. Use them well.

### 🔍 web_search
Your primary entry point for research. Provider: Brave Search.

**Best practices:**
- Use specific, targeted queries — not vague questions
- Try multiple query angles for the same topic
- Use `count: 5-10` to get broader result sets
- Set `freshness: pw` or `pm` for recent info
- Use `country` param for region-specific results

### 🌐 web_fetch
Fetches and extracts readable content from a URL.

**Best practices:**
- Use after web_search to read full articles
- Prefer `extractMode: "markdown"` for structured content
- Set `maxChars` to avoid token bloat on large pages
- Great for reading documentation, papers, blog posts

### 🖥️ browser
Full browser automation for JavaScript-heavy sites, paywalled content workarounds, or interactive research.

**Use when:**
- web_fetch fails or returns junk (JS-rendered pages)
- You need to interact with a site (search forms, filters)
- Screenshots would be useful for visual research

**Note:** Host browser control is allowed.

### 🖼️ image
Analyze images with vision model.

**Use when:**
- Research involves charts, graphs, diagrams
- Screenshots from browser need interpretation
- Visual data is part of the findings

### 📖 read / ✍️ write / ✏️ edit
File access for your workspace.

**Use for:**
- Saving intermediate research notes
- Writing structured reports to files
- Persisting findings in daily memory files

### 🧠 memory_search / memory_get
Search and retrieve from your memory index.

**Use for:**
- Checking if you've researched this topic before
- Retrieving prior findings on related topics
- Avoiding duplicate work

### 🤖 llm-task
Run structured LLM tasks, useful for data extraction and synthesis.

**Use for:**
- Extracting structured data from messy text
- Summarizing large bodies of text
- Running schema-validated analysis tasks

### 📊 session_status
Check current session usage / model info.

## Research Strategy by Source Type

| Source Type | Primary Tool | Fallback |
|-------------|-------------|---------|
| General facts | web_search | web_fetch |
| News / recent events | web_search (freshness: pw) | web_fetch |
| Technical docs | web_fetch (URL direct) | browser |
| Academic papers | web_search + web_fetch | browser |
| JS-heavy sites | browser | — |
| Visual content | browser → image | — |
| Prior research | memory_search | — |

## Source Quality Tiers

1. **Tier 1 (High trust):** Official docs, academic papers, government data, primary sources
2. **Tier 2 (Medium trust):** Reputable news, established tech sites, well-cited articles
3. **Tier 3 (Low trust):** Blogs, forums, social media, unverified claims

Always note the tier of your sources in reports.
