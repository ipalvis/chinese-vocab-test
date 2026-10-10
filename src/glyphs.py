"""Build compact stroke templates for the handwriting recognizer.

usage: python3 glyphs.py hanzi-writer-data/package glyphs.json
Each character's strokes (Make Me a Hanzi medians) are resampled to K evenly spaced points
in a 0-255 box (y down), packed as bytes: x0 y0 x1 y1 ... per stroke.
"""
import base64, json, math, os, sys

K = 8
src, out = sys.argv[1:3]

def resample(pts, k):
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(seg)
    if total == 0:
        return [pts[0]] * k
    res, acc, i = [], 0.0, 0
    for j in range(k):
        target = total * j / (k - 1)
        while i < len(seg) - 1 and acc + seg[i] < target:
            acc += seg[i]; i += 1
        t = 0 if seg[i] == 0 else min(1, (target - acc) / seg[i])
        a, b = pts[i], pts[i + 1]
        res.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return res

chars, counts, data = [], [], bytearray()
for f in sorted(os.listdir(src)):
    if not f.endswith('.json'):
        continue
    c = f[:-5]
    if len(c) != 1:
        continue
    d = json.load(open(os.path.join(src, f), encoding='utf-8'))
    strokes = []
    for m in d['medians']:
        pts = [(x / 1024, (900 - y) / 1024) for x, y in m]
        if len(pts) == 1:
            pts = pts * 2
        strokes.append(resample(pts, K))
    chars.append(c); counts.append(len(strokes))
    for s in strokes:
        for x, y in s:
            data.append(max(0, min(255, round(x * 255))))
            data.append(max(0, min(255, round(y * 255))))
json.dump({'k': K, 'c': ''.join(chars), 'n': counts, 'p': base64.b64encode(bytes(data)).decode()}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(len(chars), 'chars', len(data), 'bytes', file=sys.stderr)
