#!/usr/bin/env python3
"""Rebuild /peptides/<slug>.html (50 compound pages) from peptide-db.json.

Usage: python tools/gen_peptides.py [repo_root]   (default: parent of tools/)
Pass 5 verified that, without the Oak Ridge block, this output matches the live pages byte for byte.
The hub page /peptides/index.html is built by tools/gen_hub.py.
Edit templates here, never the generated pages.
"""
import html, json, re, sys
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
DB = json.load(open(ROOT / 'peptide-db.json', encoding='utf8'))
H = lambda s: html.escape(str(s), quote=True)
PROTON = 1.007276  # proton mass; pages state it rounded as 1.00728
DATE = '2026-11-23'
# charge-state count by average mass (fit to the published pages)
CHARGE_STEPS = [1050, 1700, 2400, 3200, 3900, 4600]

# ---- Oak Ridge Peptides disclosed link (Steve decision 2026-11-23) ----
OR_BASE = 'https://oakridgepeptides.com'
_prod = ROOT / 'tools' / 'oakridge-products.json'
# slug -> product path on oakridgepeptides.com, only where a matching product page exists
OR_PRODUCTS = json.load(open(_prod, encoding='utf8')) if _prod.exists() else {}
INCLUDE_OR = '--no-oakridge' not in sys.argv


def oakridge_url(slug, medium):
    path = OR_PRODUCTS.get(slug, '/')
    sep = '&' if '?' in path else '?'
    return f'{OR_BASE}{path}{sep}utm_source=coascore&utm_medium={medium}&utm_campaign={slug}'


def oakridge_block(slug, short, medium='compound-page'):
    if not INCLUDE_OR:
        return ''
    prod = slug in OR_PRODUCTS
    label = f'View the {short} listing at Oak Ridge Peptides' if prod else 'Shop research peptides at Oak Ridge Peptides'
    return ('<aside class="partner-note" aria-label="Disclosure"><p><strong>Disclosure:</strong> CoaScore is built by the team '
            'behind Oak Ridge Peptides, which sells research peptides. '
            f'<a href="{H(oakridge_url(slug, medium))}" rel="sponsored noopener" target="_blank">{H(label)}</a>. '
            'Our COA scores are not influenced by this link.</p></aside>')


def tidy(n):
    """Editorial clean-up of DB notes for display (matches the published pages)."""
    n = re.sub(r'^MW intentionally null\.\s*', '', n)
    n = n.replace('MW intentionally null due to SOURCE CONFLICT:', 'Reason: Sources disagree:')
    n = n.replace('CAUTION/overlap:', 'Caution:').replace('CAUTION:', 'Caution:')
    n = n.replace('SOURCE CONFLICT:', 'Sources disagree:').replace('NOT a peptide', 'Not a peptide')
    return re.sub(r' Real MW given for identity check[^.]*\.', '', n)


def short_name(n):
    return re.sub(r'\s*\(.*\)\s*$', '', n)


def fmt(x, nd=2):
    return f'{x:,.{nd}f}'


def mz(mass, n, nd):
    # decimal arithmetic on the DB values, so 4-decimal rounding matches the published pages
    v = (Decimal(str(mass)) + n * Decimal(str(PROTON))) / n
    return f'{v.quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_EVEN):,}'


def charges(mass):
    return 1 + sum(mass >= t for t in CHARGE_STEPS)


def ions(x):
    avg, mono = x['avgMW'], x['monoisotopicMW']
    rows = []
    for n in range(1, charges(avg) + 1):
        ion = '[M+H]<sup>+</sup>' if n == 1 else f'[M+{n}H]<sup>{n}+</sup>'
        cell = f'<td>{mz(mono, n, 4)}</td>' if mono else ''
        rows.append(f'<tr><td>{ion}</td><td>{mz(avg, n, 2)}</td>{cell}</tr>')
    return ''.join(rows)


def table(label, head, rows):
    th = ''.join(f'<th scope="col">{h}</th>' for h in head)
    return (f'<div class="table-wrap" role="region" aria-label="{H(label)}" tabindex="0"><table class="data-table">'
            f'<thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div>')


def neighbours(x):
    pool = [y for y in DB if y['slug'] != x['slug'] and y['avgMW']]
    pool.sort(key=lambda y: (0, 0) if y['class'] == x['class'] else (1, abs(y['avgMW'] - x['avgMW'])))
    return pool[:6]


NAV = ('<a href="/">Home</a><a href="/how-to-read-a-coa.html">How to read a COA</a><a href="/verify-a-coa.html">Verify a COA</a>'
       '<a href="/known-labs.html">Known labs</a><a href="/coa-red-flags.html">Red flags</a><a href="/peptides/">Peptide reference</a>'
       '<a href="/about.html">About</a><a class="tool-button" href="/tool/">Open the tools</a>')
CLARITY = ('<script type="text/javascript">(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};'
           't=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];'
           'y.parentNode.insertBefore(t,y);})(window, document, "clarity", "script", "xos7mepm3i");</script>')
FOOT = ('<footer class="site-footer"><div class="footer-wrap"><span class="brand-wordmark"><span class="brand-mark">Coa</span>Score</span>'
        "<p>CoaScore turns any vendor's Certificate of Analysis into a plain-English read and a vendor-neutral documentation score; "
        'every COA is scored using the same process. CoaScore is built by the team behind Oak Ridge Peptides, but is not paid to score '
        'any result a particular way. For research use only — not medical advice.</p><div class="footer-links">'
        '<a href="/peptides/">Peptide reference</a><a href="/faq.html">COA FAQ</a><a href="/about.html">About</a>'
        '<a href="/legal.html">Terms, privacy &amp; disclaimer</a></div></div></footer>'
        '<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=\'{"token":"b446603e67084e5a90b2b1a4581815b7"}\'></script></body></html>')
RELATED = ('<aside class="related prose" aria-labelledby="rel"><h2 id="rel">Related guides</h2><ul>'
           '<li><a href="/peptides/">All compounds in the peptide reference</a></li>'
           '<li><a href="/coa-tests-explained.html">Peptide COA tests explained</a></li>'
           '<li><a href="/how-to-read-a-coa.html">How to read a peptide COA</a></li>'
           '<li><a href="/read-hplc-and-mass-spec.html">Read an HPLC chromatogram and mass spectrum</a></li>'
           '<li><a href="/verify-a-coa.html">How to verify a COA</a></li>'
           '<li><a href="/net-peptide-content.html">Net peptide content vs purity</a></li>'
           '<li><a href="/coa-red-flags.html">COA red flags</a></li><li><a href="/faq.html">COA FAQ</a></li>'
           '<li><a href="/tool/">COA Interpreter</a></li><li><a href="/calc/">Reconstitution calculator</a></li></ul></aside>')
AD = '<aside class="ad-slot" data-slot="in-article" aria-label="Advertisement" hidden></aside>'


def page(x):
    slug, name = x['slug'], x['name']
    sn = short_name(name)
    has_mass = x['avgMW'] is not None
    word = 'peptide' if x['isPeptide'] else 'compound'
    url = f'https://coascore.com/peptides/{slug}.html'
    aliases = ', '.join(x['aliases'])
    title = f'{sn} COA: Molecular Weight, Expected m/z, Checks | CoaScore'
    if len(title) > 66:
        title = title[:-len(' | CoaScore')]
    if has_mass:
        desc = (f"What a {sn} certificate of analysis should show: reference molecular weight {fmt(x['avgMW'])} Da, "
                f"formula {x['molecularFormula']}, expected mass-spec peaks and compound-specific cautions.")
    else:
        desc = (f"Why {sn} has no single molecular weight, how its identity is normally shown on a certificate of analysis, "
                "and what to check on the report.")
    ld = {"@context": "https://schema.org", "@type": "Article", "datePublished": DATE, "dateModified": DATE,
          "headline": title, "description": desc, "author": {"@type": "Organization", "name": "CoaScore"},
          "publisher": {"@type": "Organization", "name": "CoaScore", "logo": {"@type": "ImageObject", "url": "https://coascore.com/og.png"}},
          "mainEntityOfPage": url}
    OG = f'https://coascore.com/og/peptides/{slug}.png'
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://coascore.com/"},
        {"@type": "ListItem", "position": 2, "name": "Peptide reference", "item": "https://coascore.com/peptides/"},
        {"@type": "ListItem", "position": 3, "name": sn, "item": url}]}
    head = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<link rel="stylesheet" href="/brand.css"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><title>{H(title)}</title>'
            f'<meta name="description" content="{H(desc)}"><link rel="canonical" href="{url}"><meta property="og:type" content="article">'
            f'<meta property="og:site_name" content="CoaScore"><meta property="og:title" content="{H(title)}">'
            f'<meta property="og:description" content="{H(desc)}"><meta property="og:url" content="{url}">'
            f'<meta property="og:image" content="{OG}"><meta property="og:image:width" content="1200">'
            f'<meta property="og:image:height" content="630"><meta property="og:image:alt" content="{H(sn)} COA reference card: molecular weight and what to check">'
            f'<meta name="twitter:card" content="summary_large_image">'
            f'<meta name="twitter:title" content="{H(title)}"><meta name="twitter:description" content="{H(desc)}">'
            f'<meta name="twitter:image" content="{OG}">'
            f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
            f'<script type="application/ld+json">{json.dumps(bc, ensure_ascii=False, separators=(",", ":"))}</script>'
            f'{CLARITY}</head><body><a class="skip-link" href="#main">Skip to content</a><header class="site-header"><div class="nav-wrap">'
            f'<a class="brand-wordmark" href="/"><span class="brand-mark">Coa</span>Score</a><nav class="site-nav" aria-label="Primary">{NAV}</nav></div></header>')
    crumbs = ('<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true"> / </span>'
              f'<a href="/peptides/">Peptide reference</a><span aria-hidden="true"> / </span><span aria-current="page">{H(sn)}</span></nav>')
    body = (f'<main id="main"><article class="prose">{crumbs}<p class="eyebrow">Peptide COA reference</p>'
            f'<h1>{H(sn)} COA: molecular weight and what to check</h1>'
            f"<p class=\"lede\">{H(sn)} is listed in CoaScore's reference data as a {H(x['class'])}; other names include {H(aliases)}. "
            'This page collects the reference numbers a certificate of analysis for it should be compared against, and the cautions that go with them.</p>'
            '<div class="notice"><p><strong>Research use only.</strong> This is documentation reference, not dosing, medical or purchasing advice.</p></div>')
    src = x['sourceUrl']
    host = re.sub(r'^https?://(www\.)?', '', src).split('/')[0]
    rows = f'<tr><td>Name</td><td>{H(name)}</td></tr><tr><td>Also called</td><td>{H(aliases)}</td></tr><tr><td>Class</td><td>{H(x["class"])}</td></tr>'
    if has_mass:
        rows += (f'<tr><td>Molecular formula</td><td>{H(x["molecularFormula"])}</td></tr>'
                 f'<tr><td>Average molecular weight</td><td>{fmt(x["avgMW"])} Da</td></tr>')
        if x['monoisotopicMW']:
            rows += f'<tr><td>Monoisotopic mass</td><td>{fmt(x["monoisotopicMW"], 4)} Da</td></tr>'
    if x['sequence']:
        rows += f'<tr><td>Sequence</td><td>{H(x["sequence"])}</td></tr>'
    rows += f'<tr><td>Reference source</td><td><a href="{H(src)}" rel="noopener" target="_blank">{H(host)}</a></td></tr>'
    body += '<h2>Reference identity</h2>' + table(f'{sn} reference identity', ['Item', 'Value'], rows)
    notes = tidy(x['notes'])
    if has_mass:
        body += ('<h2>Expected mass-spectrum peaks</h2><p>A mass spectrometer reports m/z, not mass. The table applies '
                 '(M + n &times; 1.00728) &divide; n to the reference mass above for each protonated charge state n. '
                 f"Peaks near these values support a mass of about {fmt(x['avgMW'])} Da. Real spectra show some of these charge states, "
                 'not all of them, and low charge states of larger molecules are often weak or absent. Sodium and potassium adducts and salt '
                 'forms shift peaks, so a small offset is not automatically a mismatch; a large one is worth a question to the lab.</p>'
                 + table(f'{sn} expected m/z values', ['Ion', 'm/z from average mass'] + (['m/z from monoisotopic mass'] if x['monoisotopicMW'] else []), ions(x))
                 + '<p>The method is explained on the <a href="/read-hplc-and-mass-spec.html">chromatogram and mass spectrum guide</a>, with a worked example.</p>')
    else:
        body += ("<h2>Why there is no single molecular weight</h2><p>CoaScore's reference data deliberately lists no single mass for this one. "
                 f'{H(notes)} A COA that states one exact molecular weight for it deserves a question about where the number came from.</p>')
    cav = ''
    if has_mass:
        cav += f'<li><strong>Compound note.</strong> {H(tidy(x["notes"]))}</li>'
    cav += f'<li><strong>Salt and counter-ion.</strong> {H(x["saltNote"])}'
    if has_mass:
        cav += (f" A vial's powder weight includes counter-ions and water, so the labeled amount is not necessarily the amount of {word}; "
                'see <a href="/net-peptide-content.html">net peptide content</a>.')
    cav += '</li>'
    if has_mass and x['modified']:
        cav += ('<li><strong>Modified structure.</strong> Reference data marks this as modified, so a mass worked out from the plain '
                'amino-acid sequence will not match; compare against the published mass above.</li>')
    body += f'<h2>Cautions specific to this compound</h2><ul>{cav}</ul>'
    if has_mass:
        ident = (f"<li><strong>Identity.</strong> The report shows a mass-spectrum result and states an expected mass for {H(sn)}. "
                 f"Compare it with {fmt(x['avgMW'])} Da (average) and the m/z table above.</li>")
        pur = (f"CoaScore's reference data lists a common purity claim of &ldquo;{H(x['typicalHplcSpec'])}&rdquo;. "
               'A claim like that is relative composition, not vial quantity.')
    else:
        ident = '<li><strong>Identity.</strong> The report names the method it used for identity and says what it was compared against.</li>'
        pur = f"CoaScore's reference data notes: {H(x['typicalHplcSpec'])}."
    body += (f'<h2>What a COA for {H(sn)} should show</h2><ol class="checklist">{ident}'
             f'<li><strong>Purity.</strong> The report shows the HPLC trace, the method conditions and a peak table, not only a percentage. {pur}</li>'
             '<li><strong>Quantity.</strong> If the vial states an amount, the report says how it was measured. Purity and quantity are different numbers.</li>'
             '<li><strong>Traceability.</strong> Lot number, sample ID, issuing lab, dates and report number match the vial and appear on every page of the PDF.</li></ol>'
             '<p>Want a line-by-line review of a real report? <a href="/tool/">Open the COA Interpreter</a>. '
             'Checking your own lab arithmetic? <a href="/calc/">Use the reconstitution calculator</a>.</p>')
    if has_mass:
        nr = ''
        for y in neighbours(x):
            d = y['avgMW'] - x['avgMW']
            nr += (f'<tr><td><a href="/peptides/{y["slug"]}.html">{H(short_name(y["name"]))}</a></td><td>{H(y["class"])}</td>'
                   f'<td>{fmt(y["avgMW"])} Da</td><td>{"-" if d < 0 else "+"}{fmt(abs(d))} Da</td></tr>')
        body += ("<h2>Other compounds to compare against</h2><p>Same class first, then the nearest masses. If a COA's mass fits more than one row, "
                 'identity needs another line of evidence.</p>'
                 + table(f'Compounds with similar mass to {sn}', ['Compound', 'Class', 'Average mass', f'Difference from {H(sn)}'], nr))
    body += RELATED + oakridge_block(slug, sn) + AD + '</article></main>'
    return head + body + FOOT


if __name__ == '__main__':
    out = ROOT / 'peptides'
    for x in DB:
        (out / f"{x['slug']}.html").write_text(page(x), encoding='utf8', newline='')
    print(f'wrote {len(DB)} compound pages')
