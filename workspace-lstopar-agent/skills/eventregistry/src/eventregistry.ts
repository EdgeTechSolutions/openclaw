import https from "https";

interface EventRegistryConfig {
  apiKey: string;
  baseUrl?: string;
}

interface ArticleSearchParams {
  keyword?: string | string[];
  keywordLoc?: "body" | "title" | "body,title";
  keywordOper?: "and" | "or";
  conceptUri?: string | string[];
  categoryUri?: string | string[];
  sourceUri?: string | string[];
  sourceLocationUri?: string | string[];
  authorUri?: string;
  locationUri?: string | string[];
  lang?: string | string[];
  dateStart?: string;
  dateEnd?: string;
  minSentiment?: number;
  maxSentiment?: number;
  dataType?: "news" | "blog" | "pr";
  isDuplicateFilter?: "keepAll" | "skipDuplicates";
  articlesPage?: number;
  articlesCount?: number;
  articlesSortBy?: "date" | "rel" | "sourceImportance" | "sourceAlexaGlobalRank" | "socialScore";
  articlesSortByAsc?: boolean;
  includeArticleBody?: boolean;
  includeArticleConcepts?: boolean;
  includeArticleCategories?: boolean;
  includeArticleImage?: boolean;
  includeArticleSocialScore?: boolean;
  includeArticleLinks?: boolean;
}

interface EventSearchParams {
  keyword?: string | string[];
  keywordLoc?: "body" | "title" | "body,title";
  conceptUri?: string | string[];
  categoryUri?: string | string[];
  sourceUri?: string | string[];
  locationUri?: string | string[];
  lang?: string | string[];
  dateStart?: string;
  dateEnd?: string;
  eventsPage?: number;
  eventsCount?: number;
  eventsSortBy?: "date" | "rel" | "size" | "socialScore";
  eventsSortByAsc?: boolean;
  includeEventConcepts?: boolean;
  includeEventCategories?: boolean;
  includeEventStories?: boolean;
}

interface Article {
  uri: string;
  title: string;
  body?: string;
  url: string;
  source: { uri: string; title: string };
  dateTime: string;
  date: string;
  lang: string;
  sentiment?: number;
  image?: string;
  concepts?: any[];
  categories?: any[];
}

interface ArticleSearchResult {
  articles: {
    results: Article[];
    totalResults: number;
    page: number;
    count: number;
    pages: number;
  };
}

interface Event {
  uri: string;
  title: Record<string, string>;
  summary: Record<string, string>;
  date: string;
  location?: any;
  concepts?: any[];
  categories?: any[];
  articleCounts?: Record<string, number>;
}

interface EventSearchResult {
  events: {
    results: Event[];
    totalResults: number;
    page: number;
    count: number;
    pages: number;
  };
}

interface SuggestResult {
  uri: string;
  label?: Record<string, string>;
  title?: string;
  type?: string;
}

function request(url: string, body?: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const isPost = !!body;
    const parsed = new URL(url);
    const options: https.RequestOptions = {
      hostname: parsed.hostname,
      path: parsed.pathname + parsed.search,
      method: isPost ? "POST" : "GET",
      headers: isPost ? { "Content-Type": "application/json" } : {},
    };

    const req = https.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        if (res.statusCode && res.statusCode >= 400) {
          reject(new Error(`HTTP ${res.statusCode}: ${data}`));
          return;
        }
        try {
          resolve(JSON.parse(data));
        } catch {
          reject(new Error(`Invalid JSON: ${data.slice(0, 200)}`));
        }
      });
    });
    req.on("error", reject);
    if (isPost) req.write(JSON.stringify(body));
    req.end();
  });
}

export class EventRegistryClient {
  private apiKey: string;
  private baseUrl: string;

  constructor(config: EventRegistryConfig) {
    this.apiKey = config.apiKey;
    this.baseUrl = config.baseUrl || "https://eventregistry.org/api/v1";
  }

  /**
   * Load config from file. Falls back to EVENTREGISTRY_API_KEY env var.
   */
  static fromFile(path = "/workspace/.eventregistry-config.json"): EventRegistryClient {
    try {
      const fs = require("fs");
      const config = JSON.parse(fs.readFileSync(path, "utf-8"));
      return new EventRegistryClient({ apiKey: config.apiKey });
    } catch {
      const key = process.env.EVENTREGISTRY_API_KEY;
      if (!key) throw new Error("No API key found. Set EVENTREGISTRY_API_KEY or create /workspace/.eventregistry-config.json");
      return new EventRegistryClient({ apiKey: key });
    }
  }

  // ── Article Search ──

  async searchArticles(params: ArticleSearchParams): Promise<ArticleSearchResult> {
    return request(`${this.baseUrl}/article/getArticles`, {
      apiKey: this.apiKey,
      resultType: "articles",
      articlesPage: params.articlesPage ?? 1,
      articlesCount: params.articlesCount ?? 10,
      articlesSortBy: params.articlesSortBy ?? "date",
      articlesSortByAsc: params.articlesSortByAsc ?? false,
      ...params,
    });
  }

  // ── Event Search (5 tokens/search — use sparingly on free plan) ──

  async searchEvents(params: EventSearchParams): Promise<EventSearchResult> {
    return request(`${this.baseUrl}/event/getEvents`, {
      apiKey: this.apiKey,
      resultType: "events",
      eventsPage: params.eventsPage ?? 1,
      eventsCount: params.eventsCount ?? 10,
      eventsSortBy: params.eventsSortBy ?? "date",
      eventsSortByAsc: params.eventsSortByAsc ?? false,
      ...params,
    });
  }

  // ── Trending ──

  async getTrendingConcepts(count = 10, source = "news"): Promise<any> {
    return request(`${this.baseUrl}/trending/getConceptTrendingGroups?apiKey=${this.apiKey}&source=${source}&count=${count}`);
  }

  async getTrendingCategories(count = 10, source = "news"): Promise<any> {
    return request(`${this.baseUrl}/trending/getCategoryTrendingGroups?apiKey=${this.apiKey}&source=${source}&count=${count}`);
  }

  // ── URI Resolution Helpers ──

  async suggestConcepts(prefix: string, lang = "eng"): Promise<SuggestResult[]> {
    return request(`${this.baseUrl}/suggestConceptsFast?prefix=${encodeURIComponent(prefix)}&lang=${lang}&apiKey=${this.apiKey}`);
  }

  async suggestCategories(prefix: string): Promise<SuggestResult[]> {
    return request(`${this.baseUrl}/suggestCategoriesFast?prefix=${encodeURIComponent(prefix)}&apiKey=${this.apiKey}`);
  }

  async suggestSources(prefix: string): Promise<SuggestResult[]> {
    return request(`${this.baseUrl}/suggestSourcesFast?prefix=${encodeURIComponent(prefix)}&apiKey=${this.apiKey}`);
  }

  async suggestLocations(prefix: string, lang = "eng"): Promise<SuggestResult[]> {
    return request(`${this.baseUrl}/suggestLocationsFast?prefix=${encodeURIComponent(prefix)}&lang=${lang}&apiKey=${this.apiKey}`);
  }

  // ── Convenience Methods ──

  /**
   * Get latest news articles by keyword. Simple wrapper for common use case.
   */
  async getLatestNews(keyword: string, count = 10, lang = "eng"): Promise<Article[]> {
    const result = await this.searchArticles({
      keyword,
      lang,
      articlesCount: count,
      articlesSortBy: "date",
      isDuplicateFilter: "skipDuplicates",
      includeArticleBody: true,
      includeArticleImage: true,
    });
    return result.articles.results;
  }

  /**
   * Get top headlines (most shared articles from the last 24h).
   */
  async getTopHeadlines(count = 10, lang = "eng"): Promise<Article[]> {
    const now = new Date();
    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    const fmt = (d: Date) => d.toISOString().slice(0, 10);

    const result = await this.searchArticles({
      lang,
      dateStart: fmt(yesterday),
      dateEnd: fmt(now),
      articlesCount: count,
      articlesSortBy: "socialScore",
      isDuplicateFilter: "skipDuplicates",
      includeArticleBody: false,
      includeArticleImage: true,
    });
    return result.articles.results;
  }
}

// ── CLI Entry Point ──

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === "--help") {
    console.log(`Usage: eventregistry <command> [options]

Commands:
  search <keyword>          Search articles by keyword
  events <keyword>          Search events by keyword (5 tokens)
  trending                  Get trending concepts
  trending-categories       Get trending categories
  headlines                 Get top headlines (most shared)
  suggest-concept <prefix>  Find concept URI
  suggest-source <prefix>   Find source URI
  suggest-category <prefix> Find category URI

Options:
  --count <n>      Number of results (default: 10)
  --lang <code>    Language code (default: eng)
  --sort <field>   Sort by: date, rel, socialScore (default: date)
  --from <date>    Start date (YYYY-MM-DD)
  --to <date>      End date (YYYY-MM-DD)`);
    return;
  }

  const client = EventRegistryClient.fromFile();
  const getOpt = (name: string): string | undefined => {
    const idx = args.indexOf(`--${name}`);
    return idx >= 0 ? args[idx + 1] : undefined;
  };
  const count = parseInt(getOpt("count") || "10");
  const lang = getOpt("lang") || "eng";
  const sort = getOpt("sort") as any || "date";
  const query = args.slice(1).filter(a => !a.startsWith("--") && args[args.indexOf(a) - 1]?.startsWith("--") === false).join(" ") || args[1];

  switch (command) {
    case "search": {
      const result = await client.searchArticles({
        keyword: query,
        lang,
        articlesCount: count,
        articlesSortBy: sort,
        isDuplicateFilter: "skipDuplicates",
        includeArticleBody: false,
        includeArticleImage: true,
        dateStart: getOpt("from"),
        dateEnd: getOpt("to"),
      });
      const articles = result.articles.results;
      console.log(`Found ${result.articles.totalResults} articles (showing ${articles.length}):\n`);
      for (const a of articles) {
        console.log(`[${a.date}] ${a.title}`);
        console.log(`  Source: ${a.source.title} | Sentiment: ${a.sentiment ?? "N/A"}`);
        console.log(`  URL: ${a.url}\n`);
      }
      break;
    }
    case "events": {
      const result = await client.searchEvents({
        keyword: query,
        lang,
        eventsCount: count,
        eventsSortBy: sort,
        includeEventConcepts: true,
      });
      const events = result.events.results;
      console.log(`Found ${result.events.totalResults} events (showing ${events.length}):\n`);
      for (const e of events) {
        const title = e.title?.eng || Object.values(e.title)[0] || "Untitled";
        console.log(`[${e.date}] ${title}`);
        if (e.summary?.eng) console.log(`  ${e.summary.eng.slice(0, 200)}...`);
        console.log();
      }
      break;
    }
    case "trending": {
      const result = await client.getTrendingConcepts(count);
      console.log(JSON.stringify(result, null, 2));
      break;
    }
    case "trending-categories": {
      const result = await client.getTrendingCategories(count);
      console.log(JSON.stringify(result, null, 2));
      break;
    }
    case "headlines": {
      const articles = await client.getTopHeadlines(count, lang);
      console.log(`Top ${articles.length} headlines:\n`);
      for (const a of articles) {
        console.log(`[${a.date}] ${a.title}`);
        console.log(`  Source: ${a.source.title} | URL: ${a.url}\n`);
      }
      break;
    }
    case "suggest-concept": {
      const results = await client.suggestConcepts(query, lang);
      for (const r of results) console.log(`${r.uri}  (${r.type}) ${JSON.stringify(r.label)}`);
      break;
    }
    case "suggest-source": {
      const results = await client.suggestSources(query);
      for (const r of results) console.log(`${r.uri}  ${r.title}`);
      break;
    }
    case "suggest-category": {
      const results = await client.suggestCategories(query);
      for (const r of results) console.log(`${r.uri}`);
      break;
    }
    default:
      console.error(`Unknown command: ${command}. Run with --help for usage.`);
      process.exit(1);
  }
}

main().catch((e) => {
  console.error("Error:", e.message);
  process.exit(1);
});
