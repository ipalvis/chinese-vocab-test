"""Add listening and writing data to bank.json.

usage: python3 enrich.py bank.json cedict.json hanzi-writer-data/ bank_out.json strokes.json

Per quiz word adds:
  xm  1 = leave out of Mandarin listening (a more common word sounds identical, tones included)
  jp  Jyutping (Cantonese reading of the traditional form), absent when unknown
  xc  1 = leave out of Cantonese listening (no reading, or a more common identical-sounding word)
  ws / wt  1 = writable in simplified / traditional (2-3 characters, stroke data for every character)
strokes.json maps each needed character to Hanzi Writer data {strokes, medians}.
"""
import json, os, re, sys
from collections import defaultdict
import math
from wordfreq import top_n_list, get_frequency_dict
import ToJyutping

bank_path, cedict_path, hwd_dir, out_path, strokes_path = sys.argv[1:6]
bank = json.load(open(bank_path, encoding='utf-8'))
cedict = json.load(open(cedict_path, encoding='utf-8'))

CJK = re.compile(r'^[一-鿿]+$')
top = [w for w in top_n_list('zh', 100000) if CJK.match(w)]
rank = {w: i for i, w in enumerate(top)}

# character frequency = summed frequency of every word the character appears in (Zipf scale)
char_freq = defaultdict(float)
for w, f in get_frequency_dict('zh').items():
    if CJK.match(w):
        for c in w:
            char_freq[c] += f
def char_zipf(c):
    f = char_freq.get(c, 0)
    return math.log10(f * 1e9) if f > 0 else 0.0

# Mandarin: toned pinyin -> words (simplified) among common dictionary words
by_pn = defaultdict(set)
trad_of = {}
for e in cedict:
    if e['pinyin'][:1].islower() and e['simplified'] in rank:
        by_pn[e['pinyin'].lower().replace('u:', 'v')].add(e['simplified'])
        trad_of.setdefault(e['simplified'], e['traditional'])

def jyut(text):
    try:
        lst = ToJyutping.get_jyutping_list(text)
    except Exception:
        return None
    if not lst or any(j is None for _, j in lst):
        return None
    return ' '.join(j for _, j in lst)

# Cantonese: Jyutping of the 40k most common dictionary words (traditional form)
by_jp = defaultdict(set)
for w in top[:40000]:
    t = trad_of.get(w)
    if not t:
        continue
    j = jyut(t)
    if j:
        by_jp[j].add(w)

have = set(os.path.splitext(f)[0] for f in os.listdir(hwd_dir) if f.endswith('.json'))
need = set()
words = [w for b in bank['bands'] for w in b['words']]
stats = defaultdict(int)
for w in words:
    r = rank.get(w['s'], 10**9)
    if any(rank.get(o, 10**9) < r for o in by_pn.get(w['pn'], ()) if o != w['s']):
        w['xm'] = 1; stats['xm'] += 1
    j = jyut(w['t'])
    if j:
        w['jp'] = j
        if any(rank.get(o, 10**9) < r for o in by_jp.get(j, ()) if o != w['s']):
            w['xc'] = 1; stats['xc_homophone'] += 1
    else:
        w['xc'] = 1; stats['xc_noreading'] += 1
    if 2 <= len(w['s']) <= 3:
        if all(c in have for c in w['s']):
            w['ws'] = 1; need.update(w['s']); stats['ws'] += 1
        if all(c in have for c in w['t']):
            w['wt'] = 1; need.update(w['t']); stats['wt'] += 1
        if w.get('ws') or w.get('wt'):
            # per-character difficulty for partial credit in writing: rarer characters weigh more
            w['cw'] = [max(1.0, round(8 - char_zipf(c), 1)) for c in w['s']]

strokes = {}
for c in sorted(need):
    d = json.load(open(os.path.join(hwd_dir, c + '.json'), encoding='utf-8'))
    strokes[c] = {'strokes': d['strokes'], 'medians': d['medians']}

json.dump(bank, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(strokes, open(strokes_path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(dict(stats), 'words', len(words), 'stroke chars', len(strokes), file=sys.stderr)
