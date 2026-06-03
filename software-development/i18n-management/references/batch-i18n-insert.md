# i18n Batch-Insert Reference

This reference documents the approach for adding 50+ new translation keys across 12+ language files in a TypeScript monorepo with strict `DeepString<T>` type enforcement.

## Problem

Adding new translation keys to only `en.ts` and `ru.ts` (while leaving the other 12 languages untouched) causes build failures:

```
error TS2740: Type '{ ... }' is missing the following properties from type 'DeepString<...>':
  liveStatusOnline, liveStatusSessions, quickActionMarket, ... and 48 more.
```

## Solution: Brace-Counting Batch Sync

The canonical approach uses brace counting to find section boundaries and syncs ALL sections, not just one. Two reference scripts exist:

- **`scripts/i18n-sync.py`** in the skill directory — portable, standalone, designed to be copied to any monorepo
- **`scripts/sync-i18n.py`** in the project root — project-specific (may have custom RENAME_MAP)

### Key algorithm: brace-counting section finder

```python
def find_section_boundaries(content, section_name):
    """Find (brace_pos, close_pos_exclusive) for a section by counting braces."""
    pattern = f'    {section_name}: {{'
    idx = content.find(pattern)
    if idx < 0: return None, None
    brace = content.find('{', idx)
    depth = 1
    i = brace + 1
    while i < len(content):
        if content[i] == '{': depth += 1
        elif content[i] == '}': depth -= 1
        if depth == 0:
            return brace, i + 1
        i += 1
    return None, None
```

### Comprehensive sync approach

1. Read `en.ts` as reference
2. Identify ALL section names from en.ts
3. For each language file, iterate ALL sections
4. Inside each section, find keys present in en.ts but missing in the target file
5. For each missing key, copy its block (including multi-line values) from en.ts
6. Insert it after the preceding key as it appears in en.ts
7. After all insertions, fix trailing commas with `re.sub`

### Avoiding the line-by-line insertion trap

Do NOT manipulate files line-by-line in a list — multi-line values get mangled. Instead, work on the raw string content:

- Extract blocks from `en.ts` as raw substrings
- Insert into the target file as raw substrings
- Use `re.sub` for comma-fixing after all insertions

## Language-Specific Quirks

Languages with apostrophe problems in single-quoted strings:

| Language | Problem | Fix |
|----------|---------|-----|
| Italian | `l'analisi`, `l'intero`, `sull'efficienza`, `un'analisi` | Remove apostrophe: `l analisi`, `l intero` |
| French | `j'ai`, `s'intègre`, `d'heures`, `n'aurais`, `l'efficacité` | Remove apostrophe: `j ai`, `s integre` |
| Turkish | `AI'ya` (possessive), `ClawHost'u` | Remove: `AI alanina`, `ClawHost kullanimi` |

## File List

All 14 language files that need updating:
- `packages/i18n/src/langs/en.ts` (base, defines required keys)
- `packages/i18n/src/langs/ru.ts`, `ar.ts`, `de.ts`, `es.ts`, `fr.ts`, `hi.ts`, `it.ts`, `ja.ts`, `nl.ts`, `pl.ts`, `pt.ts`, `tr.ts`, `zh.ts`
