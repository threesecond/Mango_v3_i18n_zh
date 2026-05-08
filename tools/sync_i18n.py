#!/usr/bin/env python3
"""
Compare i18n.properties and i18n_zh.properties. Insert missing keys from English into Chinese file
keeping English order. Inserted values will be empty. Creates a backup of the original Chinese file.
Prints a summary and list of inserted keys.
"""
import io
import os
import sys

EN = os.path.abspath(r"d:\Users\threesecond\OneDrive\Github\Mango_v3_i18n_zh\modules\lang_zh\classes\i18n.properties")
ZH = os.path.abspath(r"d:\Users\threesecond\OneDrive\Github\Mango_v3_i18n_zh\modules\lang_zh\classes\i18n_zh.properties")


def read_properties(path):
    """Read a .properties file and return list of (line, key, value, is_comment_or_empty)
    Keeps original lines for rewriting while extracting keys.
    """
    items = []
    with io.open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.rstrip('\n')
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                items.append((line, None, None, True))
                continue
            # find first = or :
            sep_index = None
            for i, ch in enumerate(line):
                if ch in ('=', ':'):
                    sep_index = i
                    break
            if sep_index is None:
                # malformed or key only
                key = line.strip()
                val = ''
            else:
                key = line[:sep_index].strip()
                val = line[sep_index+1:].lstrip()
            items.append((line, key, val, False))
    return items


def build_key_map(items):
    keys = []
    key_set = set()
    for line, key, val, is_misc in items:
        if is_misc:
            continue
        if key not in key_set:
            keys.append(key)
            key_set.add(key)
    return keys, key_set


def main():
    if not os.path.exists(EN) or not os.path.exists(ZH):
        print('Ensure both files exist:')
        print(' EN=', EN)
        print(' ZH=', ZH)
        sys.exit(2)

    en_items = read_properties(EN)
    zh_items = read_properties(ZH)

    en_keys, _ = build_key_map(en_items)
    zh_keys, zh_key_set = build_key_map(zh_items)

    missing = [k for k in en_keys if k not in zh_key_set]
    if not missing:
        print('No missing keys. Nothing to do.')
        return

    # backup zh
    bak = ZH + '.bak'
    if not os.path.exists(bak):
        import shutil
        shutil.copyfile(ZH, bak)
        print('Backup created at', bak)
    else:
        print('Backup already exists at', bak)

    # We'll produce a new zh content by iterating en_items and for each key line
    # take zh translation if exists else insert empty value
    zh_key_to_val = {k: v for _, k, v, misc in zh_items if k}

    out_lines = []
    for line, key, val, is_misc in en_items:
        if is_misc:
            out_lines.append(line)
            continue
        if key in zh_key_to_val:
            out_lines.append(f"{key}={zh_key_to_val[key]}")
        else:
            out_lines.append(f"{key}=")

    # write back
    with io.open(ZH, 'w', encoding='utf-8', newline='\n') as f:
        for l in out_lines:
            f.write(l + "\n")

    print(f'Inserted {len(missing)} missing keys into {ZH}')
    for k in missing[:200]:
        print(k)


if __name__ == '__main__':
    main()
