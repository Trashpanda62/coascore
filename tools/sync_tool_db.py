#!/usr/bin/env python3
"""Copy peptide-db.json into tool/peptide-db.json and into the inline `let DB = [...]` block of tool/index.html.

Usage: python tools/sync_tool_db.py [repo_root]. Run after any edit to peptide-db.json, before the page generators.
"""
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
raw = (ROOT / 'peptide-db.json').read_text(encoding='utf8')
(ROOT / 'tool' / 'peptide-db.json').write_text(raw, encoding='utf8', newline='')
p = ROOT / 'tool' / 'index.html'
t = p.read_text(encoding='utf8')
i = t.index('let DB = [') + len('let DB = ')
j = t.index('\n];', i) + 2
p.write_text(t[:i] + raw.strip() + t[j:], encoding='utf8', newline='')
print('synced tool/peptide-db.json and tool/index.html')
