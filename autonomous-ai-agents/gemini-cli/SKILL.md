---
name: gemini-cli
description: "Delegate coding tasks to Google Gemini CLI (features, refactoring, code generation)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Gemini, Google, Code-Review, Refactoring, PTY, Automation]
    related_skills: [claude-code, codex, opencode]
---

# Gemini CLI — Hermes Orchestration Guide

Delegate coding tasks to [Gemini CLI](https://cloud.google.com/gemini-cli) (Google's autonomous coding agent CLI) via the Hermes terminal.

## Prerequisites

- **Install path:** check with `which gemini` or locate via `npm list -g @google/gemini-cli`
- **Auth:** `gemini` requires a one-time OAuth login on first launch (browser-based)
- **Version check:** `gemini --version`
- **Health:** run `gemini` once interactively to complete OAuth setup

## Two Modes

### Mode 1: Print Mode (`-p`) — Non-Interactive (PREFERRED)

Headless one-shot execution. Returns result and exits. No PTY needed for simple tasks, but **use pty=true** to handle any unexpected prompts.

```bash
gemini -p "Add error handling to all API routes" --approval-mode yolo
```

**Key flags for non-interactive mode:**

| Flag | Effect |
|------|--------|
| `-p, --prompt "..."` | Non-interactive (headless) mode with the given prompt |
| `--approval-mode yolo` | Auto-approve all actions (read, write, execute) |
| `--approval-mode auto_edit` | Auto-approve edit tools only |
| `--approval-mode plan` | Read-only mode (no changes made) |
| `-m, --model <model>` | Specify the model (e.g., `gemini-2.5-pro`) |
| `--max-turns <n>` | Limit agentic loops |
| `-y, --yolo` | Deprecated alias for yolo (do NOT combine with `--approval-mode`) |
| `--acp` | Start in ACP mode for agent-to-agent communication |

**⚠️ CRITICAL:** Do NOT use `-y` and `--approval-mode` together — they conflict. Use `--approval-mode yolo` alone.

**Complete headless example:**
```bash
terminal(
  command="cd /repo && gemini -p 'Refactor auth module to use JWT' --approval-mode yolo",
  pty=true,
  timeout=300
)
```

### Mode 2: Interactive Mode (default)

Full TUI with prompt input and conversation history. Requires `pty=true` in terminal.

```bash
# Start interactive session with initial prompt
terminal(command="cd /repo && gemini 'Refactor the auth module'", pty=true, timeout=300)

# Send follow-up via process tool
process(action="submit", session_id="<id>", data="Now add unit tests")

# Monitor output
process(action="poll", session_id="<id>")
```

## CLI Subcommands

| Subcommand | Purpose |
|------------|---------|
| `gemini` | Default: launch interactive REPL |
| `gemini "query"` | Start REPL with initial prompt |
| `gemini -p "query"` | Print mode (headless) |
| `gemini mcp` | Manage MCP servers |
| `gemini skills <command>` | Manage agent skills/slash commands |
| `gemini extensions <command>` | Manage Gemini CLI extensions |
| `gemini hooks <command>` | Manage Gemini CLI hooks |
| `gemini gemma` | Manage local Gemma model routing |

## Approval Modes

| Mode | Behavior |
|------|----------|
| `default` | Prompt for each tool approval |
| `auto_edit` | Auto-approve file edits, ask for bash/network |
| `yolo` | Auto-approve ALL actions (fastest) |
| `plan` | Read-only — no filesystem modifications |

## Session Management

```bash
# List sessions
gemini --list-sessions

# Resume most recent
gemini -r latest

# Resume specific session by index
gemini -r 3

# Resume by session ID
gemini -r <uuid>

# Delete a session
gemini --delete-session 3

# Start with custom session ID
gemini --session-id <uuid>
```

## Key Flags Reference

| Flag | Effect |
|------|--------|
| `-p, --prompt "..."` | Headless mode (exits when done) |
| `-m, --model <name>` | Model selection |
| `--approval-mode <mode>` | default, auto_edit, yolo, plan |
| `-y, --yolo` | YOLO mode (deprecated — use `--approval-mode yolo`) |
| `-d, --debug` | Debug mode (opens debug console with F12) |
| `--skip-trust` | Trust workspace for this session |
| `-w, --worktree [name]` | Run in isolated git worktree |
| `-s, --sandbox` | Run in sandbox |
| `--acp` | Agent Communication Protocol mode |
| `--allowed-tools <list>` | Tools allowed without confirmation (deprecated) |
| `--policy <paths>` | Additional policy files |
| `--include-directories <paths>` | Additional workspace directories |
| `--output-format <fmt>` | text, json, stream-json |
| `--raw-output` | Disable output sanitization |
| `--resume <id>` | Resume a previous session |
| `--skip-trust` | Trust the workspace for this session |

## Extensions & Skills

Gemini CLI has its own extensibility system:

```bash
# List extensions
gemini extensions list

# Manage skills (slash commands)
gemini skills list
gemini skills add <name>
gemini skills remove <name>

# Manage hooks (event-driven automation)
gemini hooks list
```

## MCP Configuration

Gemini CLI uses a `.gemini/` directory in the project root for config:

```json
// .gemini/mcp.json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

MCP servers are configured in `.gemini/mcp.json` or loaded from the project's `.gemini/` directory.

## Background Execution for Long Tasks

```bash
# Launch in background
terminal(
  command="cd /repo && gemini -p 'Implement the search feature' --approval-mode yolo",
  pty=true,
  background=true,
  notify_on_complete=true
)

# Check progress
process(action="poll", session_id="<id>")

# View full log
process(action="log", session_id="<id>")

# Send input if needed
process(action="submit", session_id="<id>", data="y")
```

## Typical Task Patterns

### Feature Implementation
```bash
terminal(
  command="cd /repo && gemini -p 'Add a dark mode toggle to the settings page. Use Tailwind classes.' --approval-mode yolo",
  pty=true,
  timeout=300
)
```

### Code Review
```bash
terminal(
  command="cd /repo && gemini -p 'Review the diff: git diff main...feature. Check for bugs, security issues, and performance problems.' --approval-mode plan",
  pty=true,
  timeout=120
)
```

### Refactoring
```bash
terminal(
  command="cd /repo && gemini -p 'Refactor src/auth/ to use JWT tokens instead of sessions. Keep all existing tests passing.' --approval-mode yolo",
  pty=true,
  timeout=300
)
```

### Delegate from ТЗ / Technical Specification
```bash
# Write a spec file first, then reference it
terminal(
  command="cd /repo && gemini -p \"$(cat /tmp/spec.md)\" --approval-mode yolo",
  pty=true,
  timeout=600
)
```

## Pitfalls & Gotchas

1. **`-y` and `--approval-mode` are mutually exclusive** — use `--approval-mode yolo` alone, not both
2. **Requires pty=true** in terminal for interactive mode; print mode works without PTY but pty=true is safer
3. **OAuth login required on first run** — run `gemini` once interactively to authenticate
4. **No built-in session JSON output** like Claude Code — parse terminal output for structured results
5. **Workspace trust prompt** appears on first visit to a directory; `--skip-trust` bypasses it for the session
6. **Background mode with pty=true** may leave processes running — monitor with `process(action="list")`
7. **MCP config** lives in `.gemini/mcp.json` at project root, not in a global settings file
8. **No `-c` / `--continue` flag** — use `--resume latest` instead to continue last session
9. **Extensions may need separate install** — check with `gemini extensions list` before assuming they're available
10. **Long timeouts for complex tasks** — set 300-600s for multi-file refactoring or feature implementation

## Rules for Hermes Agents

1. **Prefer `--approval-mode yolo`** for code generation tasks — avoids blocking on confirmations
2. **Use `--approval-mode plan`** for code review / analysis — safe read-only mode
3. **Always set `workdir`** and `timeout` appropriately
4. **Use `pty=true`** even in print mode — catches unexpected prompts
5. **Background + notify_on_complete** for tasks expected to run > 60s
6. **Pass the task as a file path or piped content** for complex specs — `$(cat spec.md)`
7. **Check output for errors** after completion — Gemini CLI reports results via stdout
8. **Remember to trust the workspace** — `--skip-trust` for automated runs
9. **Check gemini version** before relying on new flags with `gemini --version`
10. **Pair with `technical-specifications` skill** workflow: research → write ТЗ → delegate to gemini-cli
