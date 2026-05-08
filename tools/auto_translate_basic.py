#!/usr/bin/env python3
"""
Basic auto-translate script for i18n properties using local/basic translators.

Features:
- Detect untranslated keys in `modules/lang_zh/classes/i18n_zh.properties`.
- Translate them using `googletrans` (unofficial) by default.
- Supports --dry to preview translations and write CSV at `tools/lang_zh_google_preview.csv`.
- On non-dry run: backup original file and write translated values back.

Usage examples:
  python tools/auto_translate_basic.py --dry --limit 50
  python tools/auto_translate_basic.py --method googletrans

Note: This script will attempt to pip-install `googletrans==4.0.0-rc1` if it's missing.
"""
import argparse
import csv
import os
import sys
import shutil
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parents[1] / 'modules' / 'lang_zh' / 'classes'
EN_FILE = MODULE_DIR / 'i18n.properties'
ZH_FILE = MODULE_DIR / 'i18n_zh.properties'
TOOLS_DIR = Path(__file__).resolve().parents[0]


def ensure_googletrans():
    try:
        import googletrans  # noqa: F401
        from googletrans import Translator  # noqa: F401
        return True
    except Exception:
        print('googletrans not found, attempting to install via pip...')
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'googletrans==4.0.0-rc1'])
        try:
            import googletrans  # noqa: F401
            return True
        except Exception as e:
            print('Failed to import googletrans after install:', e)
            return False


def read_properties(path: Path):
    lines = []
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open('r', encoding='utf-8') as f:
        for ln in f:
            lines.append(ln.rstrip('\n'))
    return lines


def parse_properties(lines):
    """Return list of tuples (line_type, content)
    line_type: 'kv' -> (key, value), 'comment' -> raw line, 'empty' -> ''
    """
    out = []
    for ln in lines:
        stripped = ln.strip()
        if not stripped:
            out.append(('empty', ln))
        elif stripped.startswith('#') or stripped.startswith('!'):
            out.append(('comment', ln))
        else:
            # split on first '=' or ':'
            sep_pos = None
            for sep in ('=', ':'):
                pos = ln.find(sep)
                if pos != -1:
                    sep_pos = pos
                    sep_char = sep
                    break
            if sep_pos is None:
                # treat whole line as key with empty value
                key = ln.strip()
                val = ''
            else:
                key = ln[:sep_pos].strip()
                val = ln[sep_pos+1:].lstrip()
            out.append(('kv', (key, val)))
    return out


def build_kv_map(parsed):
    kv = {}
    order = []
    for t, content in parsed:
        if t == 'kv':
            k, v = content
            kv[k] = v
            order.append(k)
    return kv, order


def needs_translation(zh_val, en_val):
    if not zh_val or not zh_val.strip():
        return True
    if zh_val.strip() == en_val.strip():
        return True
    # quick heuristic: if no CJK char found, likely untranslated
    for ch in zh_val:
        if '\u4e00' <= ch <= '\u9fff' or '\u3400' <= ch <= '\u4dbf':
            return False
    return True


def translate_texts(texts, src='en', dest='zh-TW'):
    # texts: list of strings
    # returns list of translated strings in same order
    results = []
    # Try googletrans first (if installed/available)
    try:
        from googletrans import Translator
        translator = Translator()
        BATCH = 50
        for i in range(0, len(texts), BATCH):
            batch = texts[i:i+BATCH]
            try:
                trans = translator.translate(batch, src=src, dest=dest)
            except Exception as e:
                print('googletrans batch translation error:', e)
                raise
            # translator.translate returns a single object for single input
            if not isinstance(trans, list):
                trans = [trans]
            for t in trans:
                # guard against None
                txt = getattr(t, 'text', None)
                results.append(txt or '')
        # If we got here with non-empty results, return them
        if any(results):
            return results
    except Exception:
        print('googletrans unavailable or failed; will attempt deep-translator fallback')

    # Fallback to deep-translator (web-based)
    try:
        from deep_translator import GoogleTranslator as DeepGoogle
    except Exception:
        # attempt to install deep-translator
        import subprocess
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'deep-translator'])
            from deep_translator import GoogleTranslator as DeepGoogle
        except Exception as e:
            print('deep-translator not available and installation failed:', e)
            raise RuntimeError('No available translator')

    results = []
    # deep-translator expects 'zh-TW' or 'zh-CN' as shown in supported languages mapping.
    target_lang = dest
    for batch_start in range(0, len(texts), 50):
        batch = texts[batch_start:batch_start+50]
        try:
            # deep-translator can accept a single string or list
            translated = DeepGoogle(source=src, target=target_lang).translate_batch(batch)
            # translate_batch returns list
            if isinstance(translated, list):
                results.extend(translated)
            else:
                # single string? wrap it
                results.append(translated)
        except Exception as e:
            # try single-item fallback
            for t in batch:
                try:
                    tr = DeepGoogle(source=src, target=target_lang).translate(t)
                    results.append(tr)
                except Exception as e2:
                    print('deep-translator failed for item:', e2)
                    results.append('')
    return results


def write_preview_csv(rows, csv_path: Path):
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['key', 'english', 'current_zh', 'translation'])
        for r in rows:
            writer.writerow([r['key'], r['en'], r['zh'] or '', r['trans'] or ''])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--method', choices=['googletrans'], default='googletrans')
    p.add_argument('--dry', action='store_true', help='preview only, do not write files')
    p.add_argument('--limit', type=int, default=0, help='limit number of translations (0 = all)')
    args = p.parse_args()

    if not EN_FILE.exists() or not ZH_FILE.exists():
        print('Expected files not found:')
        print('EN:', EN_FILE)
        print('ZH:', ZH_FILE)
        sys.exit(1)

    en_lines = read_properties(EN_FILE)
    zh_lines = read_properties(ZH_FILE)

    en_parsed = parse_properties(en_lines)
    zh_parsed = parse_properties(zh_lines)

    en_kv, en_order = build_kv_map(en_parsed)
    zh_kv, _ = build_kv_map(zh_parsed)

    candidates = []
    for k in en_order:
        en_v = en_kv.get(k, '')
        zh_v = zh_kv.get(k, '')
        if needs_translation(zh_v, en_v):
            candidates.append({'key': k, 'en': en_v, 'zh': zh_v})

    if args.limit and args.limit > 0:
        candidates = candidates[:args.limit]

    if not candidates:
        print('No candidates found for translation.')
        return

    print(f'Found {len(candidates)} candidates for translation (method={args.method}, dry={args.dry})')

    if args.method == 'googletrans':
        ok = ensure_googletrans()
        if not ok:
            print('googletrans installation/import failed. Aborting.')
            sys.exit(1)
        texts = [c['en'] for c in candidates]
        try:
            translations = translate_texts(texts, src='en', dest='zh-TW')
        except Exception as e:
            print('Translation failed:', e)
            sys.exit(1)
    else:
        translations = ['' for _ in candidates]

    rows = []
    for c, t in zip(candidates, translations):
        rows.append({'key': c['key'], 'en': c['en'], 'zh': c['zh'], 'trans': t})

    preview_csv = TOOLS_DIR / 'lang_zh_google_preview.csv'
    write_preview_csv(rows, preview_csv)
    print('Preview CSV written to', preview_csv)

    if args.dry:
        print('Dry run complete; no files were modified.')
        return

    # Real write: create backup and write updated zh file (preserving comments/structure)
    backup = ZH_FILE.with_suffix(ZH_FILE.suffix + '.gtrans.bak')
    shutil.copy2(ZH_FILE, backup)
    print('Backup created at', backup)

    # Build a map of translations
    trans_map = {r['key']: r['trans'] for r in rows}

    # Reconstruct zh file lines: when encountering a kv with key in trans_map, replace value
    out_lines = []
    for t, content in zh_parsed:
        if t == 'kv':
            k, v = content
            if k in trans_map and trans_map[k]:
                new_v = trans_map[k]
                out_lines.append(f'{k}={new_v}')
            else:
                out_lines.append(f'{k}={v}')
        elif t == 'comment' or t == 'empty':
            out_lines.append(content)

    # For any keys that exist in EN but not in ZH file at all, append them in EN order
    zh_keys = set(zh_kv.keys())
    appended = 0
    for k in en_order:
        if k not in zh_keys:
            val = trans_map.get(k, en_kv.get(k, ''))
            out_lines.append(f'{k}={val}')
            appended += 1

    ZH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with ZH_FILE.open('w', encoding='utf-8', newline='\n') as f:
        for ln in out_lines:
            f.write(ln + '\n')

    print(f'Wrote translated file with {len(rows)} replaced and {appended} appended entries.')
    # Also write final CSV of applied translations
    final_csv = TOOLS_DIR / 'lang_zh_google_filled.csv'
    write_preview_csv(rows, final_csv)
    print('Applied translations and wrote report to', final_csv)


if __name__ == '__main__':
    main()
