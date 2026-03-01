# TOOLS.md - von Neumann's Development Toolkit

## Available Tools

### 📖 read / ✍️ write / ✏️ edit
File operations. Your primary output channel.

**Use for:**
- Writing code to files
- Creating README files
- Editing existing code
- Reading specs or input data

### ⚡ exec / 🔄 process
Run shell commands and manage background processes.

**Use for:**
- Running code (`python script.py`, `bash script.sh`, `node index.js`)
- Installing dependencies (`pip install`, `npm install`)
- Testing output
- Building/compiling

**Important:** Always test your code by running it. Don't deliver untested code.

### 🔍 web_search / 🌐 web_fetch
Look up docs, APIs, and solutions.

**Use for:**
- Finding library docs
- Looking up API references
- Checking package names / installation commands
- Researching solutions to errors

### 🧠 memory_search / memory_get
Search your own memory for prior work.

**Use for:**
- Checking if you've solved a similar problem before
- Retrieving reusable patterns from prior sessions

### 📊 session_status
Check current session usage / model info.

## Shared Workspace

```
/workspace/shared/          ← shared mount (host: workspace-shared/)
├── lstopar-agent/          ← Cyril's requests
├── galileo/                ← Galileo's requests
├── main/                   ← Main agent's requests
└── <other-agent>/
```

Your own workspace (private scratch space): `/workspace/` (everything except `/workspace/shared/`)

## Common Patterns

### Python script
```bash
cd /workspace/shared/<agent>/<project>/
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Bash script
```bash
chmod +x script.sh && ./script.sh
```

### Node.js
```bash
cd /workspace/shared/<agent>/<project>/
npm install
node index.js
```

## Dependency Notes

*(Add notes about what's available in the sandbox as you discover things)*
- Python 3 available
- pip available
- bash, standard POSIX tools available
