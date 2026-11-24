#!/usr/bin/env python3
"""Build /no-single-molecular-weight.html: why HCG, thymalin, IGF-1 LR3 and follistatin-344 have no single mass.

Usage: python tools/gen_biologics.py [repo_root]
Facts come from peptide-db.json notes plus the sources listed on the page (checked 2026-11-23). No dosing.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_peptides as g

H, table = g.H, g.table
URL = 'https://coascore.com/no-single-molecular-weight.html'
TITLE = 'Why Some Peptides Have No Single Molecular Weight (HCG, IGF-1 LR3, Follistatin, Thymalin)'
DESC = ('HCG, thymalin, IGF-1 LR3 and follistatin-344 are proteins, glycoproteins or mixtures, so a COA cannot give one exact '
        'molecular weight. What to expect on the report instead, and what to ask.')
DB = {x['slug']: x for x in g.DB}
for s in ('hcg', 'thymalin', 'igf-1-lr3', 'follistatin-344'):
    assert s in DB and DB[s]['avgMW'] is None


def cl(s):
    return f'<a href="/peptides/{s}.html">{H(g.short_name(DB[s]["name"]))}</a>'


rows = (
    f'<tr><td>{cl("hcg")}</td><td>Two-chain glycoprotein hormone (alpha subunit 92 amino acids, beta subunit 145)</td>'
    '<td>Sugar chains vary from molecule to molecule. Wikipedia gives about 36.7 kDa, and lists regular, hyperglycosylated and free-beta forms.</td>'
    '<td>Potency in international units (IU) against a reference, or an immunoassay. A small-peptide HPLC purity alone is not enough.</td></tr>'
    f'<tr><td>{cl("follistatin-344")}</td><td>344-residue recombinant glycoprotein</td>'
    '<td>Glycosylation adds mass on top of the protein core, so measured size is higher and spread out. Our reference data lists a core of about 37.8 kDa. A shorter isoform (FST-315) is also sold.</td>'
    '<td>SDS-PAGE purity, plus immunoassay or activity data. Ask which isoform was tested.</td></tr>'
    f'<tr><td>{cl("igf-1-lr3")}</td><td>83-residue recombinant protein: 13 extra N-terminal residues, and arginine in place of glutamic acid at position 3</td>'
    '<td>This one is a single defined protein, so a mass exists (Wikipedia: 9117.60). Vendors quote about 9111, 9117.8 and 9200, so CoaScore lists no single value.</td>'
    '<td>Intact-protein mass spectrum and SDS-PAGE or RP-HPLC purity. Compare the found mass with about 9.1 kDa and ask how it was calculated.</td></tr>'
    f'<tr><td>{cl("thymalin")}</td><td>Mixture of peptides extracted from calf thymus</td>'
    '<td>A mixture has no one molecule to weigh. Some vendors sell a synthetic dipeptide (Glu-Trp) under a similar name, which is a different substance.</td>'
    '<td>No single-component HPLC spec applies. Ask what the product is, how it was made, and how the lab characterised it.</td></tr>')

faq = [
    ('Why does my HCG COA not list a molecular weight?',
     'HCG is a glycoprotein made of two chains carrying sugar chains of varying size. The product is a population of slightly different molecules, '
     'so identity is normally shown by potency in IU or by an immunoassay, not by one mass. If a report prints one exact molecular weight for it, '
     'ask where the number came from.'),
    ('Is a mass-spec result useful for a protein like IGF-1 LR3?',
     'Yes, if the report shows the spectrum and says how the mass was derived. Large proteins carry many charges, so labs usually convert the peaks '
     'to one mass. Compare that mass with about 9.1 kDa and ask for the spectrum, not only a number.'),
    ('Does 99% HPLC purity prove a protein is what the label says?',
     'No. Purity says how much of the detected signal is one peak. It does not say that the peak is the named protein, how active it is, or how much '
     'is in the vial. Ask for an identity test and a quantity method as well.'),
    ('Why do two vendors quote different molecular weights for the same product?',
     'They may be quoting different things: a calculated mass from the sequence, a measured mass of one form, an average over glycoforms, or a '
     'different isoform. A quoted mass without its source and method is weak evidence.'),
]
fq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
art = {"@context": "https://schema.org", "@type": "Article", "datePublished": g.DATE, "dateModified": g.DATE, "headline": TITLE,
       "description": DESC, "author": {"@type": "Organization", "name": "CoaScore"},
       "publisher": {"@type": "Organization", "name": "CoaScore", "logo": {"@type": "ImageObject", "url": "https://coascore.com/og.png"}},
       "mainEntityOfPage": URL}
bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://coascore.com/"},
    {"@type": "ListItem", "position": 2, "name": "No single molecular weight", "item": URL}]}


def J(o):
    return json.dumps(o, ensure_ascii=False, separators=(',', ':'))


head = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        '<link rel="stylesheet" href="/brand.css"><link rel="icon" href="/favicon.svg" type="image/svg+xml">'
        f'<title>{H(TITLE)}</title><meta name="description" content="{H(DESC)}"><link rel="canonical" href="{URL}">'
        '<meta property="og:type" content="article"><meta property="og:site_name" content="CoaScore">'
        f'<meta property="og:title" content="{H(TITLE)}"><meta property="og:description" content="{H(DESC)}"><meta property="og:url" content="{URL}">'
        '<meta property="og:image" content="https://coascore.com/og.png"><meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:title" content="{H(TITLE)}"><meta name="twitter:description" content="{H(DESC)}">'
        '<meta name="twitter:image" content="https://coascore.com/og.png">'
        f'<script type="application/ld+json">{J(art)}</script><script type="application/ld+json">{J(bc)}</script>'
        f'<script type="application/ld+json">{J(fq)}</script>{g.CLARITY}</head><body><a class="skip-link" href="#main">Skip to content</a>'
        '<header class="site-header"><div class="nav-wrap"><a class="brand-wordmark" href="/"><span class="brand-mark">Coa</span>Score</a>'
        f'<nav class="site-nav" aria-label="Primary">{g.NAV}</nav></div></header>')

body = ('<main id="main"><article class="prose"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true"> / </span>'
        '<span aria-current="page">No single molecular weight</span></nav><p class="eyebrow">Proteins, glycoproteins and mixtures</p>'
        '<h1>Why some peptides have no single molecular weight</h1>'
        '<p class="lede">A small peptide is one exact molecule, so a COA can state its mass. Some products sold as &ldquo;peptides&rdquo; are not that. '
        'They are large proteins, sugar-coated proteins, or mixtures. This guide covers four of them and says what a COA should show instead.</p>'
        '<div class="notice"><p><strong>Research use only.</strong> This explains analytical documentation. It is not dosing, medical or purchasing advice.</p></div>'
        '<div class="notice" id="short-answer"><p><strong>Short answer.</strong> HCG and follistatin carry sugar chains that vary, thymalin is a mixture, '
        'and IGF-1 LR3 is a protein whose quoted mass differs by source. For these, identity comes from potency, immunoassay, SDS-PAGE or an intact-protein '
        'mass spectrum, not from one tidy molecular weight. Treat a single exact mass printed to two decimals with caution.</p></div>'
        '<h2 id="four">The four compounds</h2>'
        + table('Compounds with no single molecular weight', ['Compound', 'What it is', 'Why no single mass', 'What identity evidence to expect'], rows)
        + '<p>Compound pages carry the same notes and a COA checklist. Facts above come from the sources at the end of this page.</p>'
        '<h2 id="why">Why sugar chains and mixtures break the single-mass rule</h2>'
        '<p>A mass spectrometer weighs individual molecules. A small synthetic peptide gives one clean mass because every molecule is identical. '
        'A glycoprotein is made by cells, and each molecule can carry a slightly different set of sugar chains. The sample is a family of masses, '
        'so the instrument shows a spread, and gel results (SDS-PAGE) show a band or smear at an apparent size that need not equal the calculated one. '
        'A mixture such as thymalin is worse: there is no single target to weigh at all.</p>'
        '<h2 id="show">What a COA should show instead</h2><ol class="checklist">'
        '<li><strong>Identity.</strong> The method named and the data attached: an immunoassay or activity result for HCG and follistatin, an intact-protein spectrum for IGF-1 LR3. A statement of &ldquo;identity confirmed&rdquo; alone is not data.</li>'
        '<li><strong>Purity by a fitting method.</strong> SDS-PAGE or RP-HPLC for proteins, with the image or trace. A small-peptide HPLC percentage does not describe a glycoprotein.</li>'
        '<li><strong>Potency or quantity.</strong> HCG is measured in international units against a reference, so the report should state the unit and the reference used. For any protein, ask how the amount was measured.</li>'
        '<li><strong>Safety tests where relevant.</strong> Endotoxin and sterility matter more for recombinant products. See <a href="/coa-tests-explained.html">which tests belong on a COA</a>.</li>'
        '<li><strong>Traceability.</strong> Lot, sample ID, lab, dates, report number, as for any COA. See <a href="/verify-a-coa.html">how to verify a COA</a>.</li></ol>'
        '<h2 id="flags">Red flags specific to these products</h2><ul>'
        '<li>One exact molecular weight, to two decimals, for HCG, follistatin or thymalin.</li>'
        '<li>A bare &ldquo;99% HPLC&rdquo; with no identity or potency data for a glycoprotein.</li>'
        '<li>A mass that matches a different compound, such as a dipeptide named in place of a thymus extract. Check the name against the reference.</li>'
        '<li>No isoform stated for follistatin (344 versus 315 residues).</li>'
        '<li>A quoted mass with no method, or a vendor and a lab that quote different values for the same lot.</li></ul>'
        '<h2 id="ask">Questions to put to the lab or seller</h2><ol>'
        '<li>What exactly was tested, and against what reference?</li>'
        '<li>How was identity shown, and can I see the raw data?</li>'
        '<li>Which form or isoform does this report cover?</li>'
        '<li>How was the amount measured, and in what unit?</li>'
        '<li>Which lot and report number can I confirm with the lab directly?</li></ol>'
        '<p>Enter what the report says into the <a href="/tool/">COA Interpreter</a> to see what is missing, or print the <a href="/coa-checklist.html">one-page checklist</a>.</p>'
        '<h2 id="faq">Common questions</h2>'
        + ''.join(f'<h3>{H(q)}</h3><p>{H(a)}</p>' for q, a in faq)
        + '<h2 id="refs">Sources (checked 2026-11-23)</h2><ul>'
        '<li><a href="https://en.wikipedia.org/wiki/Human_chorionic_gonadotropin" rel="noopener" target="_blank">Wikipedia: Human chorionic gonadotropin</a> (subunits, glycosylation, forms, IU).</li>'
        '<li><a href="https://en.wikipedia.org/wiki/IGF-1_LR3" rel="noopener" target="_blank">Wikipedia: IGF-1 LR3</a> (83 residues, Arg3 substitution, molar mass 9117.60). The article is not primary literature.</li>'
        '<li><a href="https://en.wikipedia.org/wiki/Follistatin" rel="noopener" target="_blank">Wikipedia: Follistatin</a> (isoforms FS-288, FS-300 and FS-315 reported). The core figure of about 37.8 kDa in CoaScore&rsquo;s reference data came from an R&amp;D Systems product listing that we could not reopen on 2026-11-23, so treat it as approximate.</li>'
        '<li>Thymalin and vendor-quoted IGF-1 LR3 masses: CoaScore reference data (<a href="/peptides/thymalin.html">thymalin</a>, <a href="/peptides/igf-1-lr3.html">IGF-1 LR3</a>). Public thymalin sources are mostly vendor pages, so we state no mass.</li></ul>'
        + g.RELATED.replace('<li><a href="/no-single-molecular-weight.html">Why some peptides have no single molecular weight</a></li>', '') + g.AD + '</article></main>')

if __name__ == '__main__':
    (g.ROOT / 'no-single-molecular-weight.html').write_text(head + body + g.FOOT, encoding='utf8', newline='')
    print('wrote no-single-molecular-weight.html')
