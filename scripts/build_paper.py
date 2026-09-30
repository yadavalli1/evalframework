"""Render paper/paper.md to paper/paper.html and paper/paper.pdf (headless Chromium)."""
import markdown, re
from pathlib import Path
from playwright.sync_api import sync_playwright

CHROME = str(next(Path("/opt/pw-browsers").glob("chromium-*/chrome-linux*/chrome")))
ROOT = Path(__file__).resolve().parent.parent / "paper"
body = markdown.markdown((ROOT / "paper.md").read_text(), extensions=["tables", "fenced_code", "md_in_html"])
body = body.replace("[ ]", "☐")
body = re.sub(r"<p><img alt=\"(Figure \d)\" src=\"([^\"]+)\" /></p>", r'<figure><img alt="\1" src="\2"/></figure>', body)
CSS = """
@page { size: Letter; margin: 0.8in 0.85in; }
body { font-family: 'DejaVu Serif', Georgia, serif; font-size: 10.5pt; line-height: 1.5; color: #1a1a1a; max-width: 7in; margin: auto; }
h1 { font-family: 'DejaVu Sans', sans-serif; font-size: 20pt; line-height: 1.25; text-align: center; margin: 0 0 6px; }
.byline { text-align: center; color: #52514e; margin-bottom: 18px; }
h2 { font-family: 'DejaVu Sans', sans-serif; font-size: 13pt; margin: 22px 0 6px; border-bottom: 1px solid #ddd; padding-bottom: 3px; }
h3 { font-family: 'DejaVu Sans', sans-serif; font-size: 11pt; margin: 14px 0 4px; }
.abstract { background: #f4f3ef; border-left: 3px solid #2a78d6; padding: 4px 16px; margin: 0 0 12px; font-size: 10pt; }
table { border-collapse: collapse; width: 100%; font-size: 9.2pt; margin: 8px 0; }
th, td { border-bottom: 1px solid #ddd; padding: 4px 6px; text-align: left; vertical-align: top; }
th { border-bottom: 1.5px solid #888; }
figure { margin: 12px 0 2px; text-align: center; break-inside: avoid; }
figure img { max-width: 100%; }
figure svg { width: 100%; height: auto; }
figcaption, .caption { font-size: 9pt; color: #52514e; margin: 4px 0 12px; }
pre { background: #f4f3ef; padding: 8px 10px; font-size: 8.2pt; line-height: 1.35; white-space: pre-wrap; break-inside: avoid; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 0.88em; }
h2 + p, h3 + p { margin-top: 4px; }
"""
html = f'<!doctype html><html><head><meta charset="utf-8"><title>Building an LLM Evaluation Framework</title><style>{CSS}</style></head><body>{body}</body></html>'
(ROOT / "paper.html").write_text(html)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(); pg.goto((ROOT / "paper.html").as_uri()); pg.wait_for_load_state("networkidle")
    pg.pdf(path=str(ROOT / "paper.pdf"), format="Letter", print_background=True,
           display_header_footer=True, header_template="<span></span>",
           footer_template='<div style="font-size:8pt;width:100%;text-align:center;color:#888"><span class="pageNumber"></span></div>',
           margin={"top": "0.7in", "bottom": "0.8in", "left": "0.8in", "right": "0.8in"})
    b.close()
print("wrote", ROOT / "paper.pdf")
