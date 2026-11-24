"""Rebuild sitemap.xml from the pages on disk. lastmod = date of the last git commit that touched the page.
Run from anywhere: python tools/gen_sitemap.py   (commit pages first, then run, then commit sitemap.xml)"""
import glob, os, re, subprocess
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
pages = [p.replace('\\', '/') for p in glob.glob('**/*.html', recursive=True)]
pages = [p for p in pages if not p.startswith('tools/') and p != '404.html']

def url(p):
    if p == 'index.html': return 'https://coascore.com/'
    if p.endswith('/index.html'): return 'https://coascore.com/' + p[:-10]
    return 'https://coascore.com/' + p

old = re.findall(r'<loc>([^<]+)', open('sitemap.xml', encoding='utf8').read())
order = {u: i for i, u in enumerate(old)}
pages.sort(key=lambda p: (order.get(url(p), 10**6), p))
rows = []
for p in pages:
    d = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', p], capture_output=True, text=True).stdout.strip()
    if not d: continue  # not committed yet
    rows.append(f'  <url><loc>{url(p)}</loc><lastmod>{d}</lastmod></url>')
open('sitemap.xml', 'w', encoding='utf8', newline='\n').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + '\n'.join(rows) + '\n</urlset>\n')
print(len(rows), 'urls')
