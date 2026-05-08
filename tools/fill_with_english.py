#!/usr/bin/env python3
"""
Fill empty values in i18n_zh.properties using corresponding values from i18n.properties (English).
Creates a backup of the current i18n_zh.properties as .bak2 (to preserve the previous backup).
Reports the keys that were filled and count.
"""
import io
import os
import sys
import shutil

BASE = os.path.abspath(r"d:\Users\threesecond\OneDrive\Github\Mango_v3_i18n_zh\modules\lang_zh\classes")
EN = os.path.join(BASE, 'i18n.properties')
ZH = os.path.join(BASE, 'i18n_zh.properties')


def parse_properties(path):
    items = []
    with io.open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.rstrip('\n')
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                items.append((line, None, None, True))
                continue
            sep_index = None
            for i, ch in enumerate(line):
                if ch in ('=', ':'):
                    sep_index = i
                    break
            if sep_index is None:
                key = line.strip()
                val = ''
            else:
                key = line[:sep_index].strip()
                val = line[sep_index+1:].lstrip()
            items.append((line, key, val, False))
    return items


def build_map(items):
    m = {}
    for _, key, val, misc in items:
        if misc or key is None:
            continue
        if key not in m:
            m[key] = val
    return m


def main():
    if not os.path.exists(EN) or not os.path.exists(ZH):
        print('Missing files, ensure both EN and ZH exist under', BASE)
        sys.exit(2)

    en_items = parse_properties(EN)
    zh_items = parse_properties(ZH)

    en_map = build_map(en_items)
    zh_map = build_map(zh_items)

    # Backup current ZH
    bak2 = ZH + '.bak2'
    try:
        shutil.copyfile(ZH, bak2)
        print('Backup of current ZH created at', bak2)
    except Exception as e:
        print('Could not create backup:', e)
        sys.exit(1)

    filled = []
    out_lines = []
    for line, key, val, misc in zh_items:
        if misc:
            out_lines.append(line)
            continue
        # if zh value empty and english has a value, fill
        if (val is None or val == '') and key in en_map and en_map[key] != '':
            out_lines.append(f"{key}={en_map[key]}")
            filled.append(key)
        else:
            # preserve existing line (but normalize to key=val form)
            out_lines.append(f"{key}={val if val is not None else ''}")

    with io.open(ZH, 'w', encoding='utf-8', newline='\n') as f:
        for l in out_lines:
            f.write(l + '\n')

    print(f'Filled {len(filled)} keys in {ZH}')
    for k in filled:
        print(k)


if __name__ == '__main__':
    main()
