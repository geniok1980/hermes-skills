# i18n Sync After Agent-Driven Implementation

## Problem

When an external agent (Gemini CLI, Codex, Hermes subagent) adds new i18n keys to `en.ts`, the `TranslationKey` type (auto-derived from `typeof en`) updates automatically. But all other language files lack the new keys — causing ~60+ TS build errors across 12+ languages.

## Root Cause

`TranslationKey` is `NestedKeyOf<DeepString<typeof en>>` (defined in `types.ts`). It only reads `en.ts` shape. Other language files are plain `const` objects that must structurally match `en.ts`. No automatic sync exists in the toolchain.

## Detection

After delegation, always run `bun run build` and filter:

```bash
cd apps/web && bun run build 2>&1 | grep "error TS" | grep "is missing the following properties"
```

This shows which sections are missing which keys per language file.

## Fix Strategy

### Approach A: Python script (preferred for >5 missing keys per file)

Write a script that:
1. Opens `en.ts` and parses all top-level sections + key names
2. For each language file, compares section key sets
3. Adds missing keys with English fallback values
4. Writes back

Key implementation details:

```python
import re

def get_section_bounds(content, section_name):
    marker = f"    {section_name}: {{"
    start = content.find(marker)
    if start < 0: return None
    brace = content.find('{', start)
    depth, pos = 0, brace
    while pos < len(content):
        if content[pos] == '{': depth += 1
        elif content[pos] == '}':
            depth -= 1
            if depth == 0: return (start, pos + 1)
        pos += 1
    return None

def extract_keys(body):
    keys = set()
    for line in body.split('\n'):
        line = line.strip()
        if ':' in line and line.split(':')[0].strip().isidentifier():
            keys.add(line.split(':')[0].strip())
    return keys
```

### Approach B: Manual patch per section (preferred for <3 missing keys)

Use `patch` on the same anchor key across all affected languages. Example:

```python
from hermes_tools import patch
files = ['de.ts', 'fr.ts', 'it.ts', ...]
for f in files:
    patch(path=f, old_string='lastExistingKey: ...', 
          new_string='lastExistingKey: ...\nnewMissingKey: ...')
```

## Single-Quote Pitfall

When auto-generating translations for French, Italian, or Turkish, the agent frequently produces single-quote-containing strings inside single-quoted TS delimiters:

```typescript
// BROKEN — TypeScript sees string close after m'
'm\'aide à analyser...'
// Also broken — 'intero breaks parsing
l'intero
```

**Fix:** Remove the apostrophe (write `m aide` instead of `m'aide`) or switch the string to double-quoted delimiters if the file already uses `"..."` for some values (common in French for strings containing apostrophes).

## Verification After Fix

```bash
# Check for remaining single-quote issues
for f in packages/i18n/src/langs/*.ts; do
    python3 -c "
with open('$f') as fh:
    for i, line in enumerate(fh, 1):
        s = line.strip()
        if s.startswith(\"'\") and s.count(\"'\") > 2:
            print(f'$f:{i}: {s[:80]}')
    " 2>/dev/null
done

# Full build check
cd apps/web && bun run build 2>&1 | grep -c "error TS"
```

If count is 0 after the fix, the sync is complete.
