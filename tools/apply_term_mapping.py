#!/usr/bin/env python3
"""
Apply a small terminology mapping to the translated i18n_zh.properties as a dry-run preview.

Generates: tools/lang_zh_termmap_preview.csv
Does NOT modify the original file in dry-run mode.

Mapping is small and editable in the script; add entries like '觀點' -> '點' to fix domain terms.
"""
import csv
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = ROOT / 'modules' / 'lang_zh' / 'classes'
ZH_FILE = MODULE_DIR / 'i18n_zh.properties'
TOOLS = Path(__file__).resolve().parents[0]

# Default mapping: wrong machine translations -> preferred term
DEFAULT_MAP = {
    '觀點': '點',
    '觀察點': '點',
    '圖像圖': '圖表',
    '消除': '移除',
    '放': '設定',
    '克朗模式': 'Cron 模式',
}


def read_props(path: Path):
    lines = []
    with path.open('r', encoding='utf-8') as f:
        for ln in f:
            lines.append(ln.rstrip('\n'))
    return lines


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
            k = ln.strip()
            v = ''
        else:
            k = ln[:pos].strip()
            v = ln[pos+1:].lstrip()
        kv[k] = v
    return kv


def apply_mapping(value: str, mapping: dict):
    """Safer mapping: only replace when the whole value equals the 'wrong' token,
    or when the 'wrong' token is an ASCII word (use word boundaries).

    This avoids replacing short CJK characters inside longer words (e.g. '放' inside '放棄').
    """
    import re

    new = value
    # sort by length descending so longer phrases are matched first
    for wrong, right in sorted(mapping.items(), key=lambda x: -len(x[0])):
        if new == wrong:
            new = right
            break
        # for ASCII words (letters/numbers), allow word-boundary replacement
        if any(('a' <= ch.lower() <= 'z') or ('0' <= ch <= '9') for ch in wrong):
            pattern = r'\b' + re.escape(wrong) + r'\b'
            repl = re.sub(pattern, right, new)
            if repl != new:
                new = repl
    return new


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--map-file', help='Optional CSV mapping file with wrong,right')
    p.add_argument('--out', help='Preview CSV output', default=str(TOOLS / 'lang_zh_termmap_preview.csv'))
    p.add_argument('--apply', action='store_true', help='Apply the mapping to the i18n_zh.properties (will backup)')
    p.add_argument('--applied-out', help='CSV file to write applied changes', default=str(TOOLS / 'lang_zh_termmap_applied.csv'))
    args = p.parse_args()

    if not ZH_FILE.exists():
        print('ZH file not found:', ZH_FILE)
        return

    lines = read_props(ZH_FILE)
    kv = parse_kv(lines)

    mapping = DEFAULT_MAP.copy()
    if args.map_file:
        mf = Path(args.map_file)
        if mf.exists():
            with mf.open('r', encoding='utf-8') as f:
                for ln in f:
                    ln = ln.strip()
                    if not ln:
                        continue
                    parts = ln.split(',', 1)
                    if len(parts) == 2:
                        mapping[parts[0]] = parts[1]

    rows = []
    for k, v in kv.items():
        new_v = apply_mapping(v, mapping)
        if new_v != v:
            rows.append({'key': k, 'old': v, 'new': new_v})

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['key', 'old_value', 'new_value'])
        for r in rows:
            writer.writerow([r['key'], r['old'], r['new']])

    print(f'Preview written to {outp} with {len(rows)} proposed replacements')

    if args.apply:
        # backup and apply
        backup = ZH_FILE.with_suffix(ZH_FILE.suffix + '.termmap.bak')
        import shutil
        shutil.copy2(ZH_FILE, backup)
        print('Backup created at', backup)

        # Read original lines and replace values for listed keys
        orig_lines = read_props(ZH_FILE)
        key_to_new = {r['key']: r['new'] for r in rows}
        out_lines = []
        for ln in orig_lines:
            s = ln.strip()
            if not s or s.startswith('#') or s.startswith('!'):
                out_lines.append(ln)
                continue
            pos = None
            for sep in ('=', ':'):
                i = ln.find(sep)
                if i != -1:
                    pos = i
                    break
            if pos is None:
                out_lines.append(ln)
                continue
            k = ln[:pos].strip()
            v = ln[pos+1:].lstrip()
            if k in key_to_new:
                out_lines.append(f'{k}={key_to_new[k]}')
            else:
                out_lines.append(ln)

        # write back
        with ZH_FILE.open('w', encoding='utf-8', newline='\n') as f:
            for l in out_lines:
                f.write(l + '\n')

        # write applied CSV
        with Path(args.applied_out).open('w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['key', 'old_value', 'new_value'])
            for r in rows:
                writer.writerow([r['key'], r['old'], r['new']])
        print('Applied mapping and wrote report to', args.applied_out)


if __name__ == '__main__':
    main()
