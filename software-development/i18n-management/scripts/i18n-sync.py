#!/usr/bin/env python3
"""
i18n-sync.py — Sync translation keys from en.ts to all language files.

Usage: python3 i18n-sync.py

Reads en.ts as reference, finds ALL section names, then for each language file
adds any missing keys (from en.ts) to each section. Handles multi-line values,
duplicate keys, and trailing commas.

Designed for TypeScript monorepos where TranslationKey enforces exact shape match.
"""
import re, os, sys

LANGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'packages', 'i18n', 'src', 'langs')
EN_FILE = os.path.join(LANGS_DIR, 'en.ts')

# Default languages (override for your project)
LANGS = ['ar', 'de', 'es', 'fr', 'hi', 'it', 'ja', 'nl', 'pl', 'pt', 'tr', 'zh', 'ru']

# Key renames — maps old_name -> new_name when a translation key was renamed
RENAME_MAP = {
    # e.g. 'agentTypeHermes1CDescription': 'agentTypeHermesDescription',
}


def find_section_boundaries(content, section_name):
    """Find (brace_pos, close_pos_exclusive) for a named section using brace counting."""
    pattern = f'    {section_name}: {{'
    idx = content.find(pattern)
    if idx < 0:
        return None, None
    brace = content.find('{', idx)
    if brace < 0:
        return None, None
    depth = 1
    i = brace + 1
    while i < len(content):
        if content[i] == '{': depth += 1
        elif content[i] == '}': depth -= 1
        if depth == 0:
            return brace, i + 1
        i += 1
    return None, None


def get_keys_in_order(content, section_name):
    """Get ordered list of key names in a section."""
    s, e = find_section_boundaries(content, section_name)
    if s is None:
        return []
    return re.findall(r'\n        (\w+):', content[s:e])


def get_key_block(content, section_name, key_name):
    """Get the full key-value block for a key within a section."""
    s, e = find_section_boundaries(content, section_name)
    if s is None:
        return None
    section = content[s:e]
    pattern = rf'        {re.escape(key_name)}:'
    match = re.search(pattern, section)
    if not match:
        return None
    block_start = match.start()
    remaining = section[block_start + 1:]
    next_keys = list(re.finditer(r'\n\s{8}\w+:', remaining))
    if next_keys:
        block_end = block_start + 1 + next_keys[0].start()
    else:
        # Last key in section — ends at closing brace
        close = remaining.find('\n    }')
        block_end = block_start + close + 1 if close >= 0 else block_start + len(remaining)
    block = section[block_start:block_end]
    # Ensure trailing comma
    stripped = block.rstrip()
    if not stripped.endswith(',') and not stripped.endswith('{'):
        block += ','
    return block + '\n'


def deduplicate_section(content, section_name):
    """Remove duplicate keys from a section, keeping the first occurrence."""
    s, e = find_section_boundaries(content, section_name)
    if s is None:
        return content
    section = content[s:e]
    keys = re.findall(r'\n        (\w+):', section)
    seen = set()
    dups = set()
    for k in keys:
        if k in seen:
            dups.add(k)
        seen.add(k)
    for dup in dups:
        pattern = rf'        {re.escape(dup)}:'
        matches = list(re.finditer(pattern, content))
        if len(matches) > 1:
            # Keep first occurrence, remove subsequent ones
            # Find end of first occurrence (next key or closing brace)
            first_end = len(content)
            later_matches = list(re.finditer(pattern, content[matches[0].end():]))
            if later_matches:
                first_end = matches[0].end() + later_matches[0].start()
            else:
                # Only one occurrence now (after prior dedup)
                pass
            # For each later match, remove its block
            for m in matches[1:]:
                block_end = len(content)
                remaining_after = list(re.finditer(r'\n\s{8}\w+:', content[m.end():]))
                if remaining_after:
                    block_end = m.end() + remaining_after[0].start()
                else:
                    close = content[m.start():].find('\n    }')
                    if close >= 0:
                        block_end = m.start() + close
                content = content[:m.start()] + content[block_end:]
    return content


def fix_missing_commas(content):
    """Add trailing commas to key-value lines that are missing them before another key."""
    # Single-quoted strings
    content = re.sub(r"('[^']*')\n(?=\s{8}\w+:\s)", r"\1,\n", content)
    # Double-quoted strings (used when string has apostrophes)
    content = re.sub(r'("[^"]*")\n(?=\s{8}\w+:\s)', r'\1,\n', content)
    return content


def apply_rename(content):
    """Apply key renames from RENAME_MAP."""
    for old, new in RENAME_MAP.items():
        content = content.replace(old, new)
    return content


def main():
    if not os.path.exists(EN_FILE):
        print(f"Reference file not found: {EN_FILE}")
        sys.exit(1)
    
    with open(EN_FILE) as f:
        en = f.read()
    
    # Get all section names from en.ts
    sections = re.findall(r'\n    (\w+): {', en)
    print(f"Found {len(sections)} sections in en.ts")
    
    for lang in LANGS:
        fp = os.path.join(LANGS_DIR, f'{lang}.ts')
        if not os.path.exists(fp):
            print(f"  {lang}: file not found, skipping")
            continue
        
        with open(fp) as f:
            content = f.read()
        
        original = content
        
        # Apply key renames
        content = apply_rename(content)
        
        for section in sections:
            ref_keys = get_keys_in_order(en, section)
            if not ref_keys:
                continue  # section not in en.ts (shouldn't happen)
            
            s, e = find_section_boundaries(content, section)
            if s is None:
                continue  # section not in this language file (may not exist yet)
            
            # De-duplicate first
            content = deduplicate_section(content, section)
            
            # Get current keys
            current_keys = get_keys_in_order(content, section)
            
            # Find missing keys
            missing = [k for k in ref_keys if k not in current_keys]
            if not missing:
                continue
            
            print(f"  {lang}: {len(missing)} missing in '{section}'")
            
            # Find insertion point for each missing key
            for key in missing:
                ref_idx = ref_keys.index(key)
                insert_after_ref = ref_keys[ref_idx - 1] if ref_idx > 0 else None
                
                # Walk backwards to find a key that exists in the target
                insert_after = insert_after_ref
                if insert_after is not None and insert_after not in current_keys:
                    for step in range(2, min(ref_idx + 1, 30)):
                        candidate = ref_keys[ref_idx - step]
                        if candidate in current_keys:
                            insert_after = candidate
                            break
                    else:
                        insert_after = None
                
                block = get_key_block(en, section, key)
                if block is None:
                    continue
                
                if insert_after is not None:
                    # Insert after the anchor key
                    pattern = rf'        {re.escape(insert_after)}:'
                    match = re.search(pattern, content)
                    if match:
                        # Find end of anchor's block
                        after = content[match.start() + 1:]
                        next_key = re.search(r'\n\s{8}\w+:', after)
                        if next_key:
                            insert_pos = match.start() + 1 + next_key.start()
                        else:
                            insert_pos = len(content)
                        content = content[:insert_pos] + '\n' + block + content[insert_pos:]
                else:
                    # Insert at beginning of section
                    brace = content.find('{', s)
                    content = content[:brace+1] + '\n' + block + content[brace+1:]
                
                current_keys.append(key)
        
        if content != original:
            # Fix missing commas from insertions
            content = fix_missing_commas(content)
            with open(fp, 'w') as f:
                f.write(content)
            print(f"  {lang}: Saved")
        else:
            print(f"  {lang}: No changes")
    
    print("\nDone.")


if __name__ == '__main__':
    main()
