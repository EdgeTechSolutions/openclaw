/**
 * Embedding providers for the knowledge graph.
 * Supports Gemini and OpenAI embedding APIs.
 */

export interface EmbeddingConfig {
  provider: "gemini" | "openai";
  apiKey: string;
  model: string;
  dimensions: number;
}

export async function getEmbedding(
  text: string,
  config: EmbeddingConfig
): Promise<number[]> {
  if (config.provider === "gemini") {
    return getGeminiEmbedding(text, config);
  } else if (config.provider === "openai") {
    return getOpenAIEmbedding(text, config);
  }
  throw new Error(`Unknown embedding provider: ${config.provider}`);
}

export async function getEmbeddingBatch(
  texts: string[],
  config: EmbeddingConfig
): Promise<number[][]> {
  // Gemini doesn't support batch natively, so we parallelize
  if (config.provider === "openai") {
    return getOpenAIEmbeddingBatch(texts, config);
  }
  // Fallback: parallel individual requests (with concurrency limit)
  const CONCURRENCY = 5;
  const results: number[][] = new Array(texts.length);
  for (let i = 0; i < texts.length; i += CONCURRENCY) {
    const batch = texts.slice(i, i + CONCURRENCY);
    const embeddings = await Promise.all(
      batch.map((t) => getEmbedding(t, config))
    );
    for (let j = 0; j < embeddings.length; j++) {
      results[i + j] = embeddings[j];
    }
  }
  return results;
}

async function getGeminiEmbedding(
  text: string,
  config: EmbeddingConfig
): Promise<number[]> {
  const model = config.model || "text-embedding-004";
  const url = `https://generativelanguage.googleapis.com/v1/models/${model}:embedContent?key=${config.apiKey}`;

  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: `models/${model}`,
      content: { parts: [{ text }] },
      outputDimensionality: config.dimensions,
    }),
  });

  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`Gemini embedding failed (${resp.status}): ${err}`);
  }

  const data = await resp.json();
  return data.embedding.values;
}

async function getOpenAIEmbedding(
  text: string,
  config: EmbeddingConfig
): Promise<number[]> {
  const model = config.model || "text-embedding-3-small";
  const resp = await fetch("https://api.openai.com/v1/embeddings", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${config.apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      input: text,
      dimensions: config.dimensions,
    }),
  });

  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`OpenAI embedding failed (${resp.status}): ${err}`);
  }

  const data = await resp.json();
  return data.data[0].embedding;
}

async function getOpenAIEmbeddingBatch(
  texts: string[],
  config: EmbeddingConfig
): Promise<number[][]> {
  const model = config.model || "text-embedding-3-small";
  const resp = await fetch("https://api.openai.com/v1/embeddings", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${config.apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      input: texts,
      dimensions: config.dimensions,
    }),
  });

  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`OpenAI batch embedding failed (${resp.status}): ${err}`);
  }

  const data = await resp.json();
  return data.data
    .sort((a: any, b: any) => a.index - b.index)
    .map((d: any) => d.embedding);
}

/**
 * Cosine similarity between two vectors.
 * Used as fallback when sqlite-vec is not available.
 */
export function cosineSimilarity(a: number[], b: number[]): number {
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;
  for (let i = 0; i < a.length; i++) {
    dotProduct += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}
