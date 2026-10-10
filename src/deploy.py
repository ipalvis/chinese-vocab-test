"""Turn the built test page into a complete website file for Cloudflare Pages.

usage: python3 src/deploy.py chinese-vocab-test.html public/index.html

The built page is written to be dropped into a host page (no <html>/<head>/<body> of its own).
This wraps it in a full HTML document with the head tags a public website needs.
"""
import sys

src, out = sys.argv[1:3]
page = open(src, encoding='utf-8').read()
cut = page.index('</style>') + len('</style>')
head_part, body_part = page[:cut], page[cut:]

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="How many Chinese words can you read, hear and write? A free adaptive test that estimates your vocabulary in simplified or traditional characters.">
<meta name="theme-color" media="(prefers-color-scheme: light)" content="#eef1ec">
<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#111714">
<meta name="color-scheme" content="light dark">
<meta property="og:type" content="website">
<meta property="og:title" content="词汇量 Chinese Vocabulary Test">
<meta property="og:description" content="Estimate how many Chinese words you can read, understand by ear and write.">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
/* base reset: no default body margin, keep content clear of phone notches and home bars */
:root { padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }
body { margin: 0; }
img { max-width: 100%; }
</style>
"""
html = HEAD + head_part + "\n</head>\n<body>\n" + body_part + "\n</body>\n</html>\n"
open(out, 'w', encoding='utf-8').write(html)
print('wrote', out, len(html.encode('utf-8')), 'bytes')
