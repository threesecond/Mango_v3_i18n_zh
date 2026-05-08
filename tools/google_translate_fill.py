#!/usr/bin/env python3
"""
Fill untranslated keys in modules/lang_zh/classes/i18n_zh.properties using
Google Translate (to Traditional Chinese zh-TW) via API key.

Usage:
  - Set environment variable GOOGLE_API_KEY, or pass --key YOUR_KEY

Notes:
  - The script will backup the current i18n_zh.properties to .gtrans.bak
  - Outputs CSV report tools/lang_zh_google_filled.csv
  - Google Translate API: https://translation.googleapis.com/language/translate/v2
"""
import io
import os
import sys
import argparse
import csv
import requests
import time

BASE = os.path.abspath(r"d:\Users\threesecond\OneDrive\Github\Mango_v3_i18n_zh\modules\lang_zh\classes")
EN = os.path.join(BASE, 'i18n.properties')
ZH = os.path.join(BASE, 'i18n_zh.properties')
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lang_zh_google_filled.csv'))


def parse(path):
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


def translate_texts(texts, api_key, target='zh-TW'):
    # Google Translate v2 endpoint
    url = 'https://translation.googleapis.com/language/translate/v2'
    results = []
    # Batch texts in groups to avoid URL length issues
    for chunk_start in range(0, len(texts), 100):
        chunk = texts[chunk_start:chunk_start+100]
        data = {
            'q': chunk,
            'target': target,
            'format': 'text',
            'key': api_key
        }
        resp = requests.post(url, data=data)
        if resp.status_code != 200:
            raise RuntimeError(f'Translate API error: {resp.status_code} {resp.text}')
        js = resp.json()
        for item in js.get('data', {}).get('translations', []):
            results.append(item.get('translatedText'))
        time.sleep(0.1)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', help='Google API key')
    parser.add_argument('--dry', action='store_true', help='Dry run, do not write files')
    args = parser.parse_args()

    api_key = args.key or os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        print('No Google API key provided. Set env GOOGLE_API_KEY or pass --key.')
        print('See https://cloud.google.com/translate/docs/setup for obtaining API key.')
        sys.exit(2)

    en_items = parse(EN)
    zh_items = parse(ZH)
    en_order, en_map = build_map(en_items)
    _, zh_map = build_map(zh_items)

    # find untranslated: zh empty or same as english or no CJK
    to_translate = []
    keys_to_translate = []
    for k in en_order:
        eng = en_map.get(k, '')
        zh = zh_map.get(k, '')
        if zh == '' or zh == eng:
            if eng.strip() != '':
                to_translate.append(eng)
                keys_to_translate.append(k)

    print('Will translate', len(to_translate), 'entries')
    if not to_translate:
        return

    translations = translate_texts(to_translate, api_key)

    # backup
    bak = ZH + '.gtrans.bak'
    if not os.path.exists(bak):
        import shutil
        shutil.copyfile(ZH, bak)
        print('Backup created at', bak)
    else:
        print('Backup already exists at', bak)

    # apply translations
    filled = []
    zh_map_updated = dict(zh_map)
    for k, t in zip(keys_to_translate, translations):
        filled.append((k, en_map.get(k, ''), zh_map.get(k, ''), t))
        zh_map_updated[k] = t

    # rebuild zh file following english order
    out_lines = []
    for line, key, val, misc in en_items:
        if misc:
            out_lines.append(line)
            continue
        out_lines.append(f"{key}={zh_map_updated.get(key, '')}")

    if args.dry:
        print('Dry run; not writing files. Sample filled:', len(filled))
        for f in filled[:50]:
            print(f[0], '->', f[3])
        return

    with io.open(ZH, 'w', encoding='utf-8', newline='\n') as f:
        for l in out_lines:
            f.write(l + '\n')

    # write CSV
    with io.open(OUT, 'w', encoding='utf-8', newline='') as csvf:
        w = csv.writer(csvf)
        w.writerow(['key', 'english', 'previous_zh', 'new_zh'])
        for row in filled:
            w.writerow(row)

    print('Translated and wrote', len(filled), 'entries; CSV at', OUT)

if __name__ == '__main__':
    main()
