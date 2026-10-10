"""Build the runnable test page from the template, the word bank and the handwriting templates.

usage: python3 assemble.py template.html bank2.json glyphs.json chinese-vocab-test.html
glyphs.json comes from glyphs.py. Its stroke points are packed as raw bytes behind a small JSON header,
gzipped and base64-encoded into the page, so the result is one self-contained file.
"""
import base64, gzip, json, struct, sys

template, bank, glyphs, out = sys.argv[1:5]
html = open(template, encoding='utf-8').read()
for ph in ('__BANK__', '__GLYPHS__'):
    assert html.count(ph) == 1, 'template must contain exactly one ' + ph
data = open(bank, encoding='utf-8').read().strip()
g = json.load(open(glyphs, encoding='utf-8'))
head = json.dumps({'k': g['k'], 'c': g['c'], 'n': g['n']}, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
blob = struct.pack('<I', len(head)) + head + base64.b64decode(g['p'])
packed = base64.b64encode(gzip.compress(blob, 9)).decode('ascii')
html = html.replace('__BANK__', data.replace('</', '<\\/')).replace('__GLYPHS__', packed)
open(out, 'w', encoding='utf-8').write(html)
print('wrote', out, len(html.encode('utf-8')), 'bytes; glyph data', len(packed), 'chars')
