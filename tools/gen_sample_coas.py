#!/usr/bin/env python3
"""Build /sample-coas.html: three public sample COAs annotated against the CoaScore checklist.

Usage: python tools/gen_sample_coas.py [repo_root]
Every fact below was read from the linked PDF on 2026-11-23 (text layer and rendered page). Nothing is invented.
Mass checks use proton mass 1.007276 on the masses printed in the documents themselves.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_peptides as g

H, table = g.H, g.table
URL = 'https://coascore.com/sample-coas.html'
TITLE = 'Sample Peptide COAs Annotated: What Is Good and What Is Missing'
DESC = ('Three real, publicly posted peptide certificates of analysis (Cayman Chemical, NovoPro, Krause Analytical) read against the '
        'CoaScore checklist: what each shows, what it leaves out, and what to ask. Source links and dates included.')
P = 1.007276

CAY = 'https://cdn.caymanchem.com/cdn/downloadCofa/Cayman-CofA-44549-0817812.pdf'
NOV = 'https://novopro.cn/uploads/coa-reports/peptides/M2pep-peptide_Cat_319211_COA_HPLC_MS.pdf'
KRA = 'https://uzgnkjifuxpdegkzybmc.supabase.co/storage/v1/object/public/product-coas/VR-GLOW/VR-GLOW-2026-001.pdf'

cay_mz = (3020.30 - 3 * P) / 3
nov_mz = (1656.79 - 2 * P) / 2
assert abs(cay_mz - 1005.76) < 0.01 and abs(nov_mz - 827.39) < 0.01

S = {'p': 'Shown', 'h': 'Partly', 'm': 'Not shown'}
grid = [
    ('1. Sample and lot', 'h', 'p', 'p'),
    ('2. Identity (mass spec)', 'h', 'p', 'h'),
    ('3. Purity (HPLC)', 'm', 'p', 'h'),
    ('4. Quantity', 'm', 'm', 'p'),
    ('5. Authenticity', 'h', 'm', 'h'),
]
rows = ''.join(f'<tr><th scope="row">{a}</th>' + ''.join(f'<td><strong>{S[x]}</strong></td>' for x in (b, c, d)) + '</tr>'
               for a, b, c, d in grid)
overview = table('Three sample COAs against the CoaScore checklist',
                 ['Checklist section', 'Cayman C-Peptide', 'NovoPro M2pep', 'Krause Analytical GLOW blend'], rows)


def li(items):
    return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'


def sample(id_, title, meta, good, gaps, ask):
    return (f'<section id="{id_}"><h2>{title}</h2><p>{meta}</p>'
            f'<h3>What it shows</h3>{li(good)}<h3>What is missing or worth asking</h3>{li(gaps)}'
            f'<h3>Questions to put to the issuer</h3>{li(ask)}</section>')


s1 = sample(
    'cayman', '1. Cayman Chemical: C-Peptide, Item 44549, Batch 0817812',
    f'Issued by the manufacturer and posted on its own download server. <a href="{CAY}" rel="noopener" target="_blank">Open the PDF</a> '
    '(link checked 2026-11-23). The page footer is dated 10/12/2018 (a template date). The only date on the report is the expiry, 14 Apr 2030. '
    'One page.',
    ['Item number, batch number, full chemical name, molecular formula (C129H211N35O48), CAS number (33017-11-7) and formula weight (3020.30).',
     'A stated purity specification (at least 95%), then a result for each test: HPLC purity 100.0%, Mass Spec [M-3H]3- 1005.6, NMR conforms.',
     'A named reviewer with a signature.',
     f'Our check: from the printed formula weight, the expected [M-3H]3- is about {cay_mz:.1f}. The report says 1005.6, so the two agree to about 0.2.'],
    ['No analysis date, so you cannot tell when this batch was tested. An expiry date is not a test date.',
     'No chromatogram, no peak table and no method (column, gradient, wavelength). The 100.0% cannot be checked. Our <a href="/coa-red-flags.html">red-flags page</a> '
     'explains why an unqualified 100.0% deserves a question. That is a prompt to ask, not a claim that the number is wrong.',
     'No mass spectrum is attached, and no tolerance is stated for the mass match. The NMR line says only "Conforms".',
     'No content or quantity line: no net peptide content, water or counterion result. See <a href="/net-peptide-content.html">net peptide content vs purity</a>.',
     'The maker tested its own product. That is normal for a catalogue standard, but it is not an independent check.'],
    ['What was the HPLC method and detector, and can I see the trace?',
     'On what date was this batch analysed?',
     'Is there a peptide content value for this batch?'])

s2 = sample(
    'novopro', '2. NovoPro Bioscience: M2pep peptide, Cat. 319211, Lot MTFA33550-251110',
    f'Issued by the supplier\'s Quality Assurance department and posted in its public "COA reports" folder. <a href="{NOV}" rel="noopener" target="_blank">Open the PDF</a> '
    '(link checked 2026-11-23). Certified 20 Nov 2025; the mass spectrum shows an acquisition date of 2025/11/19. Three pages.',
    ['Lot number, sequence (YEQDPWGVKWWY), salt form (acetate) and storage on page 1, with a signature and a stamp.',
     'Identity: theoretical mass 1656.79 and observed 1656.80, plus a spectrum where the main peak is labelled [M-2H]2- at m/z 827.40. '
     f'Our check: (1656.79 - 2 x 1.00728) / 2 = {nov_mz:.2f}, so the labelled peak fits the stated mass.',
     'Purity: a full chromatogram at 214 nm and a peak table with five peaks. The main peak is 97.350% of the area. The areas add up to the printed total (4,351,497).',
     'Method: column (Kromasil C18, 4.6 x 250 mm), mobile phases, gradient, flow rate, wavelength, injection volume and dissolving solvent. This is the most complete method block of the three samples.'],
    ['Purity is area-%, so it says how much of the detector signal is the main peak. It does not say how much of the powder is peptide. See <a href="/read-hplc-and-mass-spec.html">reading HPLC and mass spec</a>.',
     'The test table lists endotoxin, TFA solubility, moisture content and acetic acid content, all as "N/A". For a product described as an acetate salt, '
     'no acetate or moisture result means the peptide content of the 5 mg was not measured on this report.',
     'The "Quantity" row reads 5 mg against 5.0 mg. The report does not say whether that is powder weight or peptide content.',
     'The mass spectrum does not name the instrument model, and no tolerance is stated for the mass match.',
     'Certified by the seller\'s own QA team. There is no independent lab and no report number to look up.'],
    ['Is the 5 mg the weight of powder or of peptide, and how was it measured?',
     'Can you give the moisture and acetate content for this lot?',
     'Which instrument produced the spectrum?'])

s3 = sample(
    'krause', '3. Krause Analytical (Finnrick Analytics report): GLOW blend, batch znqbxhy, 70 mg label claim',
    f'Issued by an independent lab, as a four-page report. This copy is posted publicly on a seller\'s file storage. <a href="{KRA}" rel="noopener" target="_blank">Open the PDF</a> '
    '(link checked 2026-11-23). Sample received 4/21/2026, analysed 5/2/2026, report issued 5/13/2026. '
    'The report says it can be verified at finnrick.com/verify; we did not run that check, so treat this copy as unverified.',
    ['Project number, lab number, batch/lot, label claim, three dates (received, analysed, issued), the lab address and a signature from the named laboratory director.',
     'Photos of the vial with its batch label, so the sample can be tied to a lot.',
     'Identity: "ID Confirmed" by HPLC-UV-MS for each of the three analytes (BPC-157, GHK-Cu, TB-500), with CAS numbers, plus one combined mass spectrum.',
     'Quantity: a result in mg per vial, a limit of quantification (0.5), and the result as a percent of label for each analyte: 7.46 mg (74.6%), 29.5 mg (58.9%), 5.82 mg (58.2%). '
     'The methods page explains that the peptide is compared against a known standard. This is the only sample here that measures amount.',
     'A methods summary naming USP/NF chapters and describing how purity (area ratio) and amount are calculated.'],
    ['One purity line (more than 99.9%) for a blend of three, and it is not tied to a single analyte. Ask for purity per component.',
     'The methods summary describes endotoxin (USP/NF 85) and metals (USP/NF 233) tests, but no endotoxin or metals result appears on the report pages. Ask whether those were run on this lot.',
     'Observed and expected masses are not printed per analyte, only "ID Confirmed". A spectrum is attached, but you cannot check it against a stated target.',
     'The label amounts per analyte are not printed on the report. The percentages imply 10 mg, 50 mg and 10 mg, which add up to the 70 mg label claim.',
     'The report is the lab\'s result for one vial, so it describes that sample, not every batch. Check the batch code against your own vial.'],
    ['Can I see purity for each component, not one combined figure?',
     'Were endotoxin and metals tested on this lot, and where are the results?',
     'Can the report be confirmed through the lab\'s own page, using the printed certificate ID?'])

faq = [
    ('Where can I find a sample peptide COA?',
     'This page links three that are public: a catalogue C-peptide COA from Cayman Chemical, a catalogue peptide COA with chromatogram and mass spectrum from NovoPro, and an independent-lab report from Krause Analytical. '
     'Each is annotated against the CoaScore checklist. Documents of this kind are samples of format, not endorsements of any product.'),
    ('Which of the three samples is the most complete?',
     'None is complete. NovoPro shows the most identity and purity detail but no content measurement. Krause Analytical measures amount per vial and is independent, '
     'but gives one purity line for a three-peptide blend and no endotoxin or metals results. Cayman gives short results with no trace or method.'),
    ('Does a sample COA prove the product I bought is genuine?',
     'No. A COA describes the sample that was tested. To tie it to your vial, match the lot, read the dates, and confirm the report number with the lab itself. See how to verify a COA.'),
]
art = {"@context": "https://schema.org", "@type": "Article", "datePublished": g.DATE, "dateModified": g.DATE, "headline": TITLE,
       "description": DESC, "author": {"@type": "Organization", "name": "CoaScore"},
       "publisher": {"@type": "Organization", "name": "CoaScore", "logo": {"@type": "ImageObject", "url": "https://coascore.com/og.png"}},
       "mainEntityOfPage": URL}
fq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://coascore.com/"},
    {"@type": "ListItem", "position": 2, "name": "Sample COAs", "item": URL}]}


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
        '<span aria-current="page">Sample COAs</span></nav><p class="eyebrow">Real documents, read against our checklist</p>'
        '<h1>Sample peptide COAs, annotated</h1>'
        '<p class="lede">Reading about a COA is easier with one in front of you. Below are three public ones. Each is read against the five sections of the '
        '<a href="/coa-checklist.html">CoaScore checklist</a>: what it shows, what it leaves out, and what to ask.</p>'
        '<div class="notice"><p><strong>Research use only.</strong> These notes describe documents, not product quality. We did not test any product. '
        'We could not confirm any of these documents with its issuer, and a PDF alone never proves a batch. Nothing here is dosing, medical or purchasing advice. '
        'Everything we state comes from the document itself or from arithmetic on its printed numbers (shown where used). Sources were read on 2026-11-23, and posted files can move.</p></div>'
        '<h2 id="grid">At a glance</h2>' + overview +
        '<p><strong>Shown</strong> means the document gives the item. <strong>Partly</strong> means some of it. <strong>Not shown</strong> means the page does not give it. '
        'A "Not shown" is a question for the issuer, not proof of a problem.</p>'
        + s1 + s2 + s3 +
        '<h2 id="use">How to use these on your own COA</h2><ol>'
        '<li>Print the <a href="/coa-checklist.html">checklist</a> and mark your report the way the table above does.</li>'
        '<li>Enter what the report says into the <a href="/tool/">COA Interpreter</a> to see the missing items in plain words.</li>'
        '<li>Compare the printed mass with the expected one in the <a href="/peptides/">peptide reference</a>, or use the mass matcher.</li>'
        '<li>Ask the issuer the questions above, and confirm the report number with the lab. See <a href="/verify-a-coa.html">how to verify a COA</a>.</li></ol>'
        '<h2 id="faq">Common questions</h2>'
        + ''.join(f'<h3>{H(q)}</h3><p>{H(a)}</p>' for q, a in faq)
        + '<h2 id="refs">Sources (read 2026-11-23)</h2><ul>'
        f'<li><a href="{CAY}" rel="noopener" target="_blank">Cayman Chemical certificate of analysis, C-Peptide, Item 44549, Batch 0817812</a>.</li>'
        f'<li><a href="{NOV}" rel="noopener" target="_blank">NovoPro Bioscience certificate of analysis, M2pep peptide, Cat. 319211, Lot MTFA33550-251110</a>.</li>'
        f'<li><a href="{KRA}" rel="noopener" target="_blank">Krause Analytical / Finnrick Analytics certificate of analysis, batch znqbxhy</a> (seller-hosted copy).</li>'
        '<li>Expected-mass arithmetic: [M-nH]n- = (M - n x 1.007276) / n, using the mass printed on each report.</li></ul>'
        + g.RELATED.replace('<li><a href="/sample-coas.html">Sample peptide COAs, annotated</a></li>', '') + g.AD + '</article></main>')

if __name__ == '__main__':
    (g.ROOT / 'sample-coas.html').write_text(head + body + g.FOOT, encoding='utf8', newline='')
    print('wrote sample-coas.html')
