/**
 * Knowledge Graph database layer.
 * Uses better-sqlite3 with JSON-stored embeddings and JS-based vector search.
 * This avoids native sqlite-vec dependency issues on ARM/Docker.
 *
 * Architecture:
 *   entities ──── mentions (entity_id, mention_text, embedding) ──── relations
 *
 * Vector search flow:
 *   1. Embed query
 *   2. Score all mention embeddings by cosine similarity
 *   3. Collect the top-K unique entity IDs from ranked mentions
 *   4. Fetch all relations where subject or object is one of those entities
 *   5. Return facts sorted by the best mention similarity for that entity
 */

import Database from "better-sqlite3";
import * as path from "path";
import * as os from "os";
import { cosineSimilarity } from "./embeddings";

export interface Entity {
  id: number;
  name: string;
  type: string;
  properties: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Mention {
  id: number;
  entity_id: number;
  mention_text: string;
  source: string;
  source_id: string;
  created_at: string;
}

export interface Relation {
  id: number;
  subject_id: number;
  relation: string;
  object_id: number;
  confidence: number;
  source: string;
  source_id: string;
  context: string;
  created_at: string;
}

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

export interface KnowledgeGraphDB {
  init(): void;
  close(): void;
  getOrCreateEntity(name: string, type: string, properties?: Record<string, any>): number;
  storeMention(entityId: number, mentionText: string, embedding: number[], source: string, sourceId: string): number;
  storeRelation(
    subjectId: number,
    relation: string,
    objectId: number,
    confidence: number,
    source: string,
    sourceId: string,
    context: string
  ): number;
  searchByVector(queryEmbedding: number[], limit: number): Fact[];
  searchByEntity(entityName: string, limit: number): Fact[];
  searchByRelation(relationType: string, limit: number): Fact[];
  findSimilarEntities(queryEmbedding: number[], limit: number): Array<Entity & { similarity: number }>;
  getStats(): { entities: number; relations: number; mentions: number };
  getAllFacts(limit: number): Fact[];
  getMentions(entityId: number, limit: number): Mention[];
  getEntityId(name: string): number | null;
  deduplicateEntities(name1: string, name2: string): void;
}

export function createDB(dbPath: string): KnowledgeGraphDB {
  const expandedPath = dbPath.replace(/^~/, os.homedir());
  const dir = path.dirname(expandedPath);

  const fs = require("fs");
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  const db = new Database(expandedPath);
  db.pragma("journal_mode = WAL");
  db.pragma("foreign_keys = ON");

  return {
    init() {
      db.exec(`
        -- Entities (nodes in the graph)
        CREATE TABLE IF NOT EXISTS entities (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          canonical_name TEXT NOT NULL,
          type TEXT DEFAULT 'unknown',
          properties TEXT DEFAULT '{}',
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(canonical_name)
        );

        -- Relations (edges in the graph)
        CREATE TABLE IF NOT EXISTS relations (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          subject_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
          relation TEXT NOT NULL,
          object_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
          confidence REAL DEFAULT 1.0,
          source TEXT,
          source_id TEXT,
          context TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          superseded_by INTEGER REFERENCES relations(id)
        );

        -- Mentions: each entity appearance in context, with a vector embedding.
        -- This is the primary mechanism for vector search:
        --   query → rank mentions → get entity IDs → get all facts for those entities
        CREATE TABLE IF NOT EXISTS mentions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
          mention_text TEXT NOT NULL,
          source TEXT,
          source_id TEXT,
          embedding TEXT NOT NULL,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Legacy tables kept for backward compatibility (no longer written to)
        CREATE TABLE IF NOT EXISTS entity_embeddings (
          entity_id INTEGER PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
          embedding TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS fact_embeddings (
          relation_id INTEGER PRIMARY KEY REFERENCES relations(id) ON DELETE CASCADE,
          fact_text TEXT NOT NULL,
          embedding TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_entity_name ON entities(canonical_name);
        CREATE INDEX IF NOT EXISTS idx_entity_type ON entities(type);
        CREATE INDEX IF NOT EXISTS idx_relation_type ON relations(relation);
        CREATE INDEX IF NOT EXISTS idx_relation_subject ON relations(subject_id);
        CREATE INDEX IF NOT EXISTS idx_relation_object ON relations(object_id);
        CREATE INDEX IF NOT EXISTS idx_relation_created ON relations(created_at);
        CREATE INDEX IF NOT EXISTS idx_mention_entity ON mentions(entity_id);
        CREATE INDEX IF NOT EXISTS idx_mention_created ON mentions(created_at);
      `);
    },

    close() {
      db.close();
    },

    getOrCreateEntity(name: string, type: string, properties?: Record<string, any>): number {
      const canonical = name.toLowerCase().trim();
      const existing = db.prepare("SELECT id FROM entities WHERE canonical_name = ?").get(canonical) as any;
      if (existing) {
        if (type && type !== "unknown") {
          db.prepare("UPDATE entities SET type = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?").run(type, existing.id);
        }
        return existing.id;
      }
      const result = db.prepare(
        "INSERT INTO entities (name, canonical_name, type, properties) VALUES (?, ?, ?, ?)"
      ).run(name, canonical, type || "unknown", JSON.stringify(properties || {}));
      return Number(result.lastInsertRowid);
    },

    /**
     * Store a mention of an entity with its context embedding.
     * Each fact produces two mentions (one for subject, one for object),
     * both using the fact statement as the mention text.
     */
    storeMention(
      entityId: number,
      mentionText: string,
      embedding: number[],
      source: string,
      sourceId: string
    ): number {
      const result = db.prepare(
        "INSERT INTO mentions (entity_id, mention_text, source, source_id, embedding) VALUES (?, ?, ?, ?, ?)"
      ).run(entityId, mentionText, source, sourceId, JSON.stringify(embedding));
      return Number(result.lastInsertRowid);
    },

    storeRelation(
      subjectId: number,
      relation: string,
      objectId: number,
      confidence: number,
      source: string,
      sourceId: string,
      context: string
    ): number {
      const existing = db.prepare(`
        SELECT id FROM relations
        WHERE subject_id = ? AND relation = ? AND object_id = ? AND superseded_by IS NULL
      `).get(subjectId, relation, objectId) as any;

      if (existing) {
        db.prepare(`
          UPDATE relations SET confidence = MAX(confidence, ?), context = ?, source = ?, source_id = ?
          WHERE id = ?
        `).run(confidence, context, source, sourceId, existing.id);
        return existing.id;
      }

      const result = db.prepare(`
        INSERT INTO relations (subject_id, relation, object_id, confidence, source, source_id, context)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `).run(subjectId, relation, objectId, confidence, source, sourceId, context);
      return Number(result.lastInsertRowid);
    },

    /**
     * Vector search via mentions:
     * 1. Score every mention embedding against the query
     * 2. Rank mentions, deduplicate to top-K unique entity IDs
     * 3. Fetch all relations where subject or object is one of those entities
     * 4. Return facts sorted by best mention similarity for the entity involved
     */
    searchByVector(queryEmbedding: number[], limit: number = 10): Fact[] {
      // Load all mention embeddings
      const mentionRows = db.prepare(
        "SELECT id, entity_id, embedding FROM mentions"
      ).all() as any[];

      if (mentionRows.length === 0) return [];

      // Score each mention
      const scoredMentions = mentionRows.map((m) => ({
        entityId: m.entity_id as number,
        similarity: cosineSimilarity(queryEmbedding, JSON.parse(m.embedding)),
      }));
      scoredMentions.sort((a, b) => b.similarity - a.similarity);

      // Deduplicate: keep the best score per entity
      const entityBestScore = new Map<number, number>();
      for (const m of scoredMentions) {
        if (!entityBestScore.has(m.entityId)) {
          entityBestScore.set(m.entityId, m.similarity);
        }
        // Stop once we have enough candidate entities
        if (entityBestScore.size >= limit * 3) break;
      }

      // Fetch all relations involving those entities
      const seenRelations = new Set<number>();
      const facts: Fact[] = [];

      // Sort entity IDs by descending best-score so the most relevant come first
      const rankedEntityIds = [...entityBestScore.entries()]
        .sort((a, b) => b[1] - a[1])
        .map(([entityId, similarity]) => ({ entityId, similarity }));

      for (const { entityId, similarity } of rankedEntityIds) {
        const entityFacts = db.prepare(`
          SELECT
            r.id AS relation_id,
            e1.name AS subject, e1.type AS subject_type,
            r.relation,
            e2.name AS object, e2.type AS object_type,
            r.confidence, r.source, r.context, r.created_at
          FROM relations r
          JOIN entities e1 ON e1.id = r.subject_id
          JOIN entities e2 ON e2.id = r.object_id
          WHERE (r.subject_id = ? OR r.object_id = ?)
            AND r.superseded_by IS NULL
        `).all(entityId, entityId) as any[];

        for (const row of entityFacts) {
          if (!seenRelations.has(row.relation_id)) {
            seenRelations.add(row.relation_id);
            facts.push({
              subject: row.subject,
              subject_type: row.subject_type,
              relation: row.relation,
              object: row.object,
              object_type: row.object_type,
              confidence: row.confidence,
              source: row.source,
              context: row.context,
              created_at: row.created_at,
              similarity,
            });
          }
        }

        if (facts.length >= limit * 2) break; // enough candidates
      }

      // Sort by similarity and return top N
      facts.sort((a, b) => (b.similarity ?? 0) - (a.similarity ?? 0));
      return facts.slice(0, limit);
    },

    searchByEntity(entityName: string, limit: number = 20): Fact[] {
      const canonical = entityName.toLowerCase().trim();
      return db.prepare(`
        SELECT
          e1.name AS subject, e1.type AS subject_type,
          r.relation,
          e2.name AS object, e2.type AS object_type,
          r.confidence, r.source, r.context, r.created_at
        FROM relations r
        JOIN entities e1 ON e1.id = r.subject_id
        JOIN entities e2 ON e2.id = r.object_id
        WHERE (e1.canonical_name LIKE ? OR e2.canonical_name LIKE ?)
          AND r.superseded_by IS NULL
        ORDER BY r.created_at DESC
        LIMIT ?
      `).all(`%${canonical}%`, `%${canonical}%`, limit) as Fact[];
    },

    searchByRelation(relationType: string, limit: number = 20): Fact[] {
      return db.prepare(`
        SELECT
          e1.name AS subject, e1.type AS subject_type,
          r.relation,
          e2.name AS object, e2.type AS object_type,
          r.confidence, r.source, r.context, r.created_at
        FROM relations r
        JOIN entities e1 ON e1.id = r.subject_id
        JOIN entities e2 ON e2.id = r.object_id
        WHERE r.relation = ?
          AND r.superseded_by IS NULL
        ORDER BY r.created_at DESC
        LIMIT ?
      `).all(relationType, limit) as Fact[];
    },

    /**
     * Find entities semantically similar to a query by ranking their mentions.
     * For each entity, the best mention similarity is used as the entity score.
     */
    findSimilarEntities(queryEmbedding: number[], limit: number = 5) {
      const mentionRows = db.prepare(
        "SELECT entity_id, embedding FROM mentions"
      ).all() as any[];

      // Best score per entity
      const entityBestScore = new Map<number, number>();
      for (const m of mentionRows) {
        const sim = cosineSimilarity(queryEmbedding, JSON.parse(m.embedding));
        const prev = entityBestScore.get(m.entity_id) ?? -1;
        if (sim > prev) entityBestScore.set(m.entity_id, sim);
      }

      const ranked = [...entityBestScore.entries()]
        .sort((a, b) => b[1] - a[1])
        .slice(0, limit);

      return ranked.map(([entityId, similarity]) => {
        const entity = db.prepare(
          "SELECT id, name, type, properties, created_at, updated_at FROM entities WHERE id = ?"
        ).get(entityId) as any;
        return {
          id: entity.id,
          name: entity.name,
          type: entity.type,
          properties: JSON.parse(entity.properties || "{}"),
          created_at: entity.created_at,
          updated_at: entity.updated_at,
          similarity,
        };
      });
    },

    getStats() {
      const entities = (db.prepare("SELECT COUNT(*) AS count FROM entities").get() as any).count;
      const relations = (db.prepare("SELECT COUNT(*) AS count FROM relations WHERE superseded_by IS NULL").get() as any).count;
      const mentions = (db.prepare("SELECT COUNT(*) AS count FROM mentions").get() as any).count;
      return { entities, relations, mentions };
    },

    getAllFacts(limit: number = 50): Fact[] {
      return db.prepare(`
        SELECT
          e1.name AS subject, e1.type AS subject_type,
          r.relation,
          e2.name AS object, e2.type AS object_type,
          r.confidence, r.source, r.context, r.created_at
        FROM relations r
        JOIN entities e1 ON e1.id = r.subject_id
        JOIN entities e2 ON e2.id = r.object_id
        WHERE r.superseded_by IS NULL
        ORDER BY r.created_at DESC
        LIMIT ?
      `).all(limit) as Fact[];
    },

    getMentions(entityId: number, limit: number = 10): Mention[] {
      return db.prepare(`
        SELECT id, entity_id, mention_text, source, source_id, created_at
        FROM mentions
        WHERE entity_id = ?
        ORDER BY created_at DESC
        LIMIT ?
      `).all(entityId, limit) as Mention[];
    },

    getEntityId(name: string): number | null {
      const canonical = name.toLowerCase().trim();
      const row = db.prepare(
        "SELECT id FROM entities WHERE canonical_name LIKE ? LIMIT 1"
      ).get(`%${canonical}%`) as any;
      return row ? row.id : null;
    },

    deduplicateEntities(name1: string, name2: string) {
      const canonical1 = name1.toLowerCase().trim();
      const canonical2 = name2.toLowerCase().trim();

      const e1 = db.prepare("SELECT id FROM entities WHERE canonical_name = ?").get(canonical1) as any;
      const e2 = db.prepare("SELECT id FROM entities WHERE canonical_name = ?").get(canonical2) as any;

      if (!e1 || !e2) throw new Error("One or both entities not found");

      // Repoint all e2 references to e1
      db.prepare("UPDATE relations SET subject_id = ? WHERE subject_id = ?").run(e1.id, e2.id);
      db.prepare("UPDATE relations SET object_id = ? WHERE object_id = ?").run(e1.id, e2.id);
      db.prepare("UPDATE mentions SET entity_id = ? WHERE entity_id = ?").run(e1.id, e2.id);

      // Remove legacy embeddings
      db.prepare("DELETE FROM entity_embeddings WHERE entity_id = ?").run(e2.id);

      // Delete e2
      db.prepare("DELETE FROM entities WHERE id = ?").run(e2.id);
    },
  };
}
