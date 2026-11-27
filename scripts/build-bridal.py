#!/usr/bin/env python3
"""Build bridal/index.html: the same invitation, sent by the bride's parents.

Generated from index.html, so after editing the main page just run:

    npm run bridal          # or: python3 scripts/build-bridal.py

Served at https://tashkeensayyad.github.io/Valima-Invite/bridal/
(<base href="../"> lets it share every asset, style and script with the main page.)
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://tashkeensayyad.github.io/Valima-Invite/"
A = '<span class="cap-a">A</span>'

REPLACEMENTS = [
    # Page setup
    ('<html lang="en">', '<html lang="en" data-variant="bridal">'),
    ('<meta charset="utf-8">', '<meta charset="utf-8">\n  <base href="../">'),
    ("<title>Tashkeen &amp; Anusha · Valima</title>", "<title>Anusha &amp; Tashkeen · Valima</title>"),
    (f'<link rel="canonical" href="{SITE}">', f'<link rel="canonical" href="{SITE}bridal/">'),
    (f'<meta property="og:url" content="{SITE}">', f'<meta property="og:url" content="{SITE}bridal/">'),
    ('content="Tashkeen &amp; Anusha">', 'content="Anusha &amp; Tashkeen">'),
    ('content="Valima — Tashkeen &amp; Anusha">', 'content="Valima — Anusha &amp; Tashkeen">', 2),
    ("assets/og-card.jpg?v=", "assets/og-card-bridal.jpg?v=", 3),
    ("reading Valima, Tashkeen Syed and Anusha Nizamani,", "reading Valima, Anusha Nizamani and Tashkeen Syed,"),
    # Door medallion
    (f'<span>T</span><i>✦</i>{A}', f'{A}<i>✦</i><span>T</span>', 2),
    # Welcome card
    ("Mr &amp; Mrs<br>Jallal Hyder Shah Bukhari Syed", "Mr &amp; Mrs<br>Barkat Ali Nizamani"),
    (f'Tashkeen <span class="amp">&amp;</span> {A}nusha', f'{A}nusha <span class="amp">&amp;</span> Tashkeen'),
    ("تاشقين ۽ انوشا", "انوشا ۽ تاشقين", 2),
    # Main invitation
    ('<p class="inviters-name">Jallal Hyder Shah Bukhari Syed</p>', '<p class="inviters-name">Barkat Ali Nizamani</p>'),
    ("پنهنجي پٽ جي وليمي", "پنهنجي ڌيءَ جي وليمي"),
    ("at the Valima of their son", "at the Valima of their daughter"),
    (f'''          <p class="name script foil">Tashkeen</p>
          <p class="amp-line"><span data-sd="۽">with</span></p>
          <p class="name script foil">{A}nusha</p>
          <p class="parent"><em>daughter of</em> Barkat Ali Nizamani</p>''',
     f'''          <p class="name script foil">{A}nusha</p>
          <p class="amp-line"><span data-sd="۽">with</span></p>
          <p class="name script foil">Tashkeen</p>
          <p class="parent"><em>son of</em> Jallal Hyder Shah Bukhari Syed</p>'''),
    # Closing and footer
    ("Tashkeen &amp; Anusha</p>", "Anusha &amp; Tashkeen</p>"),
    ("<p>Tashkeen &amp; Anusha · 29.12.2026 · Thatta</p>", "<p>Anusha &amp; Tashkeen · 29.12.2026 · Thatta</p>"),
]


def build():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    for item in REPLACEMENTS:
        old, new = item[0], item[1]
        count = item[2] if len(item) > 2 else 1
        found = html.count(old)
        if found != count:
            raise SystemExit(f"build-bridal: expected {count}x, found {found}x: {old[:70]!r}")
        html = html.replace(old, new)
    out = ROOT / "bridal" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
