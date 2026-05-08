#!/usr/bin/env python3
"""
Report untranslated keys in modules/lang_zh/classes/i18n_zh.properties compared to i18n.properties.
Criteria for untranslated:
 - zh value is empty
 - zh value equals english value
 - zh value contains no CJK characters (heuristic)
Outputs CSV: tools/lang_zh_untranslated.csv
"""
import io
import os
import csv
import re

BASE = os.path.abspath(r"d:\Users\threesecond\OneDrive\Github\Mango_v3_i18n_zh\modules\lang_zh\classes")
EN = os.path.join(BASE, 'i18n.properties')
ZH = os.path.join(BASE, 'i18n_zh.properties')
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lang_zh_untranslated.csv'))

CJK_RE = re.compile('[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]')


def parse(path):
    m = {}
    order = []
    with io.open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.rstrip('\n')
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
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
            if key not in m:
                m[key] = val
                order.append(key)
    return order, m


def is_untranslated(eng, zh):
    if zh is None or zh == '':
        return True, 'empty'
    if eng is not None and zh == eng:
        return True, 'same_as_english'
    if not CJK_RE.search(zh):
        return True, 'no_cjk'
    return False, ''


def main():
    if not os.path.exists(EN) or not os.path.exists(ZH):
        print('Missing files', EN, ZH)
        return
    order, en_map = parse(EN)
    _, zh_map = parse(ZH)

    rows = []
    for k in order:
        eng = en_map.get(k, '')
        zh = zh_map.get(k, '')
        u, reason = is_untranslated(eng, zh)
        if u:
            rows.append([k, eng, zh, reason])

    with io.open(OUT, 'w', encoding='utf-8', newline='') as csvf:
        writer = csv.writer(csvf)
        writer.writerow(['key', 'english', 'zh_value', 'reason'])
        writer.writerows(rows)

    print('Found', len(rows), 'untranslated keys. CSV at', OUT)
    for r in rows[:200]:
        print(r[0], r[3])

if __name__ == '__main__':
    main()
