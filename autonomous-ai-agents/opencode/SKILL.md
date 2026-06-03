---
name: opencode
description: "Delegate coding to OpenCode CLI (features, PR review)."
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Coding-Agent, OpenCode, Autonomous, Refactoring, Code-Review, LLM-Backend, Text-Generation]
    related_skills: [claude-code, codex, hermes-agent, ai-service-development]
---

# OpenCode CLI

Use [OpenCode](https://opencode.ai) as an autonomous coding worker orchestrated by Hermes terminal/process tools. OpenCode is a provider-agnostic, open-source AI coding agent with a TUI and CLI.

## When to Use

- User explicitly asks to use OpenCode
- You want an external coding agent to implement/refactor/review code
- You need long-running coding sessions with progress checks
- You want parallel task execution in isolated workdirs/worktrees
- You need a free LLM backend for text generation (Telegram bots, services, CLI tools) — no API keys required
- You want to replace Gemini/OpenAI for simple text tasks without spending on API calls

## Models

OpenCode ships with built-in free models that work without external API keys:
```
opencode/big-pickle
opencode/deepseek-v4-flash-free
opencode/mimo-v2.5-free
opencode/nemotron-3-super-free
```

No credentials are required for these. Use `--model opencode/deepseek-v4-flash-free` to select one.

To see all available models:
```
terminal(command="/root/.opencode/bin/opencode models")
```

## ACP Server (Agent Client Protocol)

OpenCode can run as an ACP server, allowing external agents (like Hermes) to connect and delegate work. This is the recommended setup for orchestrating OpenCode from Hermes.

**Start ACP server:**
```
terminal(command="/root/.opencode/bin/opencode acp", background=true, pty=true)
```

Options:
- `--port <num>` — port (default: auto-assigned)
- `--hostname <ip>` — host (default: 127.0.0.1)
- `--mdns` — enable mDNS discovery (auto-sets hostname to 0.0.0.0)
- `--cors <domains>` — additional CORS domains
- `--cwd <path>` — working directory

**Connect to ACP server:**
Use `--attach <url>` when starting OpenCode on the client side:
```
terminal(command="/root/.opencode/bin/opencode --attach http://<host>:<port>")
```

**Verify credentials:**
```
terminal(command="/root/.opencode/bin/opencode providers list")
```

If credentials are empty, only built-in free models are available. No external API keys needed.

## Hermes Delegation (delegate_task with ACP)

To delegate coding tasks to OpenCode via Hermes's `delegate_task`:

1. Create a wrapper script that OpenCode can invoke
2. Use `acp_command` override in `delegate_task` to point to OpenCode

Example wrapper (`/root/opencode_wrapper.py`):
```python
#!/usr/bin/env python3
import subprocess, json, sys
msg = sys.stdin.read().strip()
proc = subprocess.Popen(
    ["/root/.opencode/bin/opencode", "acp", "--stdio", "--cwd", "/root"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
# Send initialize
init = {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"hermes","version":"1.0"}}}
proc.stdin.write((json.dumps(init)+"\n").encode())
proc.stdin.flush()
# Send user message
user = {"jsonrpc":"2.0","id":2,"method":"user_message","params":{"message":{"role":"user","content":msg}}}
proc.stdin.write((json.dumps(user)+"\n").encode())
proc.stdin.flush()
# Collect response...
```

Or simpler: use OpenCode directly via Hermes terminal tool:
```
terminal(command="/root/.opencode/bin/opencode run --dangerously-skip-permissions --format json --model opencode/minimax-m2.5-free 'TASK'")
```

## Binary Resolution (Critical — REQUIRED)

The actual binary lives at `~/.opencode/bin/opencode` and is **NOT in PATH**. Shell commands that use `opencode` without a path will silently fail with "command not found" (exit code 127).

**ALWAYS use the explicit path:**
```
/root/.opencode/bin/opencode
```

Correct:
```
terminal(command="/root/.opencode/bin/opencode --version")
terminal(command="/root/.opencode/bin/opencode run '...'")
terminal(command="/root/.opencode/bin/opencode acp", background=true, pty=true)
```

Incorrect (will fail silently):
```
terminal(command="opencode --version")        # exits 127
terminal(command="opencode run '...'")         # exits 127
```

`which -a opencode` returns nothing — only the explicit path works.

## One-Shot Tasks

Use `opencode run` for bounded, non-interactive tasks:

```
terminal(command="opencode run 'Add retry logic to API calls and update tests'", workdir="~/project")
```

```
terminal(command="opencode run 'Review this config for security issues' -f config.yaml -f .env.example", workdir="~/project")
```

Show model thinking with `--thinking`:

```
terminal(command="opencode run 'Debug why tests fail in CI' --thinking", workdir="~/project")
```

Force a specific model:

```
terminal(command="opencode run 'Refactor auth module' --model openrouter/anthropic/claude-sonnet-4", workdir="~/project")
```

## Interactive Sessions (Background)

For iterative work requiring multiple exchanges, start the TUI in background:

```
terminal(command="opencode", workdir="~/project", background=true, pty=true)
# Returns session_id

# Send a prompt
process(action="submit", session_id="<id>", data="Implement OAuth refresh flow and add tests")

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send follow-up input
process(action="submit", session_id="<id>", data="Now add error handling for token expiry")

# Exit cleanly — Ctrl+C
process(action="write", session_id="<id>", data="\x03")
# Or just kill the process
process(action="kill", session_id="<id>")
```

**Important:** Do NOT use `/exit` — it is not a valid OpenCode command and will open an agent selector dialog instead. Use Ctrl+C (`\x03`) or `process(action="kill")` to exit.

### TUI Keybindings

| Key | Action |
|-----|--------|
| `Enter` | Submit message (press twice if needed) |
| `Tab` | Switch between agents (build/plan) |
| `Ctrl+P` | Open command palette |
| `Ctrl+X L` | Switch session |
| `Ctrl+X M` | Switch model |
| `Ctrl+X N` | New session |
| `Ctrl+X E` | Open editor |
| `Ctrl+C` | Exit OpenCode |

### Resuming Sessions

After exiting, OpenCode prints a session ID. Resume with:

```
terminal(command="opencode -c", workdir="~/project", background=true, pty=true)  # Continue last session
terminal(command="opencode -s ses_abc123", workdir="~/project", background=true, pty=true)  # Specific session
```

## Common Flags

| Flag | Use |
|------|-----|
| `run 'prompt'` | One-shot execution and exit |
| `--continue` / `-c` | Continue the last OpenCode session |
| `--session <id>` / `-s` | Continue a specific session |
| `--agent <name>` | Choose OpenCode agent (build or plan) |
| `--model provider/model` | Force specific model |
| `--format json` | Machine-readable output/events |
| `--file <path>` / `-f` | Attach file(s) to the message |
| `--thinking` | Show model thinking blocks |
| `--variant <level>` | Reasoning effort (high, max, minimal) |
| `--title <name>` | Name the session |
| `--attach <url>` | Connect to a running opencode server |

## LLM Backend (non-coding text generation)

OpenCode can serve as a free LLM backend for external apps (Telegram bots, web services, CLI tools). Treats OpenCode as a text-generation engine rather than a coding agent.

### CRITICAL: `--thinking` required for text output

Without `--thinking`, `opencode run` emits only `step_start` — no `text` event is produced, even for trivial prompts. The process exits cleanly (code 0) but the textual response is never emitted to stdout.

**Always pass `--thinking` when using OpenCode as an LLM backend.**

### Approach A: NDJSON events from stdout (simpler, less reliable)

```bash
/root/.opencode/bin/opencode run --format json --thinking --model opencode/deepseek-v4-flash-free '<prompt>'
```

Produces one JSON object per line (NDJSON):
- `step_start` — ignore
- `reasoning` — model thinking (shown only with `--thinking`; ignore for user output)
- `text` — `part.text` contains the actual response; collect all text events
- `step_finish` — `part.tokens` and `part.cost`

**Note:** This approach sometimes returns only `step_start` + `reasoning` without a `text` event, especially under load or inside Docker. Not 100% reliable.

```python
result = subprocess.run(
    ["opencode", "run", "--format", "json", "--thinking", "--model", "opencode/deepseek-v4-flash-free", prompt],
    capture_output=True, text=True, timeout=120,
    env={**os.environ, "OPENCODE_NO_TUI": "1"},
)
texts = [
    obj["part"]["text"]
    for line in result.stdout.split("\n") if line.strip()
    if (obj := json.loads(line)).get("type") == "text"
]
] response = "".join(texts) if texts else None

See `references/llm-backend-python.md` for a complete production async wrapper with error handling and DB fallback.

### Approach B: Read response from SQLite DB (recommended, reliable)

`opencode run` always writes the assistant's response to its internal SQLite DB at `~/.local/share/opencode/opencode.db`. Reading from the DB is the only 100% reliable way to get the text response.

```python
import sqlite3, json
from pathlib import Path

DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
after_time = ...  # max(time_created) before launching

subprocess.run(["opencode", "run", "--model", "opencode/deepseek-v4-flash-free", prompt],
    capture_output=True, text=True, timeout=120,
    env={**os.environ, "OPENCODE_NO_TUI": "1"})

conn = sqlite3.connect(str(DB))
rows = conn.execute("""
    SELECT p.data
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE json_extract(m.data, '$.role') = 'assistant'
    AND json_extract(p.data, '$.type') = 'text'
    AND json_extract(p.data, '$.text') IS NOT NULL
    AND m.time_created > ?
    ORDER BY m.time_created DESC
    LIMIT 1
""", (after_time,)).fetchall()
conn.close()
if rows:
    response = json.loads(rows[0][0]).get("text", "")
```

Key points:
- `message.data -> role = 'assistant'` filters for assistant responses
- `part.data -> type = 'text'` filters for text parts (not step-start/step-finish)
- Filter by `time_created` to get only the latest response after your request
- This works reliably even when NDJSON stdout doesn't contain `text` events

### Docker integration

When running OpenCode inside Docker, mount both the binary and the DB directory:

```yaml
services:
  app:
    volumes:
      - /root/.opencode/bin/opencode:/usr/local/bin/opencode:ro
      - /root/.local/share/opencode:/root/.local/share/opencode
```

The binary at `/usr/local/bin/opencode` is in PATH inside the container, so Python can call `opencode` without a full path.

### Always strip raw JSON from user-facing messages

Never fall back to returning raw stdout — it contains NDJSON like `{"type":"step_start",...}` which is meaningless to users. If both approaches fail to extract text, return `None` and let the caller show a generic error.

## Procedure

1. **Verify tool readiness** (always use explicit path):
   - `terminal(command="/root/.opencode/bin/opencode --version")`
   - `terminal(command="/root/.opencode/bin/opencode providers list")`
   - `terminal(command="/root/.opencode/bin/opencode models")`
2. For bounded tasks, use `opencode run '...'` (no pty needed).
3. For iterative tasks, start OpenCode with `background=true, pty=true`.
4. For orchestrating OpenCode from Hermes, start the ACP server first, then connect.

## PR Review Workflow

OpenCode has a built-in PR command:

```
terminal(command="opencode pr 42", workdir="~/project", pty=true)
```

Or review in a temporary clone for isolation:

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && opencode run 'Review this PR vs main. Report bugs, security risks, test gaps, and style issues.' -f $(git diff origin/main --name-only | head -20 | tr '\n' ' ')", pty=true)
```

## Parallel Work Pattern

Use separate workdirs/worktrees to avoid collisions:

```
terminal(command="opencode run 'Fix issue #101 and commit'", workdir="/tmp/issue-101", background=true, pty=true)
terminal(command="opencode run 'Add parser regression tests and commit'", workdir="/tmp/issue-102", background=true, pty=true)
process(action="list")
```

## Session & Cost Management

List past sessions:

```
terminal(command="opencode session list")
```

Check token usage and costs:

```
terminal(command="opencode stats")
terminal(command="opencode stats --days 7 --models anthropic/claude-sonnet-4")
```

## Pitfalls

- Interactive `opencode` (TUI) sessions require `pty=true`. The `opencode run` command does NOT need pty.
- `/exit` is NOT a valid command — it opens an agent selector. Use Ctrl+C to exit the TUI.
- PATH mismatch can select the wrong OpenCode binary/model config.
- If OpenCode appears stuck, inspect logs before killing:
  - `process(action="log", session_id="<id>")`
- Avoid sharing one working directory across parallel OpenCode sessions.
- Enter may need to be pressed twice to submit in the TUI (once to finalize text, once to send).
- **Text-generation pitfall:** `opencode run` without `--thinking` never produces text output on stdout. The model runs, plans, and exits — but emits no `text` event. Always use `--thinking` when you need a textual response. For production, read the response from the SQLite DB instead of parsing stdout (see "LLM Backend" section).
- **NDJSON unreliability:** Even with `--thinking`, the `text` event sometimes doesn't appear in stdout (only `step_start` and `reasoning` are emitted). This happens semi-randomly. The DB approach (reading from SQLite) is the only guaranteed way to get the response.
- **Model list out of date:** The built-in free models change as OpenCode updates. Run `opencode models` to see current models rather than hardcoding them.

## Verification

Smoke test (always use explicit path):
```
terminal(command="/root/.opencode/bin/opencode --version")
terminal(command="/root/.opencode/bin/opencode providers list")
terminal(command="/root/.opencode/bin/opencode models")
```

For coding tasks, verify OpenCode can make a file change:
```
terminal(command="cd /tmp && echo 'test' > _opencode_test.txt && /root/.opencode/bin/opencode run --model opencode/deepseek-v4-flash-free 'Append OK to _opencode_test.txt'")
# Then check: cat /tmp/_opencode_test.txt
```

For text-generation (LLM backend), verify via DB read (see "LLM Backend" section). The smoke test using `opencode run 'Respond with...'` is unreliable because the text output isn't guaranteed on stdout.

Always verify before use:
```
terminal(command="/root/.opencode/bin/opencode --version && /root/.opencode/bin/opencode providers list")
```

Success criteria:
- Version command succeeds
- Binary found at expected path
- For code tasks: expected files changed
- For text tasks: DB contains the response

## Rules

1. Prefer `opencode run` for one-shot automation — it's simpler and doesn't need pty.
2. Use interactive background mode only when iteration is needed.
3. Always scope OpenCode sessions to a single repo/workdir.
4. For long tasks, provide progress updates from `process` logs.
5. Report concrete outcomes (files changed, tests, remaining risks).
6. Exit interactive sessions with Ctrl+C or kill, never `/exit`.
