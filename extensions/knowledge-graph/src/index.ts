/**
 * Knowledge Graph Plugin for OpenClaw
 *
 * Stores facts as (subject, relation, object) triples via the Knowledge Graph
 * REST API (Django / Memgraph). Fact extraction is handled externally by the
 * Darwin agent (cron job).
 *
 * Features:
 * - Delegates all persistence to the remote API
 * - Server-side vector embeddings (no local embedding key required)
 * - Agent tool for querying and managing the graph
 */

import { KnowledgeGraphApiClient } from "./api-client";

interface PluginConfig {
  apiBaseUrl: string;
  apiKey?: string;
  minConfidence: number;
}

const DEFAULT_CONFIG: PluginConfig = {
  apiBaseUrl: "http://localhost:8000",
  apiKey: "",
  minConfidence: 0.6,
};

export default function register(api: any) {
  const pluginConfig: PluginConfig = {
    ...DEFAULT_CONFIG,
    ...(api.config?.plugins?.entries?.["knowledge-graph"]?.config || {}),
  };

  const client = new KnowledgeGraphApiClient({
    baseUrl: pluginConfig.apiBaseUrl,
    apiKey: pluginConfig.apiKey || undefined,
  });

  console.log("[knowledge-graph] Plugin ready — using API at", pluginConfig.apiBaseUrl);

  // ─── AGENT TOOL ───────────────────────────────────────────

  api.registerTool({
    name: "knowledge_graph",
    label: "Knowledge Graph",
    description:
      "Search and manage the knowledge graph. Stores facts extracted from conversations as (subject, relation, object) triples with vector embeddings for semantic search.",
    parameters: {
      type: "object",
      properties: {
        action: {
          type: "string",
          enum: ["search", "entity", "relation", "stats", "recent", "similar", "merge", "add", "mentions"],
          description:
            "Action to perform: search (semantic via mentions), entity (by name), relation (by type), stats, recent (latest facts), similar (find similar entities via mentions), merge (deduplicate entities), add (manually add a fact), mentions (list mentions for an entity)",
        },
        query: {
          type: "string",
          description: "Natural language search query (for action=search)",
        },
        entity: {
          type: "string",
          description: "Entity name to look up (for action=entity/similar/mentions)",
        },
        relation: {
          type: "string",
          description: "Relation type to filter (for action=relation)",
        },
        subject: {
          type: "string",
          description: "Subject entity (for action=add)",
        },
        subject_type: {
          type: "string",
          description: "Subject entity type (for action=add)",
        },
        object: {
          type: "string",
          description: "Object entity (for action=add)",
        },
        object_type: {
          type: "string",
          description: "Object entity type (for action=add)",
        },
        context: {
          type: "string",
          description: "Optional context sentence for the fact (for action=add)",
        },
        merge_from: {
          type: "string",
          description: "Entity to merge FROM (for action=merge)",
        },
        merge_into: {
          type: "string",
          description: "Entity to merge INTO (for action=merge)",
        },
        limit: {
          type: "number",
          description: "Max results (default 10)",
        },
      },
      required: ["action"],
    },
    async execute(_toolCallId: string, params: any) {
      const json = (result: unknown) => ({
        content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }],
        details: result,
      });

      const limit: number = params.limit || 10;

      try {
        switch (params.action) {
          case "search": {
            if (!params.query) return json({ error: "query is required for search" });
            const result = await client.search(params.query, limit);
            return json(result);
          }

          case "entity": {
            if (!params.entity) return json({ error: "entity name is required" });
            const result = await client.entity(params.entity, limit);
            return json(result);
          }

          case "relation": {
            if (!params.relation) return json({ error: "relation type is required" });
            const result = await client.relation(params.relation, limit);
            return json(result);
          }

          case "stats": {
            const result = await client.stats();
            return json(result);
          }

          case "recent": {
            const result = await client.recent(limit);
            return json(result);
          }

          case "similar": {
            if (!params.entity) return json({ error: "entity name is required" });
            const result = await client.similar(params.entity, limit);
            return json(result);
          }

          case "merge": {
            if (!params.merge_from || !params.merge_into) {
              return json({ error: "merge_from and merge_into are required" });
            }
            const result = await client.merge(params.merge_from, params.merge_into);
            return json(result);
          }

          case "add": {
            if (!params.subject || !params.relation || !params.object) {
              return json({ error: "subject, relation, and object are required" });
            }
            const result = await client.add(
              params.subject,
              params.subject_type || "unknown",
              params.relation,
              params.object,
              params.object_type || "unknown",
              params.context,
            );
            return json(result);
          }

          case "mentions": {
            if (!params.entity) return json({ error: "entity name is required" });
            const result = await client.mentions(params.entity, limit);
            return json(result);
          }

          default:
            return json({
              error: `Unknown action: ${params.action}. Use: search, entity, relation, stats, recent, similar, merge, add, mentions`,
            });
        }
      } catch (err: any) {
        return json({ error: err.message });
      }
    },
  });

  console.log("[knowledge-graph] Plugin ready (Darwin-mode: extraction handled by scheduled agent)");
}
