#!/usr/bin/env python3
"""
Apply specific agreed terminology changes to i18n_zh.properties.

Changes applied:
- common.point -> 點位
- common.cronPattern -> Cron 表達式
- dsEdit.cronPattern -> Cron 表達式

Creates backup: i18n_zh.properties.termmap2.bak
Writes report: tools/lang_zh_termmap_applied_update.csv
"""
from pathlib import Path
import shutil
import csv

ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = ROOT / 'modules' / 'lang_zh' / 'classes'
ZH_FILE = MODULE_DIR / 'i18n_zh.properties'
BACKUP = ZH_FILE.with_suffix(ZH_FILE.suffix + '.termmap2.bak')
REPORT = Path(__file__).resolve().parents[0] / 'lang_zh_termmap_applied_update.csv'

CHANGES = {
    'common.point': '點位',
    'common.cronPattern': 'Cron 表達式',
    'dsEdit.cronPattern': 'Cron 表達式',
}


def read_props(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return [ln.rstrip('\n') for ln in f]


def parse_kv(lines):
    kv = {}
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith('#') or s.startswith('!'):
            continue
        pos = None
        for sep in ('=', ':'):
            i = ln.find(sep)
            if i != -1:
                pos = i
                break
        if pos is None:
            continue
        k = ln[:pos].strip()
        v = ln[pos+1:].lstrip()
        kv[k] = v
    return kv


def apply_changes(lines, kv_map):
    out = []
    applied = []
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith('#') or s.startswith('!'):
            out.append(ln)
            continue
        pos = None
        for sep in ('=', ':'):
            i = ln.find(sep)
            if i != -1:
                pos = i
                break
        if pos is None:
            out.append(ln)
            continue
        k = ln[:pos].strip()
        v = ln[pos+1:].lstrip()
        if k in CHANGES:
            new_v = CHANGES[k]
            if new_v != v:
                applied.append({'key': k, 'old': v, 'new': new_v})
            out.append(f'{k}={new_v}')
        else:
            out.append(ln)
    return out, applied


def main():
    if not ZH_FILE.exists():
        print('ZH file not found:', ZH_FILE)
        return

    lines = read_props(ZH_FILE)
    kv = parse_kv(lines)

    # show what will change
    pending = {k: (kv.get(k, ''), v) for k, v in CHANGES.items()}
    print('Pending changes:')
    for k, (old, new) in pending.items():
        print(f' - {k}: "{old}" -> "{new}"')

    # backup
    shutil.copy2(ZH_FILE, BACKUP)
    print('Backup created at', BACKUP)

    out_lines, applied = apply_changes(lines, kv)

    # write back
    with ZH_FILE.open('w', encoding='utf-8', newline='\n') as f:
        for ln in out_lines:
            f.write(ln + '\n')

    # write report
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with REPORT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['key', 'old_value', 'new_value'])
        for r in applied:
            writer.writerow([r['key'], r['old'], r['new']])

    print(f'Applied {len(applied)} changes. Report: {REPORT}')


if __name__ == '__main__':
    main()
