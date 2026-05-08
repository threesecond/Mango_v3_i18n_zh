#!/usr/bin/env python3
"""
Generate i18n_translation.csv from i18n.properties (origin) and i18n_zh.properties (translated)

Usage: run from workspace root or with files in the same folder. By default it writes
`i18n_translation.csv` to the same folder as the input files.
"""
import re
import csv
from pathlib import Path
import sys


def load_properties(path: Path):
    props = {}
    if not path.exists():
        return props
    with path.open('r', encoding='utf-8') as f:
        for raw in f:
            line = raw.rstrip('\n')
            if not line or line.lstrip().startswith('#'):
                continue
            # split at first '=' or ':'
            m = re.split(r"(?<!\\)[=:]", line, maxsplit=1)
            if len(m) == 1:
                # maybe no separator, treat whole line as key with empty value
                key = m[0].strip()
                val = ''
            else:
                key = m[0].strip()
                val = m[1].lstrip()
            # unescape common escapes
            val = val.replace('\\n', '\n')
            props[key] = val
    return props


def main():
    # locate files relative to this script
    base = Path(__file__).resolve().parent
    en_file = base / 'i18n.properties'
    zh_file = base / 'i18n_zh.properties'
    out_file = base / 'i18n_translation.csv'

    en = load_properties(en_file)
    zh = load_properties(zh_file)

    keys = list(en.keys())

    with out_file.open('w', encoding='utf-8', newline='') as csvf:
        writer = csv.writer(csvf)
        writer.writerow(['key', 'origin', 'translated'])
        for k in keys:
            origin = en.get(k, '')
            translated = zh.get(k, '')
            writer.writerow([k, origin, translated])

    print(f'Wrote {out_file} ({len(keys)} entries)')


if __name__ == '__main__':
    main()
