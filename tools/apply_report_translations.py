#!/usr/bin/env python3
"""Apply translations from a CSV report to module i18n_zh.properties files.

CSV expected columns (with or without header):
 module,key,english,old_zh,translation

Usage:
  python tools/apply_report_translations.py --csv tools/batch_translate_report.csv --dry
  python tools/apply_report_translations.py --csv tools/batch_translate_report.csv --apply

Dry-run will write `tools/report_apply_preview.csv`.
Apply will backup each changed properties file as `<file>.apply.<timestamp>.bak` and write `tools/report_apply_result.csv`.
"""
import csv
import argparse
import os
import sys
from datetime import datetime


def read_properties_lines(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().splitlines()


def write_properties_lines(path, lines):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write('\n'.join(lines) + ('\n' if lines and not lines[-1].endswith('\n') else ''))


def parse_properties(lines):
    """Return dict key->(index,line,key,sep,value) and list of lines."""
    mapping = {}
    for idx, raw in enumerate(lines):
        s = raw.lstrip()
        if not s or s.startswith('#') or s.startswith('!'):
            continue
        # split on first = or :
        for sep in ('=', ':'):
            if sep in raw:
                k, v = raw.split(sep, 1)
                key = k.strip()
                val = v.lstrip()
                mapping[key] = (idx, raw, key, sep, val)
                break
        else:
            # no sep, maybe a key with empty value
            key = raw.strip()
            mapping[key] = (idx, raw, key, '=', '')
    return mapping


def load_csv(path):
    rows = []
    with open(path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        for r in reader:
            if not r:
                continue
            # allow optional header
            if r[0].strip().lower() == 'module' and len(r) >= 5:
                continue
            # Expect at least 5 columns; if more, join trailing as translation
            if len(r) >= 5:
                module = r[0].strip()
                key = r[1].strip()
                english = r[2].strip()
                old_zh = r[3].strip()
                translation = r[4].strip()
            else:
                # skip malformed rows
                continue
            rows.append((module, key, english, old_zh, translation))
    return rows


def backup_file(path):
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    dest = f"{path}.apply.{ts}.bak"
    with open(path, 'rb') as src, open(dest, 'wb') as dst:
        dst.write(src.read())
    return dest


def apply_translations(csv_path, dry=True, out_preview='tools/report_apply_preview.csv', out_result='tools/report_apply_result.csv'):
    rows = load_csv(csv_path)
    # group by module
    by_module = {}
    for module, key, english, old_zh, translation in rows:
        by_module.setdefault(module, []).append((key, english, old_zh, translation))

    preview_rows = []
    result_rows = []

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    for module, entries in sorted(by_module.items()):
        mod_props_dir = os.path.join(repo_root, 'modules', module, 'classes')
        zh_path = os.path.join(mod_props_dir, 'i18n_zh.properties')
        en_path = os.path.join(mod_props_dir, 'i18n.properties')

        if not os.path.exists(zh_path):
            for key, english, old_zh, translation in entries:
                preview_rows.append((module, key, old_zh, translation, 'no_zh_file'))
            continue

        lines = read_properties_lines(zh_path)
        mapping = parse_properties(lines)

        changed = False

        for key, english, old_zh, translation in entries:
            if not translation:
                preview_rows.append((module, key, old_zh, translation, 'empty_translation'))
                continue
            if key in mapping:
                idx, raw, k, sep, old_val = mapping[key]
                # strip any leading whitespace from old_val for comparison
                old_val_stripped = old_val.rstrip('\r\n')
                if old_val_stripped == translation:
                    preview_rows.append((module, key, old_val_stripped, translation, 'no_change'))
                else:
                    preview_rows.append((module, key, old_val_stripped, translation, 'will_replace'))
                    if not dry:
                        # replace line at idx preserving key and sep but using = as sep
                        lines[idx] = f"{k}={translation}"
                        changed = True
            else:
                # key not present -> will append
                preview_rows.append((module, key, '', translation, 'will_insert'))
                if not dry:
                    lines.append(f"{key}={translation}")
                    changed = True

        if not dry and changed:
            bak = backup_file(zh_path)
            write_properties_lines(zh_path, lines)
            for key, english, old_zh, translation in entries:
                # after apply, record as applied or not
                if key in mapping or True:
                    result_rows.append((module, key, translation, 'applied', zh_path, bak))

    # write preview/result CSVs
    os.makedirs(os.path.dirname(out_preview), exist_ok=True)
    with open(out_preview, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['module', 'key', 'old_zh', 'proposed_translation', 'action'])
        for r in preview_rows:
            w.writerow(r)

    if not dry:
        with open(out_result, 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['module', 'key', 'applied_translation', 'status', 'file', 'backup'])
            for r in result_rows:
                w.writerow(r)

    return out_preview, (out_result if not dry else None)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', '-c', default='tools/batch_translate_report.csv')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--dry', action='store_true', default=True, dest='dry')
    group.add_argument('--apply', action='store_true', dest='apply')
    # default outputs should be at repo root 'tools/' not under modules/
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    default_preview = os.path.join(repo_root, 'tools', 'report_apply_preview.csv')
    default_result = os.path.join(repo_root, 'tools', 'report_apply_result.csv')
    parser.add_argument('--preview-out', default=default_preview)
    parser.add_argument('--result-out', default=default_result)
    args = parser.parse_args()

    do_dry = not args.apply
    preview, result = apply_translations(args.csv, dry=do_dry, out_preview=args.preview_out, out_result=args.result_out)
    print('Preview written to', preview)
    if result:
        print('Result written to', result)


if __name__ == '__main__':
    main()
