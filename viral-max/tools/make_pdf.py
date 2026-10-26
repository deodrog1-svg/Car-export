#!/usr/bin/env python3
"""Turn a Viral Max task (Markdown) into a styled PDF ready for shooting day.

Usage:
  python3 viral-max/tools/make_pdf.py viral-max/tasks/001-first-10-viral-videos.md
  -> writes viral-max/tasks/001-first-10-viral-videos.pdf

Needs: pip install markdown, and Node with Playwright (Chromium).
"""
import re
import subprocess
import sys
from pathlib import Path

import markdown

CSS = """
@page { size: A4; margin: 14mm 12mm 16mm 12mm; }
* { box-sizing: border-box; }
body { font-family: 'Inter', 'Noto Sans', 'DejaVu Sans', Arial, sans-serif; color: #1a1a1a;
       font-size: 10.5pt; line-height: 1.45; }
h1 { font-size: 22pt; color: #fff; background: linear-gradient(90deg, #c8102e, #003478);
     padding: 14px 18px; border-radius: 10px; margin: 0 0 14px; }
h2 { font-size: 15pt; color: #003478; border-bottom: 3px solid #c8102e; padding-bottom: 4px;
     margin-top: 22px; break-after: avoid; }
h3 { color: #c8102e; break-after: avoid; }
table { width: 100%; border-collapse: collapse; margin: 8px 0 12px; font-size: 9.5pt;
        break-inside: auto; }
tr { break-inside: avoid; }
th { background: #003478; color: #fff; text-align: left; padding: 6px; }
td { border: 1px solid #d6dbe4; padding: 5px 6px; vertical-align: top; }
tr:nth-child(even) td { background: #f4f6fa; }
blockquote { margin: 10px 0; padding: 8px 12px; background: #fff6e0; border-left: 4px solid #f0a500;
             border-radius: 4px; }
code { background: #eef1f6; padding: 1px 4px; border-radius: 3px; font-size: 9pt; }
pre { background: #eef1f6; padding: 8px; border-radius: 6px; white-space: pre-wrap; }
hr { border: none; height: 0; margin: 0; break-after: page; }
strong { color: #000; }
"""

PRINT_JS = """
const { chromium } = require('playwright');
(async () => {
  const [html, pdf] = process.argv.slice(1);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + html, { waitUntil: 'networkidle' });
  await page.pdf({ path: pdf, format: 'A4', printBackground: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888">Viral Max · <span class="pageNumber"></span>/<span class="totalPages"></span></div>',
    margin: { top: '14mm', bottom: '16mm', left: '12mm', right: '12mm' } });
  await browser.close();
})();
"""


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1]).resolve()
    # Flag emoji don't render in Chromium PDFs; spell the country code instead (🇩🇪 -> (DE)).
    text = re.sub("([\U0001F1E6-\U0001F1FF])([\U0001F1E6-\U0001F1FF])",
                  lambda m: "(" + "".join(chr(ord(c) - 0x1F1E6 + 65) for c in m.groups()) + ")", src.read_text())
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    html = src.with_suffix(".print.html")
    html.write_text(f"<!doctype html><html lang='ru'><head><meta charset='utf-8'><style>{CSS}</style>"
                    f"</head><body>{body}</body></html>")
    pdf = src.with_suffix(".pdf")
    try:
        subprocess.run(["node", "-e", PRINT_JS, str(html), str(pdf)], check=True)
    finally:
        html.unlink(missing_ok=True)
    print(pdf)


if __name__ == "__main__":
    main()
