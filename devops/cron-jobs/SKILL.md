---
name: cron-jobs
description: Write, debug, and maintain reliable cron job prompts — avoiding the tool-call-description pitfall, handling restricted toolsets, self-contained prompting, and user-centric output.
---

# Cron Jobs: Effective Prompting & Reliability

## Trigger

Load this skill whenever you are **creating, updating, or debugging** a cron job (via the `cronjob` tool). Especially important when:

- The cron job uses `enabled_toolsets` (restricted toolset)
- The output is broken/incomplete/cut off
- The user says "мне нужна полноценная подборка" or similar about cron output
- The cron prompt is in Russian

## Critical Pitfall: Tool-Call Description vs Actual Invocation

### The Problem

Some models (especially DeepSeek, but also others) have a tendency to **describe tool calls in markdown code blocks** instead of actually making them. For example, instead of invoking `web_search(...)` as a real tool call, the model writes:

```
web_search(query="rkeeper вакансия site:hh.ru", max_results=5)
```

…as a code block in the response text. This produces NO search results and the cron output is just the description of what should have been done.

### Why It's Worse in Cron Jobs

- Cron jobs run **autonomously** — no human catches the mistake
- The broken output is **automatically delivered** to the user
- The model gets no intermediate feedback (no tool results to guide it)
- The user sees a fragmented, incomplete message

### The Fix

Add this rule **prominently at the TOP** of every cron prompt (after the task header):

```
### ВАЖНЕЙШЕЕ ПРАВИЛО:
Ты ОБЯЗАН реально выполнять web_search (делать tool call), а не описывать его.
Никогда не пиши "начну поиск", "сделаю запрос", "поищу" — сразу делай поиск.
Твой ответ — это уже готовая подборка, а не план поиска.
```

For English prompts:
```
### CRITICAL RULE:
You MUST actually invoke tools (make real tool calls), not describe them in code blocks.
Never write "I will search", "let me look up", "starting search" — just make the call.
Your response IS the final output, not a plan for what to do.
```

## Other Key Principles

### 1. Self-Contained Prompts

Cron jobs run in a **fresh session** with no conversation history, no memory, no prior context. The prompt must include:

- **WHO** the user is (name, profession, interests)
- **WHAT** to do (specific task, not vague)
- **WHERE** to look / which sources
- **HOW** to format the output (exact template)
- **LANGUAGE** (specify if non-English)

### 2. Output Format Template

Always provide an exact formatting template at the end of the prompt so the model doesn't invent its own structure. For Russian-language "подборка" style prompts:

```
📅 **Утренняя подборка — {дата}**

🔥 **rkeeper / Автоматизация ресторанов:**
— [Заказ/Вакансия] Описание (бюджет/зп, источник)

💻 **Торговые боты:**
— ...

🤖 **Разработческие задачи:**
— ...

🎯 **Итого:** что самое интересное сегодня
```

### 3. Matching Toolsets to Prompt

If `enabled_toolsets` is set (e.g., `["web"]`), only those tools are available. The prompt must only reference available tools. Common pairings:

| Toolset | Available tools | Good for |
|---------|----------------|----------|
| `["web"]` | `web_search`, `web_extract`, `web_visit` | Research, digests, price checks |
| `["terminal"]` | `terminal` | Scripts, builds, file ops |
| `["browser"]` | browser tools | Web interaction, form filling |
| `["terminal", "web"]` | both | Mixed research + automation |
| `["file"]` | `read_file`, `write_file`, `search_files`, `patch` | File processing tasks |
| `["search"]` | `session_search` | Recalling past sessions |
| `["skills"]` | `skill_view`, `skills_list` | Looking up skills |

### 4. SILENT Mode

If there is genuinely nothing new to report, respond with exactly `[SILENT]` to suppress delivery. Never combine `[SILENT]` with content.

### 5. Avoid Planning Language

Models love to write phrases like:
- "Начну последовательный поиск по всем направлениям."
- "Let me start by searching for..."
- "I will look into this first..."

These waste tokens and can result in the model stopping after the plan without executing. The prompt should explicitly forbid this.

## Delivery Targets

Cron jobs can deliver to various destinations via the `deliver` parameter:

| Value | Destination |
|-------|-------------|
| `'origin'` (default) | Current conversation / home channel |
| `'local'` | Save only, no delivery |
| `'all'` | Every connected home channel |
| `'telegram:-100xxxxxxxxx'` | Specific Telegram channel (numeric ID) |
| `'telegram:#channelname'` | Public Telegram channel by username |
| `'discord:#channel'` | Discord channel |
| `'telegram:-100xxx:thread_id'` | Telegram topic thread |

**To deliver to a Telegram channel:**

1. Get the channel's numeric ID (see `telegram-promotion` skill, section "Get Channel Chat ID")
2. Create/update the cron job with `deliver='telegram:-100xxxxxxxxx'`
3. Verify the delivery works by running `cronjob(action='run', job_id='...')`

**Example:** Sending to a private Telegram channel from a cron job:

```python
cronjob(action='create',
    name='Daily tip',
    schedule='0 9 * * *',
    prompt='Write a short Freqtrade strategy tip...',
    deliver='telegram:-1003896078901')
```

### ⚠️ Delivery Pitfall: Confirm Where Cron Output Should Go

When the user has a Telegram channel AND is using cron jobs, ask explicitly where each cron should deliver — do not assume. Common mistake pattern:

1. Cron created with `deliver='origin'` (goes to DM — correct for personal reminders)
2. User creates a Telegram channel and says "публикуй в канал"
3. You update all cron deliveries to the channel
4. User corrects: "нет, личные кроны не должны идти в канал, канал только для контента"

**Rule of thumb:**
- Personal notifications (habit reminders, daily earning plans, morning briefs with personal tasks) → `origin` (DM)
- Published content (articles, tips, announcements, educational material) → channel (`telegram:-100xxx`)
- If unsure, default to `origin` and ask the user to confirm channel delivery explicitly

## Timezone Handling

The `schedule` field uses the **server's local timezone**, not UTC.

**Always check the server timezone** before setting schedules:
- `timedatectl show --property=Timezone --value` shows the system timezone
- Memory stores: "Cron scheduler uses server local time (Europe/Samara +04)"
- `next_run_at` in job response confirms the timezone (e.g., `+04:00` suffix = Samara)

On this server (Europe/Samara, GMT+4):
- 09:00 Samara → `"0 9 * * *"` (no UTC conversion needed)
- 18:00 Samara → `"0 18 * * *"`
- 10:00 Samara → `"0 10 * * *"`

If the server uses UTC:
- 09:00 local → `"0 9 * * *"` (still no conversion — the schedule IS local time)

### 7. Script-Based Cron Jobs (Alternative to Enabled Toolsets)

For tasks that don't need LLM reasoning — or need precise deterministic extraction — use the `script` field instead of `enabled_toolsets`. Two modes:

#### no_agent=True (Pure Script)
The script runs on schedule; its stdout is the **delivered message verbatim**. No LLM involved. Perfect for:
- Watchdogs / change-detection: script checks a metric, prints only when something changes; empty stdout = silent delivery
- Data collection: scrape a site and format the output as markdown
- Any task where the output shape is fixed and deterministic

```python
# Script runs and its print() output is delivered directly
print("📅 Morning report...")
```

Set `no_agent=True` with `script`:
```bash
cronjob(action='create',
    name='Daily digest',
    schedule='0 9 * * *',
    script='my-script.py',
    no_agent=True)
```

**Important**: The shebang of the script must point to the correct Python binary if using a venv:
```python
#!/root/crawl4ai-env/bin/python3   # explicit venv path
```
Otherwise the cron scheduler runs the script with the system Python, which won't have your packages.

#### LLM+Script Mode (Default: no_agent=False)
The script runs, its stdout is injected into the LLM's context as data, then the LLM decides what to deliver. Use when:
- Script collects raw data, LLM summarizes/analyzes it
- Filtering or commentary is needed on top of raw data
- The output format needs to vary based on content

```
script = "collect_data.sh"   # output goes to LLM context
prompt = "Summarize this..."
```

#### Testing script-based jobs

Always test the script manually before attaching it to a cron job:
```bash
timeout 120 /path/to/script.py   # check output and runtime
```

If the script takes longer than expected, adjust `timeout` or optimize the script (e.g., use concurrency for multiple page fetches).

To test the cron job itself:
```bash
# After updating the script, run the cron immediately
cronjob(action='run', job_id='...')
# Then check the session output
session_search(query='cron job name')
```

## Verification Checklist

Before saving a cron job, verify:

- [ ] Prompt contains explicit tool-call instruction (no descriptions, no planning language)
- [ ] All referenced tools are in `enabled_toolsets` (or use `script` + `no_agent` for non-LLM tasks)
- [ ] If using `script` with `no_agent=True`, the script has an **explicit shebang** pointing to the correct venv Python
- [ ] If using `script` with `no_agent=True`, the script was tested manually first (`timeout 120 ./script.py`)
- [ ] Format template is provided
- [ ] Target language is specified
- [ ] Prompt is fully self-contained (no assumption of prior context)
- [ ] User identity/name is included if relevant
- [ ] SILENT strategy is defined (when to suppress delivery)

## Debugging a Broken Cron Job

1. **Check session history**: `session_search(query="cron job name")` to see what the cron actually produced
2. **Look for code-block tool calls**: If the output contains markdown code blocks with tool syntax (e.g., \`\`\`tool\nweb_search(...)\n\`\`\`), the model wrote about tool calls instead of making them
3. **Fix**: update the prompt with the CRITICAL RULE section
4. **Run immediately after fix**: use `cronjob(action='run', job_id=...)` to test with the updated prompt — don't wait for the next scheduled tick
5. **Verify**: check the session output for the run; it should be a proper compilation, not a plan or partial search
6. **Script-based jobs**: if using `script` + `no_agent=True`, run the script manually first to verify it produces correct output:
   ```bash
   timeout 120 /root/.hermes/scripts/your-script.py
   ```
   If it fails with "module not found", the shebang or venv path is wrong — fix `#!/path/to/venv/bin/python3`