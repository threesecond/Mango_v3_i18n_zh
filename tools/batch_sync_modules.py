#!/usr/bin/env python3
"""
Batch sync for modules: for each module under modules/*/classes that contains
both i18n.properties and i18n_zh.properties, insert missing keys (in English order)
and fill empty chinese values with the English value. Creates backups and a CSV report.
"""
import io
import os
import sys
import shutil
import csv
from datetime import datetime

ROOT = os.path.abspath(r"d:\Users\threesecond\OneDrive\Github\Mango_v3_i18n_zh\modules")
TOOLS = os.path.abspath(os.path.join(os.path.dirname(__file__)))
REPORT = os.path.join(TOOLS, 'batch_report.csv')


def read_props(path):
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
    order = []
    for _, key, val, misc in items:
        if misc or key is None:
            continue
        if key not in m:
            m[key] = val
            order.append(key)
    return order, m


def process_pair(en_path, zh_path, module_name, csv_writer):
    en_items = read_props(en_path)
    zh_items = read_props(zh_path)
    en_order, en_map = build_map(en_items)
    zh_order, zh_map = build_map(zh_items)

    missing = [k for k in en_order if k not in zh_map]
    # backup zh
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    bak = zh_path + '.' + ts + '.bak'
    shutil.copyfile(zh_path, bak)

    # fill: produce output following english order and fill empty values
    out_lines = []
    filled_keys = []
    for line, key, val, misc in en_items:
        if misc:
            out_lines.append(line)
            continue
        # if zh has key and non-empty value, use it
        zh_val = zh_map.get(key)
        if zh_val is not None and zh_val != '':
            out_lines.append(f"{key}={zh_val}")
        else:
            # prefer english value if present
            eng_val = en_map.get(key, '')
            out_lines.append(f"{key}={eng_val}")
            # record if zh was missing or empty
            prev = '' if key not in zh_map else ''
            csv_writer.writerow([module_name, key, eng_val, prev])
            filled_keys.append(key)

    with io.open(zh_path, 'w', encoding='utf-8', newline='\n') as f:
        for l in out_lines:
            f.write(l + '\n')

    return len(missing), filled_keys, bak


def main():
    rows = []
    total_missing = 0
    total_filled = 0
    with io.open(REPORT, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['module', 'key', 'english_value', 'previous_zh_value'])
        # traverse modules
        for child in os.listdir(ROOT):
            child_path = os.path.join(ROOT, child)
            if not os.path.isdir(child_path):
                continue
            classes_dir = os.path.join(child_path, 'classes')
            if not os.path.isdir(classes_dir):
                continue
            en = os.path.join(classes_dir, 'i18n.properties')
            zh = os.path.join(classes_dir, 'i18n_zh.properties')
            if os.path.exists(en) and os.path.exists(zh):
                print('Processing', child)
                missing_count, filled_keys, bak = process_pair(en, zh, child, writer)
                total_missing += missing_count
                total_filled += len(filled_keys)
                print(f'  missing keys: {missing_count}, filled: {len(filled_keys)}, backup: {bak}')

    print('Batch complete')
    print('Total missing keys across modules (inserted positions):', total_missing)
    print('Total keys filled with english values:', total_filled)
    print('CSV report at', REPORT)

if __name__ == '__main__':
    main()
