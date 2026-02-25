/**
 * Knowledge Graph database layer.
 * Uses better-sqlite3 with JSON-stored embeddings and JS-based vector search.
 * This avoids native sqlite-vec dependency issues on ARM/Docker.
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
  storeEntityEmbedding(entityId: number, embedding: number[]): void;
  storeRelation(
    subjectId: number,
    relation: string,
    objectId: number,
    confidence: number,
    source: string,
    sourceId: string,
    context: string
  ): number;
  storeFactEmbedding(relationId: number, embedding: number[]): void;
  searchByVector(queryEmbedding: number[], limit: number): Fact[];
  searchByEntity(entityName: string, limit: number): Fact[];
  searchByRelation(relationType: string, limit: number): Fact[];
  findSimilarEntities(queryEmbedding: number[], limit: number): Array<Entity & { similarity: number }>;
  getStats(): { entities: number; relations: number; embeddings: number };
  getAllFacts(limit: number): Fact[];
  deduplicateEntities(name1: string, name2: string): void;
}

export function createDB(dbPath: string): KnowledgeGraphDB {
  // Expand ~ to home directory
  const expandedPath = dbPath.replace(/^~/, os.homedir());
  const dir = path.dirname(expandedPath);

  // Ensure directory exists
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

        -- Entity embeddings (stored as JSON arrays for portability)
        CREATE TABLE IF NOT EXISTS entity_embeddings (
          entity_id INTEGER PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
          embedding TEXT NOT NULL
        );

        -- Fact embeddings (composite: "subject relation object")
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
      `);
    },

    close() {
      db.close();
    },

    getOrCreateEntity(name: string, type: string, properties?: Record<string, any>): number {
      const canonical = name.toLowerCase().trim();
      const existing = db.prepare("SELECT id FROM entities WHERE canonical_name = ?").get(canonical) as any;
      if (existing) {
        // Update type/properties if provided
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

    storeEntityEmbedding(entityId: number, embedding: number[]) {
      db.prepare(
        "INSERT OR REPLACE INTO entity_embeddings (entity_id, embedding) VALUES (?, ?)"
      ).run(entityId, JSON.stringify(embedding));
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
      // Check for duplicate
      const existing = db.prepare(`
        SELECT id FROM relations 
        WHERE subject_id = ? AND relation = ? AND object_id = ? AND superseded_by IS NULL
      `).get(subjectId, relation, objectId) as any;

      if (existing) {
        // Update confidence and context if higher confidence
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

    storeFactEmbedding(relationId: number, embedding: number[]) {
      const rel = db.prepare(`
        SELECT e1.name AS subject, r.relation, e2.name AS object
        FROM relations r
        JOIN entities e1 ON e1.id = r.subject_id
        JOIN entities e2 ON e2.id = r.object_id
        WHERE r.id = ?
      `).get(relationId) as any;

      const factText = rel
        ? `${rel.subject} ${rel.relation.replace(/_/g, " ")} ${rel.object}`
        : "";

      db.prepare(
        "INSERT OR REPLACE INTO fact_embeddings (relation_id, fact_text, embedding) VALUES (?, ?, ?)"
      ).run(relationId, factText, JSON.stringify(embedding));
    },

    searchByVector(queryEmbedding: number[], limit: number = 10): Fact[] {
      // Load all fact embeddings and compute cosine similarity in JS
      const rows = db.prepare(`
        SELECT
          fe.relation_id,
          fe.embedding,
          e1.name AS subject,
          e1.type AS subject_type,
          r.relation,
          e2.name AS object,
          e2.type AS object_type,
          r.confidence,
          r.source,
          r.context,
          r.created_at
        FROM fact_embeddings fe
        JOIN relations r ON r.id = fe.relation_id
        JOIN entities e1 ON e1.id = r.subject_id
        JOIN entities e2 ON e2.id = r.object_id
        WHERE r.superseded_by IS NULL
      `).all() as any[];

      // Compute similarities
      const scored = rows.map((row) => {
        const embedding = JSON.parse(row.embedding);
        const similarity = cosineSimilarity(queryEmbedding, embedding);
        return {
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
        };
      });

      // Sort by similarity descending and take top N
      scored.sort((a, b) => b.similarity - a.similarity);
      return scored.slice(0, limit);
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

    findSimilarEntities(queryEmbedding: number[], limit: number = 5) {
      const rows = db.prepare(`
        SELECT ee.entity_id, ee.embedding, e.name, e.type, e.properties, e.created_at, e.updated_at
        FROM entity_embeddings ee
        JOIN entities e ON e.id = ee.entity_id
      `).all() as any[];

      const scored = rows.map((row) => {
        const embedding = JSON.parse(row.embedding);
        const similarity = cosineSimilarity(queryEmbedding, embedding);
        return {
          id: row.entity_id,
          name: row.name,
          type: row.type,
          properties: JSON.parse(row.properties || "{}"),
          created_at: row.created_at,
          updated_at: row.updated_at,
          similarity,
        };
      });

      scored.sort((a, b) => b.similarity - a.similarity);
      return scored.slice(0, limit);
    },

    getStats() {
      const entities = (db.prepare("SELECT COUNT(*) AS count FROM entities").get() as any).count;
      const relations = (db.prepare("SELECT COUNT(*) AS count FROM relations WHERE superseded_by IS NULL").get() as any).count;
      const embeddings = (db.prepare("SELECT COUNT(*) AS count FROM fact_embeddings").get() as any).count;
      return { entities, relations, embeddings };
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

    deduplicateEntities(name1: string, name2: string) {
      const canonical1 = name1.toLowerCase().trim();
      const canonical2 = name2.toLowerCase().trim();

      const e1 = db.prepare("SELECT id FROM entities WHERE canonical_name = ?").get(canonical1) as any;
      const e2 = db.prepare("SELECT id FROM entities WHERE canonical_name = ?").get(canonical2) as any;

      if (!e1 || !e2) throw new Error("One or both entities not found");

      // Merge: point all e2 references to e1
      db.prepare("UPDATE relations SET subject_id = ? WHERE subject_id = ?").run(e1.id, e2.id);
      db.prepare("UPDATE relations SET object_id = ? WHERE object_id = ?").run(e1.id, e2.id);

      // Delete e2
      db.prepare("DELETE FROM entity_embeddings WHERE entity_id = ?").run(e2.id);
      db.prepare("DELETE FROM entities WHERE id = ?").run(e2.id);
    },
  };
}
