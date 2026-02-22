---
name: eventregistry
description: Search news articles, discover trending topics, and find events using the EventRegistry (NewsAPI.ai) API. Use when the user asks about news, current events, trending topics, or wants to search for articles by keyword, concept, source, category, location, or sentiment. Triggers on keywords like "news", "articles", "trending", "headlines", "events", "what's happening".
metadata:
  {
    "openclaw":
      {
        "emoji": "📰",
        "requires":
          {
            "env": ["EVENTREGISTRY_API_KEY"],
          },
      },
  }
---

# EventRegistry (NewsAPI.ai)

Search for news articles, events, and trending topics using the EventRegistry REST API.

**Free plan limits**: last 30 days of content only, limited tokens per month. Each article search = 1 token, event search = 5 tokens. Max 100 articles or 50 events per request.

## Setup

1. Register at https://newsapi.ai/register (free)
2. Get your API key from https://newsapi.ai/dashboard
3. Provide it to the agent: `EVENTREGISTRY_API_KEY=your-key-here`
4. Store in `/workspace/.eventregistry-config.json`

## Configuration

The API key is stored in `/workspace/.eventregistry-config.json`:

```json
{
  "apiKey": "YOUR_API_KEY"
}
```

Read it before every request:

```bash
EVENTREGISTRY_API_KEY=$(cat /workspace/.eventregistry-config.json | python3 -c "import sys,json; print(json.load(sys.stdin)['apiKey'])")
```

## Base URL

All requests go to: `https://eventregistry.org/api/v1/`

---

## Search Articles

**Endpoint**: `POST https://eventregistry.org/api/v1/article/getArticles`

```bash
curl -s -X POST "https://eventregistry.org/api/v1/article/getArticles" \
  -H "Content-Type: application/json" \
  -d '{
    "apiKey": "API_KEY",
    "keyword": "artificial intelligence",
    "keywordLoc": "body",
    "lang": "eng",
    "dateStart": "2026-02-01",
    "dateEnd": "2026-02-21",
    "articlesPage": 1,
    "articlesCount": 10,
    "articlesSortBy": "date",
    "articlesSortByAsc": false,
    "resultType": "articles",
    "includeArticleBody": true,
    "includeArticleConcepts": true,
    "includeArticleCategories": true
  }'
```

### Search Parameters

| Parameter | Description |
|-----------|-------------|
| `keyword` | Keywords to search (string or array) |
| `keywordLoc` | Where to search: `body`, `title`, or `body,title` |
| `keywordOper` | `and` (all keywords) or `or` (any keyword) |
| `conceptUri` | Filter by concept URI (e.g. `http://en.wikipedia.org/wiki/Google`) |
| `categoryUri` | Filter by category (e.g. `news/Business`) |
| `sourceUri` | Filter by source (e.g. `bbc.co.uk`) |
| `sourceLocationUri` | Filter by source location |
| `authorUri` | Filter by author |
| `locationUri` | Filter by event location |
| `lang` | Article language (`eng`, `deu`, `fra`, `slv`, etc.) |
| `dateStart` | Start date (YYYY-MM-DD) |
| `dateEnd` | End date (YYYY-MM-DD) |
| `minSentiment` | Min sentiment (-1 to 1) |
| `maxSentiment` | Max sentiment (-1 to 1) |
| `dataType` | `news`, `blog`, or `pr` |
| `isDuplicateFilter` | `keepAll`, `skipDuplicates` |
| `articlesPage` | Page number (1-indexed) |
| `articlesCount` | Results per page (max 100) |
| `articlesSortBy` | `date`, `rel`, `sourceImportance`, `sourceAlexaGlobalRank`, `socialScore` |
| `articlesSortByAsc` | `true` for ascending, `false` for descending |

### Result Fields

Set `includeArticle*` flags to get extra data:

| Flag | Returns |
|------|---------|
| `includeArticleBody` | Full article text |
| `includeArticleConcepts` | Mentioned entities/concepts |
| `includeArticleCategories` | Article categories |
| `includeArticleImage` | Article image URL |
| `includeArticleSocialScore` | Social media share counts |
| `includeArticleLinks` | Links from the article body |
| `includeArticleVideos` | Video links |

### Response Structure

```json
{
  "articles": {
    "results": [
      {
        "uri": "article-uri",
        "title": "Article Title",
        "body": "Full text...",
        "url": "https://source.com/article",
        "source": { "uri": "source.com", "title": "Source Name" },
        "dateTime": "2026-02-21T10:00:00Z",
        "date": "2026-02-21",
        "lang": "eng",
        "sentiment": 0.3,
        "image": "https://...",
        "concepts": [...],
        "categories": [...]
      }
    ],
    "totalResults": 1234,
    "page": 1,
    "count": 10,
    "pages": 124
  }
}
```

---

## Search Events

**Endpoint**: `POST https://eventregistry.org/api/v1/event/getEvents`

Events are clusters of articles about the same real-world event. **Costs 5 tokens per search.**

```bash
curl -s -X POST "https://eventregistry.org/api/v1/event/getEvents" \
  -H "Content-Type: application/json" \
  -d '{
    "apiKey": "API_KEY",
    "keyword": "earthquake",
    "lang": "eng",
    "eventsPage": 1,
    "eventsCount": 10,
    "eventsSortBy": "date",
    "resultType": "events",
    "includeEventConcepts": true,
    "includeEventCategories": true
  }'
```

**Note**: Use sparingly on free plan (5 tokens per search vs 1 for articles).

---

## Trending Concepts

**Endpoint**: `GET https://eventregistry.org/api/v1/trending/getConceptTrendingGroups`

```bash
curl -s "https://eventregistry.org/api/v1/trending/getConceptTrendingGroups?apiKey=API_KEY&source=news&count=10"
```

Returns currently trending people, organizations, locations, and topics in the news.

---

## Trending Categories

**Endpoint**: `GET https://eventregistry.org/api/v1/trending/getCategoryTrendingGroups`

```bash
curl -s "https://eventregistry.org/api/v1/trending/getCategoryTrendingGroups?apiKey=API_KEY&source=news&count=10"
```

---

## Resolve URIs (Helper Endpoints)

Before filtering by concept, category, or source, resolve their URIs:

### Suggest Concepts
```bash
curl -s "https://eventregistry.org/api/v1/suggestConceptsFast?prefix=Google&lang=eng&apiKey=API_KEY"
```

### Suggest Categories
```bash
curl -s "https://eventregistry.org/api/v1/suggestCategoriesFast?prefix=business&apiKey=API_KEY"
```

### Suggest Sources
```bash
curl -s "https://eventregistry.org/api/v1/suggestSourcesFast?prefix=bbc&apiKey=API_KEY"
```

### Get Location URI
```bash
curl -s "https://eventregistry.org/api/v1/suggestLocationsFast?prefix=London&lang=eng&apiKey=API_KEY"
```

---

## Free Plan Constraints

- **Last 30 days only** — no archive access
- **Token budget** — monitor via https://newsapi.ai/dashboard
- **Token costs**:
  - Article search: 1 token per page
  - Event search: 5 tokens per page
  - Trending: check dashboard for current costs
- **Max per request**: 100 articles or 50 events
- **Rate limit**: minimum 0.5s between requests
- **No commercial use** on free plan

## Tips

- Use `articlesSortBy: "date"` for latest news
- Use `articlesSortBy: "socialScore"` for most-shared articles
- Use `isDuplicateFilter: "skipDuplicates"` to remove duplicate articles
- Use `keywordLoc: "title"` for more precise matches
- Always check `totalResults` to know if there are more pages
- Prefer article search over event search to conserve tokens
- Set `articlesCount: 10` or less for summaries to save tokens
