# StackOverflow Skill for OpenClaw

## Description
This skill allows OpenClaw to search StackOverflow for programming-related questions and fetch top answers for a given question (by ID or URL). It formats results in markdown for easy readability and supports semantic memory to avoid duplicate searches.

## Features
- Search StackOverflow for questions using keywords.
- Fetch and display top answers for a specific question by ID or URL.
- Format results in markdown with links and code snippets.
- Avoid duplicate searches using semantic memory.

## Usage Examples

### Search for Questions
```
so_search <query>
```
Example:
```
so_search python parse json
```

### Fetch Top Answer for a Question
```
so_get <question_id_or_url>
```
Example:
```
so_get 123456
```
Or:
```
so_get https://stackoverflow.com/questions/123456
```

## Output Format
- **Search Results**: A markdown table with question titles, URLs, and IDs.
- **Answer Results**: Formatted markdown with the top answer, including code snippets and links.

## Dependencies
- `axios`: For fetching web pages.
- `cheerio`: For parsing HTML content.
- OpenClaw's built-in memory tools for avoiding duplicate searches.