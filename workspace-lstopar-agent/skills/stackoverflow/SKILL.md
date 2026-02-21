---
name: stackoverflow
description: Search and retrieve questions, answers, and details from StackOverflow using the StackExchange API v2.3. Use this skill when you need to:
  - Search for StackOverflow questions by keywords, tags, or other criteria.
  - Retrieve detailed information about specific questions, including their body, tags, vote count, and answer count.
  - Fetch answers for a specific question, sorted by votes or activity.
  - Retrieve detailed information about specific answers, including their body, vote count, and whether they are accepted.

This skill uses the StackExchange API and does not require an API key for basic usage (limited to 300 requests/day per IP).
---

# StackOverflow Skill

This skill allows you to interact with the StackExchange API v2.3 to search for questions, retrieve question details, fetch answers for questions, and retrieve specific answer details from StackOverflow.

## Base URL

All API requests are made to:
```
https://api.stackexchange.com/2.3/
```

## Endpoints

### 1. Search StackOverflow Questions

Search for questions on StackOverflow using keywords, tags, or other criteria.

**Endpoint:**
```
/2.3/search/advanced?site=stackoverflow
```

**Parameters:**
- `q` (string): Search query (e.g., `python list comprehension`).
- `tagged` (string, optional): Semicolon-delimited list of tags (e.g., `python;list`).
- `nottagged` (string, optional): Semicolon-delimited list of tags to exclude.
- `title` (string, optional): Text that must appear in the question title.
- `body` (string, optional): Text that must appear in the question body.
- `accepted` (boolean, optional): `true` to return only questions with accepted answers.
- `answers` (integer, optional): Minimum number of answers a question must have.
- `views` (integer, optional): Minimum number of views a question must have.
- `sort` (string, optional): Sort order (`activity`, `creation`, `votes`, `relevance`). Default: `activity`.
- `order` (string, optional): Sort direction (`desc`, `asc`). Default: `desc`.
- `filter` (string, optional): Filter to include additional data (e.g., `withbody`). Default: `none`.

**Example Command:**
```bash
curl --compressed "https://api.stackexchange.com/2.3/search/advanced?site=stackoverflow&q=python%20list%20comprehension&sort=relevance&order=desc&filter=withbody"
```

**Output Format:**
- Question title (as a link to the question)
- Score (votes)
- Answer count
- Tags (as labels)
- Question body (if `filter=withbody` is used)

---

### 2. Get Question Details

Retrieve detailed information about a specific question by its ID.

**Endpoint:**
```
/2.3/questions/{ids}?site=stackoverflow
```

**Parameters:**
- `ids` (string): Semicolon-delimited list of question IDs (e.g., `12345;67890`).
- `filter` (string, optional): Filter to include additional data (e.g., `withbody`). Default: `none`.

**Example Command:**
```bash
curl --compressed "https://api.stackexchange.com/2.3/questions/12345?site=stackoverflow&filter=withbody"
```

**Output Format:**
- Question title (as a link to the question)
- Score (votes)
- Answer count
- Tags (as labels)
- Question body (if `filter=withbody` is used)

---

### 3. Get Answers for a Question

Retrieve answers for a specific question, sorted by votes or activity.

**Endpoint:**
```
/2.3/questions/{ids}/answers?site=stackoverflow
```

**Parameters:**
- `ids` (string): Semicolon-delimited list of question IDs (e.g., `12345;67890`).
- `sort` (string, optional): Sort order (`activity`, `creation`, `votes`). Default: `activity`.
- `order` (string, optional): Sort direction (`desc`, `asc`). Default: `desc`.
- `filter` (string, optional): Filter to include additional data (e.g., `withbody`). Default: `none`.

**Example Command:**
```bash
curl --compressed "https://api.stackexchange.com/2.3/questions/12345/answers?site=stackoverflow&sort=votes&order=desc&filter=withbody"
```

**Output Format:**
- Answer body (as markdown, with code blocks preserved)
- Score (votes)
- Accepted answer indicator (✓ if accepted)
- Link to the answer

---

### 4. Get Answer Details

Retrieve detailed information about a specific answer by its ID.

**Endpoint:**
```
/2.3/answers/{ids}?site=stackoverflow
```

**Parameters:**
- `ids` (string): Semicolon-delimited list of answer IDs (e.g., `12345;67890`).
- `filter` (string, optional): Filter to include additional data (e.g., `withbody`). Default: `none`.

**Example Command:**
```bash
curl --compressed "https://api.stackexchange.com/2.3/answers/12345?site=stackoverflow&filter=withbody"
```

**Output Format:**
- Answer body (as markdown, with code blocks preserved)
- Score (votes)
- Accepted answer indicator (✓ if accepted)
- Link to the answer

---

## Usage Examples

### Example 1: Search for Questions

**User Request:**
"Search StackOverflow for questions about Python list comprehensions."

**Command:**
```bash
curl --compressed "https://api.stackexchange.com/2.3/search/advanced?site=stackoverflow&q=python%20list%20comprehension&sort=relevance&order=desc&filter=withbody"
```

**Output:**
```markdown
### [How to use list comprehension in Python?](https://stackoverflow.com/questions/123456)
- **Score:** 42
- **Answers:** 5
- **Tags:** python, list, comprehension

```python
# Example of list comprehension
squares = [x**2 for x in range(10)]
```
```

---

### Example 2: Get Question Details

**User Request:**
"Get details for StackOverflow question #12345."

**Command:**
```bash
curl --compressed "https://api.stackexchange.com/2.3/questions/12345?site=stackoverflow&filter=withbody"
```

**Output:**
```markdown
### [How to use list comprehension in Python?](https://stackoverflow.com/questions/123456)
- **Score:** 42
- **Answers:** 5
- **Tags:** python, list, comprehension

```python
# Example of list comprehension
squares = [x**2 for x in range(10)]
```
```

---

### Example 3: Get Answers for a Question

**User Request:**
"Get answers for StackOverflow question #12345, sorted by votes."

**Command:**
```bash
curl --compressed "https://api.stackexchange.com/2.3/questions/12345/answers?site=stackoverflow&sort=votes&order=desc&filter=withbody"
```

**Output:**
```markdown
### Answer by User123
- **Score:** 30
- **Accepted:** ✓
- [Link to Answer](https://stackoverflow.com/a/123457)

```python
# Example of list comprehension
squares = [x**2 for x in range(10)]
```

---

### Answer by User456
- **Score:** 15
- **Accepted:** ❌
- [Link to Answer](https://stackoverflow.com/a/123458)

```python
# Alternative example
squares = list(map(lambda x: x**2, range(10)))
```
```

---

### Example 4: Get Answer Details

**User Request:**
"Get details for StackOverflow answer #123457."

**Command:**
```bash
curl --compressed "https://api.stackexchange.com/2.3/answers/123457?site=stackoverflow&filter=withbody"
```

**Output:**
```markdown
### Answer by User123
- **Score:** 30
- **Accepted:** ✓
- [Link to Answer](https://stackoverflow.com/a/123457)

```python
# Example of list comprehension
squares = [x**2 for x in range(10)]
```
```

---

## Notes

- The StackExchange API is free to use without an API key, but it is limited to **300 requests per day per IP address**. 
- Always use the `--compressed` flag with `curl` to handle gzip-compressed responses.
- Use `filter=withbody` to include the question or answer body in the response.
- HTML entities in the response body should be decoded for readability.