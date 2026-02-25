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

export async function extractFacts(
  conversationBlock: string,
  config: ExtractionConfig
): Promise<ExtractedFact[]> {
  const prompt = EXTRACTION_PROMPT.replace("{CONVERSATION}", conversationBlock);

  try {
    const resp = await fetch(`${config.gatewayUrl}/api/tools/llm-task`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt,
        model: config.model,
        temperature: 0.1,
        maxTokens: 2000,
      }),
    });

    if (!resp.ok) {
      console.error(`[knowledge-graph] LLM extraction failed: ${resp.status}`);
      return [];
    }

    const data = await resp.json();
    let facts: ExtractedFact[];

    if (data.details?.json) {
      facts = data.details.json;
    } else if (typeof data === "string") {
      facts = JSON.parse(data);
    } else if (Array.isArray(data)) {
      facts = data;
    } else {
      console.error("[knowledge-graph] Unexpected LLM response format:", data);
      return [];
    }

    // Validate structure
    return facts.filter(
      (f) =>
        f &&
        typeof f.subject === "string" &&
        typeof f.relation === "string" &&
        typeof f.object === "string" &&
        f.subject.length > 0 &&
        f.object.length > 0
    );
  } catch (err: any) {
    console.error(`[knowledge-graph] Extraction error: ${err.message}`);
    return [];
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
