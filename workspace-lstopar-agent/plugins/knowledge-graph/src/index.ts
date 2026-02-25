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
  dbPath: "~/.openclaw/knowledge-graph.db",
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

        // 3. Compute and store embeddings (if API key configured)
        if (pluginConfig.embeddingApiKey) {
          try {
            // Entity embeddings
            const subjectEmb = await getEmbedding(
              `${fact.subject} (${fact.subject_type || "entity"})`,
              embeddingConfig
            );
            db.storeEntityEmbedding(subjectId, subjectEmb);

            const objectEmb = await getEmbedding(
              `${fact.object} (${fact.object_type || "entity"})`,
              embeddingConfig
            );
            db.storeEntityEmbedding(objectId, objectEmb);

            // Composite fact embedding
            const factText = `${fact.subject} ${fact.relation.replace(/_/g, " ")} ${fact.object}`;
            const factEmb = await getEmbedding(factText, embeddingConfig);
            db.storeFactEmbedding(relationId, factEmb);
          } catch (embErr: any) {
            console.error(`[knowledge-graph] Embedding error: ${embErr.message}`);
            // Continue without embeddings — facts are still stored
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

  // Capture inbound messages
  api.registerHook(
    "message:received",
    async (event: any) => {
      const content = event.context?.content;
      if (!content) return;

      const conversationId =
        event.context?.conversationId ||
        event.context?.channelId ||
        event.sessionKey ||
        "unknown";

      const sender = event.context?.from || "user";

      await buffer.addMessage(conversationId, sender, content);
    },
    {
      name: "knowledge-graph.message-received",
      description: "Buffers inbound messages for fact extraction",
    }
  );

  // Capture outbound messages (agent replies)
  api.registerHook(
    "message:sent",
    async (event: any) => {
      const content = event.context?.content;
      if (!content) return;

      const conversationId =
        event.context?.conversationId ||
        event.context?.channelId ||
        event.sessionKey ||
        "unknown";

      await buffer.addMessage(conversationId, "agent", content);
    },
    {
      name: "knowledge-graph.message-sent",
      description: "Buffers outbound messages for fact extraction",
    }
  );

  // ─── AGENT TOOL ───────────────────────────────────────────

  api.registerTool({
    name: "knowledge_graph",
    description:
      "Search and manage the knowledge graph. Stores facts extracted from conversations as (subject, relation, object) triples with vector embeddings for semantic search.",
    parameters: {
      type: "object",
      properties: {
        action: {
          type: "string",
          enum: ["search", "entity", "relation", "stats", "recent", "similar", "merge", "add"],
          description:
            "Action to perform: search (semantic), entity (by name), relation (by type), stats, recent (latest facts), similar (find similar entities), merge (deduplicate entities), add (manually add a fact)",
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
    handler: async (params: any) => {
      const limit = params.limit || 10;

      switch (params.action) {
        case "search": {
          if (!params.query) return { error: "query is required for search" };
          if (!pluginConfig.embeddingApiKey) {
            return { error: "Embedding API key not configured. Use action=entity or action=relation instead." };
          }
          const queryEmb = await getEmbedding(params.query, embeddingConfig);
          const results = db.searchByVector(queryEmb, limit);
          return { results, count: results.length };
        }

        case "entity": {
          if (!params.entity) return { error: "entity name is required" };
          const facts = db.searchByEntity(params.entity, limit);
          return { entity: params.entity, facts, count: facts.length };
        }

        case "relation": {
          if (!params.relation) return { error: "relation type is required" };
          const facts = db.searchByRelation(params.relation, limit);
          return { relation: params.relation, facts, count: facts.length };
        }

        case "stats": {
          const dbStats = db.getStats();
          const bufferStats = buffer.getStats();
          return {
            ...dbStats,
            totalExtracted,
            totalStored,
            activeBuffers: Object.keys(bufferStats).length,
            buffers: bufferStats,
          };
        }

        case "recent": {
          const facts = db.getAllFacts(limit);
          return { facts, count: facts.length };
        }

        case "similar": {
          if (!params.entity) return { error: "entity name is required" };
          if (!pluginConfig.embeddingApiKey) {
            return { error: "Embedding API key not configured." };
          }
          const entityEmb = await getEmbedding(params.entity, embeddingConfig);
          const similar = db.findSimilarEntities(entityEmb, limit);
          return { entity: params.entity, similar, count: similar.length };
        }

        case "merge": {
          if (!params.merge_from || !params.merge_into) {
            return { error: "merge_from and merge_into are required" };
          }
          try {
            db.deduplicateEntities(params.merge_into, params.merge_from);
            return {
              success: true,
              message: `Merged "${params.merge_from}" into "${params.merge_into}"`,
            };
          } catch (err: any) {
            return { error: err.message };
          }
        }

        case "add": {
          if (!params.subject || !params.relation || !params.object) {
            return { error: "subject, relation, and object are required" };
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

          // Compute embeddings if available
          if (pluginConfig.embeddingApiKey) {
            try {
              const subEmb = await getEmbedding(
                `${params.subject} (${params.subject_type || "entity"})`,
                embeddingConfig
              );
              db.storeEntityEmbedding(subjectId, subEmb);

              const objEmb = await getEmbedding(
                `${params.object} (${params.object_type || "entity"})`,
                embeddingConfig
              );
              db.storeEntityEmbedding(objectId, objEmb);

              const factText = `${params.subject} ${params.relation.replace(/_/g, " ")} ${params.object}`;
              const factEmb = await getEmbedding(factText, embeddingConfig);
              db.storeFactEmbedding(relationId, factEmb);
            } catch (embErr: any) {
              console.warn(`[knowledge-graph] Embedding error on manual add: ${embErr.message}`);
            }
          }

          return {
            success: true,
            fact: `${params.subject} --[${params.relation}]--> ${params.object}`,
            relationId,
          };
        }

        default:
          return {
            error: `Unknown action: ${params.action}. Use: search, entity, relation, stats, recent, similar, merge, add`,
          };
      }
    },
  });

  console.log("[knowledge-graph] Plugin registered successfully");
  console.log(`[knowledge-graph] Buffer: window=${pluginConfig.windowSize}, flush=${pluginConfig.flushTimeoutMs}ms`);
  console.log(`[knowledge-graph] Embeddings: ${pluginConfig.embeddingProvider}/${pluginConfig.embeddingModel} (${pluginConfig.embeddingDimensions}d)`);
  console.log(`[knowledge-graph] Extraction model: ${pluginConfig.extractionModel}`);
}
