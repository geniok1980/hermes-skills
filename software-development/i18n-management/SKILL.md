---
name: i18n-management
description: "Add, sync, and fix translation keys across multi-language i18n files in a TypeScript monorepo with strict type checking"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [i18n, translations, typescript, monorepo, internationalization]
    related_skills: [writing-plans, technical-specifications]
---

# I18n Management in TypeScript Monorepos

## Overview

Manage translation keys across 10+ language files in a strict TypeScript monorepo where the `TranslationKey` type enforces that every language file has exactly the same keys. Adding 50+ new keys across 12+ languages requires a careful approach to avoid corrupted files.

## Core Principle: Never Use read_file Output as patch Input

**CRITICAL PITFALL:** The `read_file` tool returns lines in `LINE_NUM|CONTENT` format. Using these prefixed lines as `old_string` in the `patch` tool causes the **line number prefix to be written literally into the file**, creating syntax errors.

```python
# WRONG — line number prefix gets written into file
result = read_file(path, offset=1100, limit=10)
value_line = result['content'].split('\\n')[2]  # '  1125|        autoUpdatesDescription:'
patch(path=path, old_string=value_line + '\\n' + next_line, new_string=...)  # CORRUPTS FILE
```

## Safe Workflow for Removing Keys from All Languages

### Strategy: Remove from en.ts first, then clean up all others

TypeScript infers the `TranslationKey` type from `en.ts` (the base locale). Removing a key from `en.ts` immediately makes it an error in every other locale file that still has it.

**Steps:**

1. **Remove the keys from `en.ts` first** — this changes the type so the compiler catches stale keys in all other files

2. **Find affected files** — the fastest way is to run the type checker and grep for the key name:
   ```bash
   cd apps/web && bunx tsc --noEmit 2>&1 | grep "does not exist in type" | grep "agentXxxName\|yourKeyName"
   ```
   Each error points to a specific language file and line number.

3. **Remove the 2-3 lines per file** — work through files identified in step 2. Each key is usually 2-3 consecutive lines (`agentXxxName: '...',` + `agentXxxDescription:` + `   '... description ...',`). Use one of these approaches:

   **Approach A: Python script** — best for 10+ files:
   ```python
   import os, re
   
   LANG_DIR = '/root/clawhost/packages/i18n/src/langs'
   key_name = 'agentHiddifyName'
   
   for f in sorted(os.listdir(LANG_DIR)):
       if not f.endswith('.ts'): continue
       path = os.path.join(LANG_DIR, f)
       with open(path) as fh:
           content = fh.read()
       
       # Remove the block: agentHiddifyName line + agentHiddifyDescription + its description lines
       pattern = rf'        {re.escape(key_name)}:.*?(?=\n        \w+:|\n    }})'
       new_content = re.sub(pattern, '', content, flags=re.DOTALL)
       # Also remove trailing blank lines left by the removal
       new_content = re.sub(r'\n{3,}', '\n\n', new_content)
       
       if new_content != content:
           with open(path, 'w') as fh:
               fh.write(new_content)
           print(f'Fixed: {f}')
   ```

   **Approach B: delegate_task** — for bulk work across 12+ files, spawn a subagent to handle all files.

4. **Also update agent catalog data** — if removing a v2 agent entry, also:
   - Delete the object from `apps/web/src/data/v2Agents.ts`
   - Remove the icon import and ternary branch from `V2.tsx`

5. **Verify** — zero errors means all files are clean:
   ```bash
   cd /root/clawhost/apps/web && bunx tsc --noEmit 2>&1 | grep -c "does not exist in type"
   ```

### Pitfall: The trailing comma cascade

When you remove the LAST key from a section, the key before it becomes the new last key — but it may still have a trailing comma, which is valid in TypeScript (trailing commas allowed in object literals). No action needed. However, if you remove a MIDDLE key from a section, the line that previously ended without a comma (because it was last) now needs one. The Python regex approach handles this automatically because it removes the full block including the comma at the end of the block.

### 1. Strategy: Brace-counting section insertion

The most robust approach: find a section by name using brace counting, then insert new keys before the closing `    },`. This works for ALL sections and ALL language files because the structure is the same.

```python
def find_section_range(lines, section_name):
    """Find (start_idx, end_idx) in a list of lines."""
    pattern = f'    {section_name}: {{'
    for i, line in enumerate(lines):
        if line.rstrip() == pattern:
            depth = 0
            for j in range(i, len(lines)):
                for ch in lines[j]:
                    if ch == '{': depth += 1
                    elif ch == '}': depth -= 1
                if depth == 0 and j > i:
                    return i, j + 1
    return None, None
```

For each new key, copy the key-value block (including multi-line values) from en.ts and insert it before the section's closing brace. Reference blocks from en.ts maintain proper formatting.

### 2. Copy from en.ts, insert at anchor

When inserting multiple new keys into a language file:

1. Extract the key-value blocks from `en.ts` for each missing key
2. Find the correct section in the target file via brace counting
3. Insert the blocks before the closing `    },`
4. Fix the trailing comma on the line that became non-last

Script: `scripts/i18n-sync.py` (see reference)

```python
# Extract reference block from en.ts
def get_key_block(content, key_name):
    pattern = rf'        {re.escape(key_name)}:'
    match = re.search(pattern, content)
    if not match:
        return None
    start = match.start()
    after = content[start+1:]
    next_keys = list(re.finditer(r'\n\s{8}\w+:', after))
    if next_keys:
        end = start + 1 + next_keys[0].start()
    else:
        close = after.find('\n    }')
        end = start + close + 1 if close >= 0 else start + len(after)
    block = content[start:end]
    stripped = block.rstrip()
    if not stripped.endswith(',') and not stripped.endswith('{'):
        block += ','
    return block + '\n'

# Insert at section close
insert_pos = close_brace_idx  # position of closing }
insert_text = '\n' + ''.join(blocks)
content = content[:insert_pos] + insert_text + content[insert_pos:]
```

### 3. Fix missing commas (TS1005)

When you insert keys before the closing `    },` of a section, the key that was previously the LAST key now has other keys after it — but it still has no trailing comma (which was legal before because it was the last entry in the TS object).

This causes `TS1005: ',' expected` errors. Fix with:

```python
import re
# Fix: add comma to single-quoted value lines before new key insertions
content = re.sub(
    r"('[^']*')\n(?=\s{8}\w+:\s)",
    r"\1,\n", content
)
# Also handle double-quoted strings (used e.g. in French/Italian with apostrophes)
content = re.sub(
    r'("[^"]*")\n(?=\s{8}\w+:\s)',
    r'\1,\n', content
)
```

### 5. Watch for single-quote conflicts in every language

When using single-quoted (') strings in TypeScript, any language string containing an apostrophe will break the file:

```
# WRONG — single quote inside single-quoted string
'L'analisi di mercato...'   # TypeScript sees this as 'L' + `analisi` (identifier) + ...

# RIGHT — remove or escape quotes
'L analisi di mercato...'
```

Common culprits by language:
- **Italian**: `l'analisi`, `l'intero`, `l'efficienza`, `sull'`, `un'`
- **French**: `j'ai`, `s'intègre`, `d'heures`, `l'IA`, `n'aurais`, `l'efficacité`
- **Turkish**: `AI'ya`, `ClawHost'u` (possessive suffixes)
- **Dutch/German**: apostrophes in possessives

### 4. Fix all issues before rebuilding

Don't fix one language at a time. Do a comprehensive scan:

```bash
for f in *.ts; do
    python3 -c "
with open('$f') as fh:
    for i, line in enumerate(fh, 1):
        stripped = line.strip()
        if stripped.startswith(\"'\") and stripped.count(\"'\") > 2:
            print(f'$f:{i}: {stripped[:100]}')
    "
done
```

### 5. Build to verify, don't rely on LSP

LSP diagnostics may be stale. Always run the full TypeScript build:
```bash
cd apps/web && bun run build
```

Filter pre-existing errors (not caused by your changes):
```bash
bun run build 2>&1 | grep "error TS" | grep -v "preExistingPattern"
```

## Pitfalls

### Using sed -i for inserting multi-line blocks
Multi-line sed insertions with `a` command work but are fragile with special characters, Unicode, and escaping. Prefer Python scripts with regex.

### Resetting files with git checkout then re-patching
If you corrupted a file, `git checkout -- file.ts` resets it. But if the file also has changes from another tool (Gemini CLI added whitespace/import-sorting changes), you'll lose those too. Stash first or use targeted `git checkout` on specific files only.

### The TranslationKey type
In strict TypeScript i18n setups, the `TranslationKey` type is auto-generated from the keys in the base language file (usually `en.ts`). Adding new keys to `en.ts` automatically extends the permitted union type — but ONLY after a build or IDE restart. During dev (Vite HMR), new keys may show TypeScript errors that don't actually prevent the app from running.

### Indentation consistency
All translation files in a monorepo must use the exact same indentation (spaces, not tabs). When inserting keys, verify the indentation matches the surrounding code (usually 8 spaces for top-level keys in the `landing` section).

### Key renames create duplicates (TS1117)
Renaming a key (e.g. `agentTypeHermes1CDescription` → `agentTypeHermesDescription`) by simple string-replace creates a duplicate if the target key already exists in the file. This causes `TS1117: An object literal cannot have multiple properties with the same name`.

**Fix**: After a bulk rename, scan each section for duplicate keys and remove all but the first occurrence:

```python
def deduplicate_section(content, section_name):
    section = find_section(content, section_name)
    keys_in_section = re.findall(r'\n        (\w+):', section['body'])
    seen = set()
    for key in keys_in_section:
        if key in seen:
            # Find and remove this duplicate entry
            pattern = rf'        {re.escape(key)}:'
            matches = list(re.finditer(pattern, content))
            if len(matches) > 1:
                # Delete the later occurrence(s)
                keep = content[:matches[0].start()]
                keep += content[matches[0].start():matches[1].start()]
                keep += content[matches[-1].end():]
                content = keep
                break
        seen.add(key)
    return content
```

### The full-sync trap
After adding keys to `en.ts`, you might be tempted to only add them to `ru.ts` since the user needs Russian. **Don't.** The `TranslationKey` type is derived from `en.ts`'s shape, and every language file must match — TS will fail on ALL of them if any are out of sync. Always sync ALL language files when adding keys to `en.ts`.
