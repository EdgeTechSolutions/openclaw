/**
 * HTTP client for the Knowledge Graph Django REST API.
 *
 * Wraps every endpoint as a typed async method so that index.ts
 * never has to construct URLs or handle raw fetch responses directly.
 *
 * All methods throw an Error (with the API error message included) on
 * non-2xx responses.
 */

// ─── Response types (mirror Django serializers) ──────────────────────────────

export interface Fact {
  subject: string;
  subject_type: string;
  relation: string;
  object: string;
  object_type: string;
  confidence: number;
  source: string;
  context: string;
  created_at: string;
  similarity?: number;
}

export interface EntityRecord {
  id: string;
  name: string;
  type: string;
  properties: Record<string, any>;
  created_at: string;
  updated_at: string;
  similarity?: number;
}

export interface MentionRecord {
  id: string;
  entity_id: string;
  mention_text: string;
  source: string;
  source_id: string;
  created_at: string;
}

export interface StatsResult {
  entities: number;
  relations: number;
  mentions: number;
}

export interface SearchResult {
  results: Fact[];
  count: number;
}

export interface EntityResult {
  entity: string;
  facts: Fact[];
  count: number;
}

export interface RelationResult {
  relation: string;
  facts: Fact[];
  count: number;
}

export interface RecentResult {
  facts: Fact[];
  count: number;
}

export interface SimilarResult {
  entity: string;
  similar: EntityRecord[];
  count: number;
}

export interface MentionsResult {
  entity: string;
  mentions: MentionRecord[];
  count: number;
}

export interface AddFactResult {
  success: boolean;
  fact: string;
  subject_id: string;
  object_id: string;
  relation_id: string;
}

export interface MergeResult {
  success: boolean;
  message: string;
}

// ─── Client ──────────────────────────────────────────────────────────────────

export interface ApiClientConfig {
  baseUrl: string;
  apiKey?: string;
}

export class KnowledgeGraphApiClient {
  private readonly baseUrl: string;
  private readonly headers: Record<string, string>;

  constructor(config: ApiClientConfig) {
    // Trim trailing slash so paths like /api/search stay clean.
    this.baseUrl = config.baseUrl.replace(/\/$/, "");
    this.headers = { "Content-Type": "application/json" };
    if (config.apiKey) {
      this.headers["Authorization"] = `Bearer ${config.apiKey}`;
    }
  }

  // ─── Private helpers ───────────────────────────────────────────────────────

  private async get<T>(path: string, params: Record<string, string | number> = {}): Promise<T> {
    const url = new URL(`${this.baseUrl}${path}`);
    for (const [k, v] of Object.entries(params)) {
      url.searchParams.set(k, String(v));
    }
    const resp = await fetch(url.toString(), { method: "GET", headers: this.headers });
    return this.handleResponse<T>(resp);
  }

  private async post<T>(path: string, body: unknown): Promise<T> {
    const resp = await fetch(`${this.baseUrl}${path}`, {
      method: "POST",
      headers: this.headers,
      body: JSON.stringify(body),
    });
    return this.handleResponse<T>(resp);
  }

  private async handleResponse<T>(resp: Response): Promise<T> {
    if (resp.ok) {
      return resp.json() as Promise<T>;
    }
    let message = `HTTP ${resp.status}`;
    try {
      const body = await resp.json() as any;
      message = body?.error ?? body?.detail ?? JSON.stringify(body);
    } catch {
      message = await resp.text().catch(() => message);
    }
    throw new Error(`Knowledge Graph API error: ${message}`);
  }

  // ─── Public API methods ────────────────────────────────────────────────────

  /** POST /api/search — semantic search using server-side embeddings. */
  search(query: string, limit: number = 10): Promise<SearchResult> {
    return this.post<SearchResult>("/api/search", { query, limit });
  }

  /** GET /api/entity — facts touching an entity (substring match). */
  entity(entity: string, limit: number = 20): Promise<EntityResult> {
    return this.get<EntityResult>("/api/entity", { entity, limit });
  }

  /** GET /api/relation — facts filtered by relation type. */
  relation(relation: string, limit: number = 20): Promise<RelationResult> {
    return this.get<RelationResult>("/api/relation", { relation, limit });
  }

  /** GET /api/stats — entity / relation / mention counts. */
  stats(): Promise<StatsResult> {
    return this.get<StatsResult>("/api/stats");
  }

  /** GET /api/recent — latest facts ordered by creation time. */
  recent(limit: number = 50): Promise<RecentResult> {
    return this.get<RecentResult>("/api/recent", { limit });
  }

  /** POST /api/similar — entities semantically similar to a name string. */
  similar(entity: string, limit: number = 5): Promise<SimilarResult> {
    return this.post<SimilarResult>("/api/similar", { entity, limit });
  }

  /** POST /api/merge — merge merge_from entity into merge_into. */
  merge(merge_from: string, merge_into: string): Promise<MergeResult> {
    return this.post<MergeResult>("/api/merge", { merge_from, merge_into });
  }

  /** POST /api/add — upsert a (subject, relation, object) triple. */
  add(
    subject: string,
    subject_type: string,
    relation: string,
    object: string,
    object_type: string,
    context?: string,
  ): Promise<AddFactResult> {
    return this.post<AddFactResult>("/api/add", {
      subject,
      subject_type,
      relation,
      object,
      object_type,
      ...(context !== undefined ? { context } : {}),
    });
  }

  /** GET /api/mentions — mention nodes attached to an entity. */
  mentions(entity: string, limit: number = 10): Promise<MentionsResult> {
    return this.get<MentionsResult>("/api/mentions", { entity, limit });
  }
}
