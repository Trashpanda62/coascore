#!/usr/bin/env python3
"""Rebuild /peptides/index.html from tools/hub.template.html + peptide-db.json.
Usage: python tools/gen_hub.py [repo_root]. The template holds all hub copy, the mass matcher script and the Oak Ridge block;
this script fills the compound table ({{ROWS}}), the matcher data ({{DATA}}) and the count ({{N}})."""
import html, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else Path(__file__).resolve().parent.parent
import gen_peptides as g   # shares DB, short_name, fmt, Oak Ridge helper

def short(x): return g.short_name(x['name'])

def build():
    db = g.DB
    rows = ''
    for x in sorted(db, key=lambda x: short(x).lower()):
        q = ' '.join([short(x)] + x['aliases'] + [x['class']]).lower()
        mass = f"{g.fmt(x['avgMW'])} Da" if x['avgMW'] else 'no single mass'
        rows += (f'<tr data-q="{g.H(q)}"><td><a href="/peptides/{x["slug"]}.html">{g.H(short(x))}</a></td>'
                 f'<td>{g.H(x["class"])}</td><td>{mass}</td></tr>')
    data = json.dumps([[x['slug'], short(x), x['aliases'], x['class'], x['avgMW']] for x in db], ensure_ascii=False, separators=(',', ':'))
    t = (g.ROOT / 'tools' / 'hub.template.html').read_text(encoding='utf8')
    return t.replace('{{ROWS}}', rows).replace('{{DATA}}', data).replace('{{N}}', str(len(db))).replace('{{OAKRIDGE}}', g.oakridge_block('hub', '', 'hub'))

if __name__ == '__main__':
    (g.ROOT / 'peptides' / 'index.html').write_text(build(), encoding='utf8', newline='')
    print('wrote hub')
