/**
 * Knowledge Graph Plugin for OpenClaw
 *
 * Stores facts as (subject, relation, object) triples in SQLite.
 * Fact extraction is handled externally by the Darwin agent (cron job).
 *
 * Features:
 * - SQLite-backed knowledge graph
 * - Vector embeddings for semantic search (Gemini or OpenAI)
 * - Agent tool for querying and managing the graph
 */

import { createDB, type KnowledgeGraphDB } from "./db";
import { getEmbedding, type EmbeddingConfig } from "./embeddings";

interface PluginConfig {
  embeddingProvider: "gemini" | "openai";
  embeddingApiKey: string;
  embeddingModel: string;
  embeddingDimensions: number;
  minConfidence: number;
  dbPath: string;
}

const DEFAULT_CONFIG: PluginConfig = {
  embeddingProvider: "gemini",
  embeddingApiKey: "",
  embeddingModel: "text-embedding-004",
  embeddingDimensions: 768,
  minConfidence: 0.6,
  dbPath: "/workspace/knowledge-graph.db",
};

export default function register(api: any) {
  const pluginConfig: PluginConfig = {
    ...DEFAULT_CONFIG,
    ...(api.config?.plugins?.entries?.["knowledge-graph"]?.config || {}),
  };

  if (!pluginConfig.embeddingApiKey) {
    console.warn(
      "[knowledge-graph] No embeddingApiKey configured. Vector search will be disabled."
    );
  }

  const db: KnowledgeGraphDB = createDB(pluginConfig.dbPath);
  db.init();
  console.log("[knowledge-graph] Database initialized at", pluginConfig.dbPath);

  const embeddingConfig: EmbeddingConfig = {
    provider: pluginConfig.embeddingProvider,
    apiKey: pluginConfig.embeddingApiKey,
    model: pluginConfig.embeddingModel,
    dimensions: pluginConfig.embeddingDimensions,
  };

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
          description: "Entity name to look up (for action=entity/similar)",
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

      const limit = params.limit || 10;

      switch (params.action) {
        case "search": {
          if (!params.query) return json({ error: "query is required for search" });
          if (!pluginConfig.embeddingApiKey) {
            return json({ error: "Embedding API key not configured. Use action=entity or action=relation instead." });
          }
          const queryEmb = await getEmbedding(params.query, embeddingConfig);
          const results = db.searchByVector(queryEmb, limit);
          return json({ results, count: results.length });
        }

        case "entity": {
          if (!params.entity) return json({ error: "entity name is required" });
          const facts = db.searchByEntity(params.entity, limit);
          return json({ entity: params.entity, facts, count: facts.length });
        }

        case "relation": {
          if (!params.relation) return json({ error: "relation type is required" });
          const facts = db.searchByRelation(params.relation, limit);
          return json({ relation: params.relation, facts, count: facts.length });
        }

        case "stats": {
          const dbStats = db.getStats();
          return json({
            entities: dbStats.entities,
            relations: dbStats.relations,
            mentions: dbStats.mentions,
          });
        }

        case "recent": {
          const facts = db.getAllFacts(limit);
          return json({ facts, count: facts.length });
        }

        case "similar": {
          if (!params.entity) return json({ error: "entity name is required" });
          if (!pluginConfig.embeddingApiKey) {
            return json({ error: "Embedding API key not configured." });
          }
          const entityEmb = await getEmbedding(params.entity, embeddingConfig);
          const similar = db.findSimilarEntities(entityEmb, limit);
          return json({ entity: params.entity, similar, count: similar.length });
        }

        case "merge": {
          if (!params.merge_from || !params.merge_into) {
            return json({ error: "merge_from and merge_into are required" });
          }
          try {
            db.deduplicateEntities(params.merge_into, params.merge_from);
            return json({
              success: true,
              message: `Merged "${params.merge_from}" into "${params.merge_into}"`,
            });
          } catch (err: any) {
            return json({ error: err.message });
          }
        }

        case "add": {
          if (!params.subject || !params.relation || !params.object) {
            return json({ error: "subject, relation, and object are required" });
          }
          const subjectId = db.getOrCreateEntity(
            params.subject,
            params.subject_type || "unknown"
          );
          const objectId = db.getOrCreateEntity(
            params.object,
            params.object_type || "unknown"
          );
          const relationId = db.storeRelation(
            subjectId,
            params.relation,
            objectId,
            1.0,
            "darwin",
            "",
            params.context || ""
          );

          if (pluginConfig.embeddingApiKey) {
            try {
              const mentionText = `${params.subject} ${params.relation.replace(/_/g, " ")} ${params.object}`;
              const embedding = await getEmbedding(mentionText, embeddingConfig);
              db.storeMention(subjectId, mentionText, embedding, "darwin", "");
              db.storeMention(objectId, mentionText, embedding, "darwin", "");
            } catch (embErr: any) {
              console.warn(`[knowledge-graph] Mention embedding error: ${embErr.message}`);
            }
          }

          return json({
            success: true,
            fact: `${params.subject} --[${params.relation}]--> ${params.object}`,
            relationId,
          });
        }

        case "mentions": {
          if (!params.entity) return json({ error: "entity name is required" });
          const entityId = db.getEntityId(params.entity);
          if (entityId === null) {
            return json({ error: `Entity "${params.entity}" not found in graph` });
          }
          const mentions = db.getMentions(entityId, limit);
          return json({ entity: params.entity, entityId, mentions, count: mentions.length });
        }

        default:
          return json({
            error: `Unknown action: ${params.action}. Use: search, entity, relation, stats, recent, similar, merge, add, mentions`,
          });
      }
    },
  });

  api.on("gateway_stop", () => {
    db.close();
  });

  console.log("[knowledge-graph] Plugin ready (Darwin-mode: extraction handled by scheduled agent)");
}
