/**
 * Knowledge Graph Plugin for OpenClaw
 *
 * Extracts facts from conversations and emails, stores them as relations
 * in a vector-searchable knowledge graph backed by SQLite.
 *
 * Features:
 * - Sliding window message buffer (4 Q&A pairs with 50% overlap)
 * - LLM-based fact extraction (subject, relation, object triples)
 * - Vector embeddings for semantic search (Gemini or OpenAI)
 * - Agent tool for querying the graph
 * - Entity deduplication
 */

import { createDB, type KnowledgeGraphDB } from "./db";
import { getEmbedding, type EmbeddingConfig } from "./embeddings";
import { extractFacts, type ExtractionConfig } from "./extraction";
import { MessageBuffer } from "./buffer";
// Note: entity_embeddings and fact_embeddings are legacy tables kept for backward compat.
// The primary vector mechanism is now the mentions table.

interface PluginConfig {
  embeddingProvider: "gemini" | "openai";
  embeddingApiKey: string;
  embeddingModel: string;
  embeddingDimensions: number;
  extractionModel: string;
  windowSize: number;
  flushTimeoutMs: number;
  minConfidence: number;
  dbPath: string;
}

const DEFAULT_CONFIG: PluginConfig = {
  embeddingProvider: "gemini",
  embeddingApiKey: "",
  embeddingModel: "text-embedding-004",
  embeddingDimensions: 768,
  extractionModel: "anthropic/claude-haiku-4.5",
  windowSize: 8,
  flushTimeoutMs: 300000,
  minConfidence: 0.6,
  dbPath: "/workspace/knowledge-graph.db",
};

export default function register(api: any) {
  const pluginConfig: PluginConfig = {
    ...DEFAULT_CONFIG,
    ...(api.config?.plugins?.entries?.["knowledge-graph"]?.config || {}),
  };

  // Validate required config
  if (!pluginConfig.embeddingApiKey) {
    console.warn(
      "[knowledge-graph] No embeddingApiKey configured. Vector search will be disabled. " +
      "Set plugins.entries.knowledge-graph.config.embeddingApiKey in openclaw.json"
    );
  }

  // Initialize database
  const db: KnowledgeGraphDB = createDB(pluginConfig.dbPath);
  db.init();
  console.log("[knowledge-graph] Database initialized at", pluginConfig.dbPath);

  const embeddingConfig: EmbeddingConfig = {
    provider: pluginConfig.embeddingProvider,
    apiKey: pluginConfig.embeddingApiKey,
    model: pluginConfig.embeddingModel,
    dimensions: pluginConfig.embeddingDimensions,
  };

  const extractionConfig: ExtractionConfig = {
    gatewayUrl: `http://127.0.0.1:${api.config?.gateway?.port || 18789}`,
    model: pluginConfig.extractionModel,
    // Resolve auth token: try config first, then env (gateway resolves ${VAR} before passing config)
    authToken: process.env.UI_AUTH_TOKEN || process.env.OPENCLAW_TOKEN,
  };

  // Track processing stats
  let totalExtracted = 0;
  let totalStored = 0;

  /**
   * Process a conversation block: extract facts, compute embeddings, store.
   */
  async function processBlock(conversationId: string, block: string): Promise<void> {
    console.log(`[knowledge-graph] Processing block from ${conversationId} (${block.length} chars)`);

    // 1. Extract facts via LLM
    const facts = await extractFacts(block, extractionConfig);
    totalExtracted += facts.length;

    if (facts.length === 0) {
      console.log("[knowledge-graph] No facts extracted from block");
      return;
    }

    console.log(`[knowledge-graph] Extracted ${facts.length} facts`);

    // 2. Store each fact
    for (const fact of facts) {
      if (fact.confidence < pluginConfig.minConfidence) {
        console.log(`[knowledge-graph] Skipping low-confidence fact: ${fact.subject} ${fact.relation} ${fact.object} (${fact.confidence})`);
        continue;
      }

      try {
        // Create/get entities
        const subjectId = db.getOrCreateEntity(fact.subject, fact.subject_type || "unknown");
        const objectId = db.getOrCreateEntity(fact.object, fact.object_type || "unknown");

        // Store relation
        const relationId = db.storeRelation(
          subjectId,
          fact.relation,
          objectId,
          fact.confidence,
          conversationId.split(":")[0] || "chat", // source channel
          conversationId,
          block.substring(0, 500) // store truncated context
        );

        // 3. Store mentions with vector embeddings (if API key configured).
        // Each fact produces two mentions — one anchored to the subject entity,
        // one anchored to the object entity — both using the fact statement as
        // the mention text. A single embedding call covers both mentions.
        if (pluginConfig.embeddingApiKey) {
          try {
            const mentionText = `${fact.subject} ${fact.relation.replace(/_/g, " ")} ${fact.object}`;
            const mentionSource = conversationId.split(":")[0] || "chat";
            const embedding = await getEmbedding(mentionText, embeddingConfig);

            db.storeMention(subjectId, mentionText, embedding, mentionSource, conversationId);
            db.storeMention(objectId, mentionText, embedding, mentionSource, conversationId);
          } catch (embErr: any) {
            console.error(`[knowledge-graph] Mention embedding error: ${embErr.message}`);
            // Facts are still stored; only mention embeddings are missing
          }
        }

        totalStored++;
        console.log(
          `[knowledge-graph] Stored: ${fact.subject} --[${fact.relation}]--> ${fact.object} (${fact.confidence})`
        );
      } catch (err: any) {
        console.error(`[knowledge-graph] Store error: ${err.message}`);
      }
    }
  }

  // Initialize message buffer
  const buffer = new MessageBuffer(
    {
      windowSize: pluginConfig.windowSize,
      stepSize: Math.floor(pluginConfig.windowSize / 2),
      flushTimeoutMs: pluginConfig.flushTimeoutMs,
    },
    processBlock
  );

  // ─── HOOKS ────────────────────────────────────────────────

  // Capture inbound messages (typed hook API)
  api.on(
    "message_received",
    async (event: any, ctx: any) => {
      const content = event.content;
      if (!content) return;

      const conversationId =
        ctx?.conversationId ||
        ctx?.channelId ||
        "unknown";

      const sender = event.from || "user";

      await buffer.addMessage(conversationId, sender, content);
    },
  );

  // Capture outbound messages (typed hook API)
  api.on(
    "message_sent",
    async (event: any, ctx: any) => {
      const content = event.content;
      if (!content) return;

      const conversationId =
        ctx?.conversationId ||
        ctx?.channelId ||
        "unknown";

      await buffer.addMessage(conversationId, "agent", content);
    },
  );

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
          const bufferStats = buffer.getStats();
          return json({
            entities: dbStats.entities,
            relations: dbStats.relations,
            mentions: dbStats.mentions,
            totalExtracted,
            totalStored,
            activeBuffers: Object.keys(bufferStats).length,
            buffers: bufferStats,
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
            "manual",
            "",
            "Manually added via agent tool"
          );

          // Store mentions with embeddings
          if (pluginConfig.embeddingApiKey) {
            try {
              const mentionText = `${params.subject} ${params.relation.replace(/_/g, " ")} ${params.object}`;
              const embedding = await getEmbedding(mentionText, embeddingConfig);
              db.storeMention(subjectId, mentionText, embedding, "manual", "");
              db.storeMention(objectId, mentionText, embedding, "manual", "");
            } catch (embErr: any) {
              console.warn(`[knowledge-graph] Mention embedding error on manual add: ${embErr.message}`);
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

  // ─── SHUTDOWN HOOK ────────────────────────────────────────
  // Flush pending messages and destroy the setInterval timer on gateway stop.
  api.on(
    "gateway_stop",
    async () => {
      console.log("[knowledge-graph] Gateway stopping — flushing buffers and cleaning up...");
      try {
        await buffer.flushAll();
      } catch (err: any) {
        console.error("[knowledge-graph] Flush error on shutdown:", err.message);
      }
      buffer.destroy();
      db.close();
      console.log("[knowledge-graph] Cleanup done.");
    },
  );

  console.log("[knowledge-graph] Plugin registered successfully");
  console.log(`[knowledge-graph] Buffer: window=${pluginConfig.windowSize}, flush=${pluginConfig.flushTimeoutMs}ms`);
  console.log(`[knowledge-graph] Embeddings: ${pluginConfig.embeddingProvider}/${pluginConfig.embeddingModel} (${pluginConfig.embeddingDimensions}d)`);
  console.log(`[knowledge-graph] Extraction model: ${pluginConfig.extractionModel}`);
}
