# AGENTS.md - Coding Agent Guidelines

This file provides guidance for agentic coding agents working in this OpenClaw installation.

## Build / Lint / Test Commands

### JavaScript Skills (e.g., `workspace/skills/ai-humanizer/`)

```bash
npm test                           # Run all tests (vitest)
npm run test:watch                 # Watch mode
npx vitest run tests/analyzer.test.js  # Run single test file
npx vitest run -t "pattern name"   # Run tests matching pattern

npm run lint                       # ESLint check
npm run lint:fix                   # Auto-fix lint issues
npm run format:check               # Prettier check
npm run format                     # Apply formatting
npm run check                      # Full check: lint + format + test
```

### TypeScript MCP Servers (e.g., `workspace/AITools/MCP/*/`)

```bash
npm install                        # Install dependencies
npm run build                      # Compile TypeScript (tsc)
npm start                          # Run compiled server
npm run dev                        # Build + start
npm run lint                       # ESLint check

# Test with MCP Inspector
npx @modelcontextprotocol/inspector node dist/index.js
```

### Athena Service (`workspace/AITools/Athena/`)

```bash
npm run dev                        # Development with tsx (hot reload)
npm run build                      # Compile TypeScript
npm run lint                       # ESLint check
```

### OpenClaw Gateway (if working from source)

```bash
pnpm build                         # Full build
pnpm check                         # Lint + format + types
pnpm lint                          # oxlint with type awareness
pnpm format:check                  # Check formatting (oxfmt)
pnpm test                          # Run test suite
```

## Code Style Guidelines

### TypeScript Configuration

All TypeScript projects use strict mode with these compiler options:

```json
{
  "target": "ES2022",
  "module": "ES2022",
  "strict": true,
  "noUnusedLocals": true,
  "noUnusedParameters": true,
  "noImplicitReturns": true,
  "noFallthroughCasesInSwitch": true
}
```

### ESLint Rules

- Unused variables with underscore prefix are allowed: `argsIgnorePattern: "^_"`
- Use `typescript-eslint` recommended rules
- Ignore `dist/` and `node_modules/`

### Import Style

**TypeScript (ES Modules):**
```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import type { Document } from "../types.js";  // Type-only imports
```

- Use `.js` extension in imports (required for ES module resolution)
- Type-only imports use `import type`
- Named imports preferred over default imports

**JavaScript (CommonJS):**
```javascript
const { patterns, wordCount } = require('./patterns');
const { computeStats } = require('./stats');
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Files | kebab-case | `work-packages.ts`, `request-context.ts` |
| Classes | PascalCase | `OutlineClient`, `PatternRegistry` |
| Interfaces/Types | PascalCase | `Document`, `WorkPackage` |
| Functions | camelCase | `searchDocuments`, `formatReport` |
| Constants | SCREAMING_SNAKE_CASE | `CATEGORY_LABELS`, `MAX_RETRIES` |
| Variables | camelCase | `apiClient`, `responseData` |
| MCP Tool names | snake_case with prefix | `outline_search_documents` |

### Error Handling

Always include context in error messages:

```typescript
if (response.status === 429) {
  const retryAfter = response.headers.get("Retry-After");
  throw new Error(
    `Rate limit exceeded. Retry after ${retryAfter || 5} seconds.`
  );
}

if (!project) {
  throw new Error(`Project not found: ${projectId}`);
}
```

### Type Annotations

Define interfaces for all API requests/responses:

```typescript
export interface Document {
  id: string;
  collectionId: string;
  title: string;
  text?: string;
}

async function searchDocuments(params: {
  query: string;
  collectionId?: string;
  limit?: number;
}): Promise<{ results: Document[]; total: number }> {
  // ...
}
```

### JSDoc Comments (JavaScript)

```javascript
/**
 * Analyze text for AI writing patterns.
 *
 * @param {string} text - The text to analyze
 * @param {object} opts - Options
 * @param {boolean} opts.verbose - Show all matches
 * @returns {object} Analysis result with scores and suggestions
 */
function analyze(text, opts = {}) {
  // ...
}
```

### Zod Validation (MCP Tools)

```typescript
server.registerTool(
  "outline_search_documents",
  {
    title: "Search Documents",
    description: "Search Outline documents by query",
    inputSchema: z.object({
      query: z.string().min(1).describe("Search query"),
      limit: z.number().min(1).max(100).default(25).describe("Max results"),
    }).strict(),
  },
  async (params) => {
    // Implementation
  }
);
```

### Async/Await

Always use async/await for asynchronous operations:

```typescript
// Good
const result = await client.fetchDocuments();

// Avoid
client.fetchDocuments().then(result => { ... });
```

## Project Structure

### Skills (`workspace/skills/`)

```
skill-name/
├── package.json          # Entry point, scripts
├── SKILL.md              # Metadata with YAML header
├── src/
│   ├── cli.js            # CLI entry point
│   ├── analyzer.js       # Core logic
│   └── patterns.js       # Data/constants
├── tests/
│   └── analyzer.test.js  # vitest tests
└── README.md
```

### MCP Servers (`workspace/AITools/MCP/`)

```
ServerName/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts              # Server init (dual transport)
│   ├── types.ts              # TypeScript interfaces
│   ├── services/
│   │   ├── client.ts         # API client
│   │   ├── formatters.ts     # Response formatting
│   │   └── request-context.ts # AsyncLocalStorage for credentials
│   └── tools/
│       ├── index.ts          # Tool registration
│       └── [category].ts     # Tool implementations
└── README.md
```

## Key Patterns

### MCP Server Dual Transport

Support both stdio (local) and HTTP (remote):

```typescript
const transport = process.env.MCP_TRANSPORT;
if (transport === "http") {
  // StreamableHTTPServerTransport at /mcp
} else {
  // StdioServerTransport (default)
}
```

### Request Context (AsyncLocalStorage)

For passing credentials through async call chains:

```typescript
import { AsyncLocalStorage } from "node:async_hooks";

export const requestContext = new AsyncLocalStorage<{
  apiKey: string;
  apiSecret?: string;
}>();

// In HTTP handler
requestContext.run({ apiKey }, () => {
  httpTransport.handleRequest(req, res, req.body);
});

// In tool handler
const ctx = requestContext.getStore();
const client = new ApiClient(ctx.apiKey);
```

### Response Formatting

Support markdown (human) and JSON (programmatic):

```typescript
const { text, structured } = formatResponse(
  data,
  format,      // "markdown" | "json"
  markdownFormatter,
  compactFormatter
);

return {
  content: [{ type: "text", text }],
  structuredContent: structured
};
```

## Testing

- **Framework:** vitest for JavaScript, MCP Inspector for TypeScript
- **Single test:** `npx vitest run tests/specific.test.js`
- **Pattern match:** `npx vitest run -t "should handle errors"`
- **Watch mode:** `npm run test:watch`

## Common Gotchas

1. **ES Module imports need `.js` extension** even for `.ts` files
2. **Unused variables** must be prefixed with `_` or removed
3. **HTTP transport** requires passing `req.body` as third argument
4. **Zod schemas** should use `.strict()` to reject unknown properties
5. **Type-only imports** should use `import type` syntax
