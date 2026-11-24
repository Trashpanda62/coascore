#!/usr/bin/env python3
"""Build 1200x630 share cards og/peptides/<slug>.png from peptide-db.json (data only, no invented text).
Usage: python tools/gen_og.py [repo_root]. Needs Pillow and Segoe UI (Windows)."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
DB = json.load(open(ROOT / 'peptide-db.json', encoding='utf8'))
FD = Path('C:/Windows/Fonts')
F = lambda f, s: ImageFont.truetype(str(FD / f), s)
BOLD, REG, SEMI = 'segoeuib.ttf', 'segoeui.ttf', 'seguisb.ttf'
INK, SOFT, ACC, BG = (15, 23, 42), (71, 85, 105), (13, 148, 136), (246, 248, 250)
out = ROOT / 'og' / 'peptides'; out.mkdir(parents=True, exist_ok=True)


def short(n):
    import re
    return re.sub(r'\s*\(.*\)\s*$', '', n)


def fit(d, text, font_file, size, maxw):
    while size > 40:
        f = F(font_file, size)
        if d.textlength(text, font=f) <= maxw:
            return f
        size -= 4
    return F(font_file, size)


for x in DB:
    im = Image.new('RGB', (1200, 630), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1200, 10], fill=ACC)
    d.text((70, 52), 'Coa', font=F(BOLD, 40), fill=INK)
    d.text((70 + d.textlength('Coa', font=F(BOLD, 40)), 52), 'Score', font=F(BOLD, 40), fill=ACC)
    d.text((70, 140), 'PEPTIDE COA REFERENCE', font=F(BOLD, 28), fill=ACC)
    name = short(x['name']) + ' COA'
    d.text((70, 190), name, font=fit(d, name, BOLD, 96, 1060), fill=INK)
    if x['avgMW']:
        l1 = f"Molecular weight {x['avgMW']:,.2f} Da"
        l2 = f"{x['molecularFormula']}  |  expected m/z peaks for mass spec"
    else:
        l1 = 'No single molecular weight'
        l2 = 'What a COA can and cannot show for this compound'
    d.text((70, 330), l1, font=fit(d, l1, SEMI, 52, 1060), fill=SOFT)
    d.text((70, 405), l2, font=fit(d, l2, REG, 36, 1060), fill=SOFT)
    d.text((70, 555), 'coascore.com  \u00b7  Independent, vendor-neutral  \u00b7  Research use only', font=F(REG, 28), fill=(100, 116, 139))
    im.save(out / f"{x['slug']}.png", optimize=True)
print(len(DB), 'cards')
