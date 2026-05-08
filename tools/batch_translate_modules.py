#!/usr/bin/env python3
"""
Batch translate untranslated keys across modules/*/classes

Produces: tools/batch_translate_report.csv

Uses the same translator strategy as auto_translate_basic.py (googletrans -> deep-translator).
"""
from pathlib import Path
import csv
import time
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = ROOT / 'modules'
TOOLS = Path(__file__).resolve().parents[0]


def read_properties(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return [ln.rstrip('\n') for ln in f]


def parse_kv(lines):
    kv = {}
    order = []
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
        order.append(k)
    return kv, order


def needs_translation(zh_v, en_v):
    if not zh_v or not zh_v.strip():
        return True
    if zh_v.strip() == en_v.strip():
        return True
    # check CJK presence
    for ch in zh_v:
        if '\u4e00' <= ch <= '\u9fff' or '\u3400' <= ch <= '\u4dbf':
            return False
    return True


def translate_texts(texts, src='en', dest='zh-TW'):
    # reuse auto_translate_basic translation function by importing it
    try:
        from auto_translate_basic import translate_texts as tfunc
        return tfunc(texts, src=src, dest=dest)
    except Exception:
        # fallback: try importing as module from tools
        sys.path.insert(0, str(TOOLS))
        try:
            from auto_translate_basic import translate_texts as tfunc2
            return tfunc2(texts, src=src, dest=dest)
        except Exception as e:
            raise RuntimeError('Translator unavailable: ' + str(e))


def write_csv(rows, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['module', 'key', 'english', 'old_zh', 'translation'])
        for r in rows:
            writer.writerow([r['module'], r['key'], r['en'], r['old_zh'], r['trans']])


def main():
    report_rows = []
    summary = []
    for mod in MODULES_DIR.iterdir():
        classes = mod / 'classes'
        if not classes.exists() or not classes.is_dir():
            continue
        en_f = classes / 'i18n.properties'
        zh_f = classes / 'i18n_zh.properties'
        if not en_f.exists() or not zh_f.exists():
            continue

        en_lines = read_properties(en_f)
        zh_lines = read_properties(zh_f)
        en_kv, en_order = parse_kv(en_lines)
        zh_kv, _ = parse_kv(zh_lines)

        candidates = []
        for k in en_order:
            en_v = en_kv.get(k, '')
            zh_v = zh_kv.get(k, '')
            if needs_translation(zh_v, en_v):
                candidates.append({'key': k, 'en': en_v, 'zh': zh_v})

        if not candidates:
            summary.append({'module': mod.name, 'translated': 0})
            continue

        texts = [c['en'] for c in candidates]
        try:
            translations = translate_texts(texts, src='en', dest='zh-TW')
        except Exception as e:
            print('Translation failed for module', mod.name, ':', e)
            continue

        # prepare backup
        ts = time.strftime('%Y%m%d%H%M%S')
        backup = zh_f.with_suffix(zh_f.suffix + f'.{ts}.bak')
        shutil.copy2(zh_f, backup)

        # build trans map
        trans_map = {c['key']: t for c, t in zip(candidates, translations)}

        # write new zh lines preserving structure
        out_lines = []
        for ln in zh_lines:
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
            if k in trans_map and trans_map[k]:
                out_lines.append(f'{k}={trans_map[k]}')
                report_rows.append({'module': mod.name, 'key': k, 'en': en_kv.get(k, ''), 'old_zh': v, 'trans': trans_map[k]})
            else:
                out_lines.append(ln)

        # append missing keys (unlikely)
        zh_keys = set(zh_kv.keys())
        appended = 0
        for k in en_order:
            if k not in zh_keys:
                val = trans_map.get(k, en_kv.get(k, ''))
                out_lines.append(f'{k}={val}')
                appended += 1
                report_rows.append({'module': mod.name, 'key': k, 'en': en_kv.get(k, ''), 'old_zh': '', 'trans': val})

        # write file
        with zh_f.open('w', encoding='utf-8', newline='\n') as f:
            for ln in out_lines:
                f.write(ln + '\n')

    translated_count = len([r for r in report_rows if r['module'] == mod.name])
    summary.append({'module': mod.name, 'translated': translated_count})
    print(f"Module {mod.name}: translated {translated_count} entries (backup {backup})")

    # write global report
    write_csv(report_rows, TOOLS / 'batch_translate_report.csv')
    print('Batch translation complete. Report: tools/batch_translate_report.csv')


if __name__ == '__main__':
    main()
