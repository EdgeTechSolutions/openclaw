"use strict";

const axios = require("axios");
const cheerio = require("cheerio");

// OpenClaw tool interface
const tools = {
  searxng_web_search: async (query) => {
    const response = await axios.post(
      "http://localhost:3000/api/tools/searxng_searxng_web_search",
      { query }
    );
    return response.data;
  },
  web_fetch: async (url) => {
    const response = await axios.post(
      "http://localhost:3000/api/tools/web_fetch",
      { url }
    );
    return response.data;
  },
  memory_search: async (query) => {
    const response = await axios.post(
      "http://localhost:3000/api/tools/memory_search",
      { query }
    );
    return response.data;
  },
  memory_get: async (key) => {
    const response = await axios.post(
      "http://localhost:3000/api/tools/memory_get",
      { key }
    );
    return response.data;
  },
  memory_set: async (key, value) => {
    const response = await axios.post(
      "http://localhost:3000/api/tools/memory_set",
      { key, value }
    );
    return response.data;
  },
};

/**
 * Search StackOverflow for questions based on a query.
 * @param {string} query - The search query.
 * @returns {Promise<string>} - Formatted markdown table of results.
 */
async function so_search(query) {
  // Check memory for previous results
  const memoryKey = `so_search_${query}`;
  const cachedResults = await tools.memory_get(memoryKey);
  if (cachedResults) {
    return cachedResults;
  }

  // Perform the search
  const results = await tools.searxng_web_search(query + " site:stackoverflow.com");

  // Parse and format results
  const formattedResults = results.results
    .map((result) => {
      const questionId = result.url.match(/\/questions\/(\d+)/)?.[1] || "N/A";
      return `| [${result.title}](${result.url}) | ${questionId} |`;
    })
    .join("\n");

  const markdownTable = `
| Question | ID |
|----------|----|
${formattedResults}
`;

  // Cache results in memory
  await tools.memory_set(memoryKey, markdownTable);

  return markdownTable;
}

/**
 * Fetch the top answer for a StackOverflow question by ID or URL.
 * @param {string} questionIdOrUrl - The question ID or URL.
 * @returns {Promise<string>} - Formatted markdown of the top answer.
 */
async function so_get(questionIdOrUrl) {
  let questionUrl;
  if (questionIdOrUrl.startsWith("http")) {
    questionUrl = questionIdOrUrl;
  } else {
    questionUrl = `https://stackoverflow.com/questions/${questionIdOrUrl}`;
  }

  // Check memory for previous results
  const memoryKey = `so_get_${questionIdOrUrl}`;
  const cachedResults = await tools.memory_get(memoryKey);
  if (cachedResults) {
    return cachedResults;
  }

  // Fetch the question page
  const response = await tools.web_fetch(questionUrl);
  const $ = cheerio.load(response.content);

  // Extract the top answer
  const topAnswer = $(".answer").first();
  if (!topAnswer.length) {
    return "No answers found for this question.";
  }

  // Format the answer
  const answerText = topAnswer.find(".s-prose").text().trim();
  const codeBlocks = topAnswer
    .find("pre code")
    .map((_, element) => {
      return `
\[\\begin{code}
${$(element).text()}
\\end{code}\]
`;
    })
    .get()
    .join("\n");

  const formattedAnswer = `
### Top Answer for [Question](${questionUrl})

${answerText}

${codeBlocks}
`;

  // Cache results in memory
  await tools.memory_set(memoryKey, formattedAnswer);

  return formattedAnswer;
}

// Export functions for OpenClaw
module.exports = { so_search, so_get };