/**
 * Fact extraction from conversation blocks using LLM.
 */

export interface ExtractedFact {
  subject: string;
  subject_type: string;
  relation: string;
  object: string;
  object_type: string;
  confidence: number;
}

export interface ExtractionConfig {
  gatewayUrl: string;
  model: string;
  authToken?: string;
}

const EXTRACTION_PROMPT = `You are a knowledge graph fact extractor. Given a conversation block, extract factual relations as structured triples.

Rules:
- Only extract CONCRETE facts (decisions, preferences, events, relationships, configurations, deadlines)
- Skip greetings, filler, opinions without substance, and small talk
- Normalize entity names (e.g., "Luka" and "Luka Stopar" → use the most complete form)
- Use lowercase snake_case for relation types
- Assign confidence 0.0-1.0 based on how certain the fact is

Entity types: person, organization, project, tool, technology, location, date, concept, decision, configuration, other

Common relation types:
- works_at, member_of, manages, reports_to
- uses, prefers, configured, installed, built
- decided, approved, rejected, chose_over
- deadline, scheduled_for, completed_on
- located_in, lives_in, based_in
- knows, collaborates_with
- has_property, is_type_of, part_of
- costs, priced_at, balance_is
- blocked_by, depends_on, requires

Conversation:
{CONVERSATION}

Return ONLY a JSON array (no markdown, no commentary):
[{"subject": "...", "subject_type": "...", "relation": "...", "object": "...", "object_type": "...", "confidence": 0.0}]

If no facts can be extracted, return: []`;

function resolveAuthToken(config: ExtractionConfig): string | undefined {
  // Prefer explicit token, then fall back to env var
  return config.authToken || process.env.UI_AUTH_TOKEN || process.env.OPENCLAW_TOKEN;
}

export async function extractFacts(
  conversationBlock: string,
  config: ExtractionConfig
): Promise<ExtractedFact[]> {
  const prompt = EXTRACTION_PROMPT.replace("{CONVERSATION}", conversationBlock);
  const token = resolveAuthToken(config);

  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
    headers["X-Auth-Token"] = token;
  }

  try {
    const resp = await fetch(`${config.gatewayUrl}/api/tools/llm-task`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        prompt,
        model: config.model,
        temperature: 0.1,
        maxTokens: 2000,
      }),
    });

    if (!resp.ok) {
      const errText = await resp.text().catch(() => "(unreadable)");
      console.error(`[knowledge-graph] LLM extraction failed: HTTP ${resp.status}: ${errText}`);
      return [];
    }

    const data = await resp.json();
    return parseExtractionResponse(data);
  } catch (err: any) {
    console.error(`[knowledge-graph] Extraction error: ${err.message}`);
    return [];
  }
}

function parseExtractionResponse(data: unknown): ExtractedFact[] {
  // Handle multiple response shapes from llm-task
  let raw: unknown = data;

  // { result: [...] } or { details: { json: [...] } } or { json: [...] }
  if (raw && typeof raw === "object" && !Array.isArray(raw)) {
    const obj = raw as Record<string, unknown>;
    if (Array.isArray(obj.result)) {
      raw = obj.result;
    } else if (obj.details && typeof obj.details === "object") {
      const details = obj.details as Record<string, unknown>;
      if (Array.isArray(details.json)) {
        raw = details.json;
      } else if (typeof details.text === "string") {
        raw = tryParseJson(details.text);
      }
    } else if (Array.isArray(obj.json)) {
      raw = obj.json;
    } else if (typeof obj.text === "string") {
      raw = tryParseJson(obj.text);
    }
  }

  // If still a string, try to parse JSON
  if (typeof raw === "string") {
    raw = tryParseJson(raw);
  }

  if (!Array.isArray(raw)) {
    console.error("[knowledge-graph] Unexpected LLM response shape:", JSON.stringify(data).slice(0, 300));
    return [];
  }

  // Validate and filter
  return (raw as unknown[]).filter(
    (f): f is ExtractedFact =>
      f !== null &&
      typeof f === "object" &&
      typeof (f as any).subject === "string" &&
      typeof (f as any).relation === "string" &&
      typeof (f as any).object === "string" &&
      (f as any).subject.length > 0 &&
      (f as any).object.length > 0
  );
}

function tryParseJson(s: string): unknown {
  try {
    // Strip code fences if present
    const trimmed = s.trim();
    const fenced = trimmed.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/i);
    return JSON.parse(fenced ? fenced[1]! : trimmed);
  } catch {
    return null;
  }
}

/**
 * Alternative extraction using direct LLM API call (no llm-task dependency).
 * Falls back to this if llm-task is not available.
 */
export async function extractFactsDirect(
  conversationBlock: string,
  apiKey: string,
  model: string = "mistral-large-latest"
): Promise<ExtractedFact[]> {
  const prompt = EXTRACTION_PROMPT.replace("{CONVERSATION}", conversationBlock);

  try {
    const resp = await fetch("https://api.mistral.ai/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model,
        messages: [{ role: "user", content: prompt }],
        temperature: 0.1,
        response_format: { type: "json_object" },
      }),
    });

    if (!resp.ok) return [];

    const data = await resp.json();
    const content = data.choices?.[0]?.message?.content;
    if (!content) return [];

    const parsed = JSON.parse(content);
    return Array.isArray(parsed) ? parsed : parsed.facts || [];
  } catch {
    return [];
  }
}
