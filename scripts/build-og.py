#!/usr/bin/env python3
"""Build the WhatsApp / social link-preview card: assets/og-card.jpg (1200x630).

Drawn with Pillow from the site's own palette and fonts (the woff2 files in
assets/fonts, converted to TTF in memory with fontTools).

    npm run og        # or: python3 scripts/build-og.py

Needs: pip install pillow fonttools brotli
After redrawing, bump ?v= on og:image and twitter:image in index.html.
`--bridal` draws assets/og-card-bridal.jpg (Anusha & Tashkeen) for the /bridal/ page.
"""
import io
import sys
import math
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
OUT = ROOT / "assets" / "og-card.jpg"
BRIDAL = "--bridal" in sys.argv
if BRIDAL:
    OUT = ROOT / "assets" / "og-card-bridal.jpg"

W, H = 1200, 630
SCALE = 2  # draw at 2x, then downsample for smooth edges

# ---- Palette (from styles.css :root) ---------------------------------------
CREAM = (251, 244, 226)      # --cream
IVORY = (255, 253, 246)
LINE = (232, 215, 173)       # --line
GOLD = (196, 154, 60)        # --gold
GOLD_DEEP = (143, 106, 34)   # --gold-deep
GOLD_SOFT = (226, 194, 113)  # --gold-soft
INK = (59, 46, 28)           # --ink
MUTED = (122, 106, 80)       # --muted
# --foil gradient stops
FOIL = [(0.00, (125, 90, 23)), (0.20, (168, 125, 40)), (0.34, (201, 155, 62)),
        (0.44, (224, 191, 108)), (0.54, (196, 154, 60)), (0.70, (148, 105, 31)),
        (0.86, (184, 138, 51)), (1.00, (125, 90, 23))]

# ---- Content (exactly as on the site) --------------------------------------
KICKER = "VALIMA"
NAME_1, SURNAME_1 = "Tashkeen", "Syed"
NAME_2, SURNAME_2 = "Anusha", "Nizamani"
if BRIDAL:  # the /bridal/ page lists the bride first
    (NAME_1, SURNAME_1), (NAME_2, SURNAME_2) = (NAME_2, SURNAME_2), (NAME_1, SURNAME_1)
DATE = "TUESDAY · 29 DECEMBER 2026 · 7:00 PM"
VENUE = "ZAM ZAM DIAMOND BANQUET · SHAH MURAD ROAD · THATTA"
HINT = "YOU ARE WARMLY INVITED"


# ---- Fonts -----------------------------------------------------------------
def use_lining_figures(tt):
    """Point the digits at the font's lining figures (its 'lnum' feature), as the site does."""
    if "GSUB" not in tt:
        return
    gsub = tt["GSUB"].table
    lookups = {i for fr in gsub.FeatureList.FeatureRecord if fr.FeatureTag == "lnum"
               for i in fr.Feature.LookupListIndex}
    mapping = {}
    for i in lookups:
        for sub in gsub.LookupList.Lookup[i].SubTable:
            if hasattr(sub, "ExtSubTable"):
                sub = sub.ExtSubTable
            mapping.update(getattr(sub, "mapping", {}) or {})
    if not mapping:
        return
    for table in tt["cmap"].tables:
        for code in range(0x30, 0x3A):
            g = table.cmap.get(code)
            if g in mapping:
                table.cmap[code] = mapping[g]


def font(file, size, wght=None):
    tt = TTFont(FONTS / file)
    if wght is not None and "fvar" in tt:
        tt = instancer.instantiateVariableFont(tt, {"wght": wght})
    use_lining_figures(tt)
    tt.flavor = None
    buf = io.BytesIO()
    tt.save(buf)
    buf.seek(0)
    return ImageFont.truetype(buf, size * SCALE)


def s(v):
    return int(round(v * SCALE))


# ---- Drawing helpers ---------------------------------------------------------
def foil_fill(size):
    """Horizontal gold-foil gradient image of the given size."""
    w, h = size
    grad = Image.new("RGB", (w, 1))
    px = grad.load()
    for x in range(w):
        t = x / max(1, w - 1)
        for (a, ca), (b, cb) in zip(FOIL, FOIL[1:]):
            if a <= t <= b:
                k = (t - a) / (b - a)
                px[x, 0] = tuple(int(ca[i] + (cb[i] - ca[i]) * k) for i in range(3))
                break
    return grad.resize((w, h))


def text_width(fnt, text, tracking=0):
    if not tracking:
        return fnt.getlength(text)
    return sum(fnt.getlength(c) for c in text) + tracking * (len(text) - 1)


def draw_tracked(draw, cx, y, text, fnt, fill, tracking):
    """Centred, letter-spaced text with its baseline at y."""
    x = cx - text_width(fnt, text, tracking) / 2
    for c in text:
        draw.text((x, y), c, font=fnt, fill=fill, anchor="ls")
        x += fnt.getlength(c) + tracking


def draw_foil_runs(img, runs, x, y):
    """Draw [(text, font), ...] one after another on a baseline, filled with foil."""
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    for text, fnt in runs:
        md.text((x, y), text, font=fnt, fill=255, anchor="ls")
        x += fnt.getlength(text)
    box = mask.getbbox()
    if box:
        fill = foil_fill((box[2] - box[0], box[3] - box[1]))
        img.paste(fill, box[:2], mask.crop(box))


def runs_width(runs):
    return sum(f.getlength(t) for t, f in runs)


def lozenge(draw, cx, cy, r, fill):
    draw.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=fill)


# ---- Build -------------------------------------------------------------------
def build():
    w, h = s(W), s(H)
    img = Image.new("RGB", (w, h), CREAM)

    # Soft radial light from the centre, like the site's hero
    glow = Image.new("L", (w // 8, h // 8))
    gp = glow.load()
    for yy in range(glow.height):
        for xx in range(glow.width):
            dx = (xx - glow.width / 2) / (glow.width / 2)
            dy = (yy - glow.height / 2) / (glow.height / 2)
            gp[xx, yy] = int(255 * max(0.0, 1 - math.hypot(dx * 0.85, dy * 1.1)) ** 1.4)
    glow = glow.resize((w, h), Image.BICUBIC)
    img = Image.composite(Image.new("RGB", (w, h), IVORY), img, glow)

    # Faint jaali lattice (the site's background pattern), stronger towards the edges
    lattice = Image.new("L", (w, h), 0)
    ld = ImageDraw.Draw(lattice)
    step = s(48)
    for gx in range(-step, w + step, step):
        for gy in range(-step, h + step, step):
            cx, cy = gx + step / 2, gy + step / 2
            ld.polygon([(cx, gy), (gx + step, cy), (cx, gy + step), (gx, cy)], outline=255, width=s(1))
            r = s(9)
            ld.ellipse([cx - r, cy - r, cx + r, cy + r], outline=255, width=s(1))
    edge = Image.eval(glow, lambda v: int((255 - v) * 0.16))
    lattice = Image.eval(lattice, lambda v: v)
    lattice = Image.composite(edge, Image.new("L", (w, h), 0), lattice)
    img = Image.composite(Image.new("RGB", (w, h), GOLD), img, lattice)

    d = ImageDraw.Draw(img)

    # Double gold border, inset from the edge, with small corner lozenges
    o, i = s(24), s(34)
    d.rectangle([o, o, w - o, h - o], outline=GOLD, width=s(2.2))
    d.rectangle([i, i, w - i, h - i], outline=GOLD_SOFT, width=s(1.2))
    for cx, cy in [(o, o), (w - o, o), (o, h - o), (w - o, h - o)]:
        lozenge(d, cx, cy, s(7), GOLD)
        lozenge(d, cx, cy, s(3), IVORY)
    for cx, cy in [(i + s(14), i + s(14)), (w - i - s(14), i + s(14)),
                   (i + s(14), h - i - s(14)), (w - i - s(14), h - i - s(14))]:
        lozenge(d, cx, cy, s(4), GOLD_SOFT)

    cx = w / 2

    # Kicker
    caps = font("CormorantGaramond-Variable.woff2", 26, wght=600)
    draw_tracked(d, cx, s(112), KICKER, caps, GOLD_DEEP, tracking=s(26 * 0.5))

    # Names: script face; the capital A comes from Alex Brush, as on the site
    script = font("GreatVibes-Regular.woff2", 112)
    script_a = font("AlexBrush-Regular.woff2", 104)
    amp_f = font("GreatVibes-Regular.woff2", 70)
    def runs(name):  # a leading capital A comes from Alex Brush, as on the site
        return [(name[0], script_a), (name[1:], script)] if name[0] == "A" else [(name, script)]
    left, right = runs(NAME_1), runs(NAME_2)
    gap = s(30)
    wl, wr, wa = runs_width(left), runs_width(right), amp_f.getlength("&")
    total = wl + gap + wa + gap + wr
    x0 = cx - total / 2
    base = s(242)
    draw_foil_runs(img, left, x0, base)
    amp_x = x0 + wl + gap
    d.text((amp_x, base - s(4)), "&", font=amp_f, fill=GOLD, anchor="ls")
    x2 = amp_x + wa + gap
    draw_foil_runs(img, right, x2, base)

    # Surnames, small italic, centred under each first name
    ital = font("CormorantGaramond-Italic.woff2", 34)
    d.text((x0 + wl / 2, s(300)), SURNAME_1, font=ital, fill=MUTED, anchor="ms")
    d.text((x2 + wr / 2, s(300)), SURNAME_2, font=ital, fill=MUTED, anchor="ms")

    # Thin gold rule with a dot at each end
    ry, rw = s(346), s(190)
    d.line([(cx - rw, ry), (cx + rw, ry)], fill=GOLD, width=s(1.5))
    for ex in (cx - rw, cx + rw):
        d.ellipse([ex - s(4.5), ry - s(4.5), ex + s(4.5), ry + s(4.5)], fill=GOLD)
    lozenge(d, cx, ry, s(6), GOLD)
    lozenge(d, cx, ry, s(2.5), IVORY)

    # Date, then venue
    date_f = font("CormorantGaramond-Variable.woff2", 31, wght=600)
    draw_tracked(d, cx, s(408), DATE, date_f, INK, tracking=s(31 * 0.14))
    venue_f = font("CormorantGaramond-Variable.woff2", 23, wght=600)
    draw_tracked(d, cx, s(458), VENUE, venue_f, GOLD_DEEP, tracking=s(23 * 0.18))

    # Quiet hint line
    hint_f = font("CormorantGaramond-Variable.woff2", 18, wght=500)
    draw_tracked(d, cx, s(540), HINT, hint_f, MUTED, tracking=s(18 * 0.32))

    out = img.resize((W, H), Image.LANCZOS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    for q in (90, 86, 82, 78, 74):
        out.save(OUT, "JPEG", quality=q, optimize=True, progressive=True)
        if OUT.stat().st_size < 190_000:
            break
    print(f"{OUT.relative_to(ROOT)}: {out.size[0]}x{out.size[1]}, "
          f"{OUT.stat().st_size / 1024:.0f} KB (quality {q})")


if __name__ == "__main__":
    build()
