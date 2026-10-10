import json, re, random, sys
from collections import defaultdict
from wordfreq import top_n_list

CEDICT = sys.argv[1]
OUT = sys.argv[2]
random.seed(7)

CJK = re.compile(r'^[一-鿿]+$')
HAS_CJK = re.compile(r'[㐀-鿿]')
BAD_SENSE = re.compile(
    r'^(surname|variant of|old variant|archaic variant|Japanese variant|unofficial variant|'
    r'see |also written|also pr\.|abbr\.|abbr |used in|erhua|CL:|classifier|M:|'
    r'\(old\)|\(archaic\)|\(dialect\)|\(Cantonese\)|\(Tw\)|\(Hong Kong|\(Taiwan|\(Beijing dialect|'
    r'\(onom|\(particle|particle|\(prefix|\(suffix|interjection|\(interj|'
    r'\(grammatical|grammatical|\(used|used as|used for|used to|used before|used after|'
    r'(?:[A-Z][a-z]+ )*\(person\)|name of|radical|Kangxi|component|\(math\.\)|\(chemistry\)|chemical element|'
    r'\(Buddhism\)|\(Taoism\)|\(TCM\)|\(slang\)|\(Internet slang\)|\(neologism)', re.I)
STRIP_PREFIX = re.compile(r'^\((bound form|coll\.|literary|idiom|loanword|polite|honorific|humble|euphemism|derog\.|lit\.|formal|written|informal|fig\.|of sb|of a person)\)\s*', re.I)
VULGAR = re.compile(r'\b(vulva|penis|vagina|fuck|genital|testicle|sexual intercourse|prostitut|whore|semen|masturbat|anus|cunt|dick|pubic|intercourse|sodomy|adult film|porn|erotic|AV actress|rape|condom|orgasm)', re.I)
STOP = set('to a an the of one oneself sb sth in on at for and or with by as be is from up out into one\'s sb\'s sth\'s etc very not no it its that this'.split())

TONE = {'a': 'āáǎàa', 'e': 'ēéěèe', 'i': 'īíǐìi', 'o': 'ōóǒòo', 'u': 'ūúǔùu', 'ü': 'ǖǘǚǜü'}
def syl(s):
    s = s.replace('u:', 'ü').replace('v', 'ü')
    m = re.match(r'^([a-zü]+)([1-5])$', s, re.I)
    if not m:
        return s
    base, t = m.group(1), int(m.group(2))
    if t == 5:
        return base
    low = base.lower()
    if 'a' in low: idx = low.index('a')
    elif 'e' in low: idx = low.index('e')
    elif 'ou' in low: idx = low.index('o')
    else:
        idx = max(i for i, c in enumerate(low) if c in 'aeiouü')
    c = low[idx]
    return base[:idx] + TONE[c][t - 1] + base[idx + 1:]
def pinyin(p):
    return ' '.join(syl(x) for x in p.split())

def clean_senses(eng, word):
    out = []
    figs = [e for e in eng if e.startswith('fig. ')]
    src = figs if figs else eng
    for e in src:
        e = e.strip()
        if e.startswith('fig. '): e = e[5:]
        if e.startswith('lit. '): e = e[5:]
        prev = None
        while prev != e:
            prev = e
            e = STRIP_PREFIX.sub('', e).strip()
        if not e or HAS_CJK.search(e) or '[' in e: continue
        if BAD_SENSE.search(e): continue
        if re.search(r'\b(Tw|PRC)\b', e): continue
        if e.startswith('('): continue  # purely grammatical description
        if re.match(r'^[A-Z]', e) and not e.startswith('I ') and e not in ('I', 'OK'):
            # likely proper noun / place
            continue
        e = re.sub(r'\s*\((idiom|coll\.|literary|loanword)\)', '', e).strip()
        if VULGAR.search(e): return []
        if len(e) > 80 or not e: continue
        out.append(e)
    return out

ABBR = [(r"\bsb's\b", "someone's"), (r"\bsth's\b", "something's"), (r"\bsb\b", "someone"), (r"\bsth\b", "something"),
        (r"\besp\.", "especially"), (r"\betc\b\.?", "etc."), (r"\(cf\.\)", "(compare)"), (r"\bmath\.", "mathematics"),
        (r"\bmaths?\b\.", "mathematics"), (r"\bcoll\.", "colloquial"), (r"\bfig\.", "figuratively"), (r"\blit\.", "literally")]
def expand(d):
    for pat, rep in ABBR:
        d = re.sub(pat, rep, d)
    return d

def content_words(defn):
    ws = re.findall(r"[a-z]+", defn.lower())
    res = set()
    for w in ws:
        if w in STOP or len(w) < 3: continue
        # crude stemming
        for suf in ('ing', 'ed', 'es', 's', 'ly'):
            if w.endswith(suf) and len(w) - len(suf) >= 3:
                w = w[:-len(suf)]; break
        res.add(w)
    return res

data = json.load(open(CEDICT, encoding='utf-8'))
by_simp = defaultdict(list)
for e in data:
    by_simp[e['simplified']].append(e)

freq = top_n_list('zh', 100000)
OVR = json.load(open(sys.argv[3], encoding='utf-8'))
accepted = []
seen = set()
for w in freq:
    if w in seen or not CJK.match(w): continue
    seen.add(w)
    ents = [e for e in by_simp.get(w, []) if e['pinyin'][:1].islower()]
    if not ents: continue
    best = None
    for e in ents:
        s = clean_senses(e['english'], w)
        if not s: continue
        score = len(e['english'])
        if best is None or score > best[0]:
            best = (score, e, s)
    if not best: continue
    _, e, senses = best
    idiom = any('(idiom)' in x for x in e['english']) or len(w) >= 4
    # build short definition
    d = senses[0]
    if len(senses) > 1 and len(d) + len(senses[1]) + 2 <= 46 and not (content_words(senses[1]) <= content_words(d)):
        d = d + '; ' + senses[1]
    if len(d) > 70:
        d = re.split(r'[;,] ', d)[0]
        if len(d) > 70: continue
    if w in OVR: d = OVR[w] or 'x'
    d = expand(d)
    accepted.append({'s': w, 't': e['traditional'], 'p': pinyin(e['pinyin']), 'pn': e['pinyin'].lower().replace('u:', 'v'), 'd': d,
                     'i': 1 if idiom else 0, 'v': 1 if d.startswith('to ') else 0})

print('accepted', len(accepted), file=sys.stderr)

EDGES = [0, 1000, 2000, 3500, 5000, 7500, 10000, 14000, 19000, 25000, 32000, 40000]
EDGES = [e for e in EDGES if e <= len(accepted)]
bands = []
POOL = 140
for b in range(len(EDGES) - 1):
    lo, hi = EDGES[b], EDGES[b + 1]
    seg = accepted[lo:hi]
    multi = [x for x in seg if len(x['s']) >= 2]
    pool = random.sample(multi, min(POOL, len(multi)))
    pool = [x for x in pool if x['s'] not in OVR or OVR[x['s']]]
    for x in pool:
        x['r'] = accepted.index(x) + 1
    bands.append({'lo': lo + 1, 'hi': hi, 'words': pool})

# extra idiom distractor pool from all accepted idioms
idioms = [x for x in accepted[:40000] if x['i'] and len(x['s']) == 4]
idiom_pool = random.sample(idioms, min(260, len(idioms)))
out = {'bands': bands, 'idioms': [{'s': x['s'], 't': x['t'], 'd': x['d']} for x in idiom_pool], 'total': len(accepted)}
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('idioms', len(idioms), file=sys.stderr)
