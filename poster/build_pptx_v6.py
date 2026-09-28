"""
build_pptx_v6.py
----------------
Editable A3-landscape version of poster v6, laid out on the geometry measured
from the rendered HTML so it matches the print PDF.

Everything is a native PowerPoint object: colour fields are rectangles, the
hazard banding is a picture (decoration only), the satellite images are real
circles, and every word is live text you can click and retype.

Fonts are Arial / Arial Black so the file opens the same on any Mac or PC.
Arial is a little wider than the Poppins used in the PDF, so a line here and
there may wrap differently; nudge the box or shorten the line.
"""
import os

from lxml import etree
from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Mm, Pt

A = os.environ.get("POSTER_ASSETS", "assets")
OUT = os.environ.get("POSTER_PPTX", "nowhere_to_go_EDITABLE_A3.pptx")

BG = RGBColor(0xFD, 0xF4, 0xCE)
INK = RGBColor(0x14, 0x18, 0x1C)
RED = RGBColor(0xD9, 0x2B, 0x1E)
HI = RGBColor(0xFF, 0xD4, 0x00)
GREY = RGBColor(0x6A, 0x65, 0x50)
CARD = RGBColor(0xFF, 0xFF, 0xFF)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

DISPLAY = "Arial Black"
BODY = "Arial"


# ----------------------------------------------------------- hazard banding
def hazard(path, w_mm, h_mm, chevron=False, dpi=300):
    px = lambda mm: max(1, int(round(mm / 25.4 * dpi)))
    W, H = px(w_mm), px(h_mm)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    band = px(3.2)
    step = band * 2
    for x in range(-H, W + H, step):
        d.polygon([(x, 0), (x + band, 0), (x + band - H, H), (x - H, H)],
                  fill=(0xFF, 0xD4, 0x00, 255))
        d.polygon([(x + band, 0), (x + step, 0), (x + step - H, H), (x + band - H, H)],
                  fill=(0x14, 0x18, 0x1C, 255))
    if chevron:
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).polygon(
            [(0, 0), (W, 0), (W, int(H * .52)), (int(W * .53), H),
             (int(W * .47), H), (0, int(H * .52))], fill=255)
        im.putalpha(mask)
    im.save(path)
    return path


os.makedirs(A, exist_ok=True)
hazard(f"{A}/rule_stripe.png", 420, 1.1)
hazard(f"{A}/cut_band.png", 420, 14.5, chevron=True)

prs = Presentation()
prs.slide_width = Mm(420)
prs.slide_height = Mm(297)
slide = prs.slides.add_slide(prs.slide_layouts[6])
sh = slide.shapes


def rect(x, y, w, h, fill, name, line=None):
    r = sh.add_shape(MSO_SHAPE.RECTANGLE, Mm(x), Mm(y), Mm(w), Mm(h))
    if fill is None:
        r.fill.background()
    else:
        r.fill.solid(); r.fill.fore_color.rgb = fill
    if line is None:
        r.line.fill.background()
    else:
        r.line.color.rgb = line; r.line.width = Pt(1)
    r.shadow.inherit = False
    r.name = name
    return r


def txt(x, y, w, h, paras, name="text", align=PP_ALIGN.LEFT, spacing=1.16,
        anchor=None, font=BODY):
    """paras: list of paragraphs; each is a list of (text, pt, bold, colour)."""
    tb = sh.add_textbox(Mm(x), Mm(y), Mm(w), Mm(h))
    tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    if anchor is not None:
        tf.vertical_anchor = anchor
    for i, runs in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        for t, pt, b, c in runs:
            r = p.add_run()
            r.text = t
            r.font.name = font
            r.font.size = Pt(pt)
            r.font.bold = b
            r.font.color.rgb = c
    return tb


def circle_image(path, x, y, d, name):
    pic = sh.add_picture(path, Mm(x), Mm(y), Mm(d), Mm(d))
    pic.name = name
    spPr = pic._element.spPr
    for g in spPr.findall(qn("a:prstGeom")):
        spPr.remove(g)
    geom = etree.SubElement(spPr, qn("a:prstGeom"))
    geom.set("prst", "ellipse")
    etree.SubElement(geom, qn("a:avLst"))
    return pic


# =============================================================== background
rect(0, 0, 420, 297, BG, "BACKGROUND — hazard yellow")
sh.add_picture(f"{A}/rule_stripe.png", Mm(0), Mm(0), Mm(420), Mm(1.1)).name = \
    "hazard rule (decoration)"

# =================================================================== header
txt(10, 2.6, 400, 6,
    [[("RGS YOUNG GEOGRAPHER OF THE YEAR 2026   ·   FROM SOURCE TO SEA   "
       "·   KEY STAGE 5", 10.4, False, GREY)]],
    name="eyebrow", font="Courier New")

txt(10, 10.2, 64, 22,
    [[("NOWHERE", 26, True, INK)], [("TO GO", 26, True, RED)]],
    name="TITLE", spacing=0.95, font=DISPLAY)

txt(77, 14.5, 287, 16,
    [[("The ", 11.3, False, INK), ("Tura", 11.3, True, INK),
      (" rises at 370 m in the Ural mountains and reaches the Arctic through the ",
       11.3, False, INK),
      ("Tobol", 11.3, True, INK), (", the ", 11.3, False, INK),
      ("Irtysh", 11.3, True, INK), (" and the ", 11.3, False, INK),
      ("Ob", 11.3, True, INK),
      (". It does four-fifths of its falling in the first 98 km.", 11.3, True, INK),
      (" After that it drops five centimetres per kilometre — so when the "
       "water rises it cannot run away downstream. It spreads. That is why half "
       "of Russia’s marshland is here, and why ", 11.3, False, INK),
      ("Tyumen", 11.3, True, INK),
      (" went under in August 2026.", 11.3, False, INK)]],
    name="standfirst", spacing=1.2)

txt(340, 19.6, 70, 10,
    [[("SASHA OSTRIAGIN", 10.9, True, INK)],
     [("Bromsgrove School", 10.4, False, GREY)]],
    name="byline", align=PP_ALIGN.RIGHT, spacing=1.2)

# ================================================================ key terms
TERMS = [("TYUMEN", "Oldest Russian city in Siberia, 1586.", INK),
         ("TURA", "Tyumen’s river. 1,030 km, from the Urals.", INK),
         ("TOBOL", "The river the Tura runs into. 1,591 km.", INK),
         ("IRTYSH", "4,248 km, from China. Takes the Tobol.", INK),
         ("OB", "3,650 km more, to the Arctic Ocean.", RED)]
for i, (name, defn, edge) in enumerate(TERMS):
    x = 10 + i * 80.45
    rect(x, 32.4, 78.2, 13.6, CARD, "term card — %s" % name)
    rect(x, 32.4, 1.3, 13.6, edge, "term edge — %s" % name)
    txt(x + 2.9, 33.7, 74, 11,
        [[(name, 10.4, True, INK)], [(defn, 10.4, False, GREY)]],
        name="term — %s" % name, spacing=1.18)

# ============================================================= long profile
sh.add_picture(f"{A}/long_profile.png", Mm(10), Mm(47.6), Mm(400), Mm(59.9)).name = \
    "LONG PROFILE — Tura to Kara Sea (measured)"

# ============================================================ theory boxes
THEORY = [
    ("WHAT THE GRADIENT BUILDS",
     [("Steep upper course: vertical erosion cuts a V-shaped valley. Once the ", False),
      ("gradient", True),
      (" collapses, lateral erosion takes over — the river meanders and widens a ", False),
      ("floodplain", True), (", then abandons it. Those are the ", False),
      ("river terraces", True), (" Tyumen is built on.", False)]),
    ("WHY SO MUCH OF IT DROWNS",
     [("With almost no slope the channels cannot clear meltwater or rain: ", False),
      ("half of all the marshland in Russia", True),
      (" is in this basin. The Ob also flows ", False), ("north", True),
      (", so meltwater from the thawing south meets 2 m of ice and spreads up "
       "to 50 km sideways.", False)]),
    ("WHO WANTS THE WATER",
     [("27 million people; two-thirds of Russia’s oil and gas. Flat ground "
       "allows just ", False),
      ("one dam on 3,650 km of Ob", True),
      (". Upstream, China’s Irtysh–Karamay canal takes ", False),
      ("2.5 km³ a year", True),
      (" from the longest transboundary tributary on Earth, with no treaty.", False)]),
]
for i, (head, runs) in enumerate(THEORY):
    x = 10 + i * 134.2
    rect(x, 109.1, 131.6, 28.2, CARD, "theory card %d" % (i + 1))
    txt(x + 2, 110.3, 127.6, 26,
        [[(head, 11.0, True, INK)],
         [(t, 10.2, b, INK) for t, b in runs]],
        name="theory %d" % (i + 1), spacing=1.12)

# ================================================================== TYUMEN
rect(10, 138.0, 76, 8.9, INK, "tag — what happened at Tyumen")
txt(12.6, 139.9, 72, 6, [[("WHAT HAPPENED AT TYUMEN", 13.0, True, HI)]],
    name="tag text — Tyumen")
txt(89, 137.7, 321, 10,
    [[("Rain on the headwaters in the Ural mountains. Seven hundred kilometres "
       "downstream the Tura rose for three weeks and peaked at ", 11.3, False, INK),
      ("897 cm on 2 August 2026", 11.3, True, INK),
      (" — a record summer flood. I filled sandbags on the ", 11.3, False, INK),
      ("low bank", 11.3, True, INK),
      (" for two days, then mapped it from Sentinel-2.", 11.3, False, INK)]],
    name="Tyumen intro", spacing=1.2)

sh.add_picture(f"{A}/section_tyumen.png", Mm(10), Mm(149.1), Mm(214), Mm(51.9)).name = \
    "SECTION — Tyumen, the Tura"

circle_image(f"{A}/sq_pre.png", 228, 149.1, 36, "Sentinel-2 — 18 June 2026")
circle_image(f"{A}/sq_flood.png", 266.6, 149.1, 36, "Sentinel-2 — 29 July 2026")
txt(228, 186.1, 36, 9, [[("18 JUNE", 10.4, True, INK)],
                        [("137 ha", 10.4, False, GREY)]],
    name="caption — 18 June", spacing=1.14)
txt(266.6, 186.1, 36, 9, [[("29 JULY", 10.4, True, INK)],
                          [("415 ha — tripled", 10.4, False, GREY)]],
    name="caption — 29 July", spacing=1.14)

txt(305.2, 148.6, 104.8, 10, [[("1 in 6", 28.4, True, RED)]],
    name="stat — 1 in 6", spacing=0.95, font=DISPLAY)
txt(305.2, 159.3, 104.8, 14,
    [[("buildings flooded on the ", 10.4, False, INK), ("low bank", 10.4, True, INK),
      (", against ", 10.4, False, INK), ("1 in 250", 10.4, True, INK),
      (" on the ", 10.4, False, INK), ("high bank", 10.4, True, INK),
      (". Nine times as many people were in the water.", 10.4, False, INK)]],
    name="stat text — banks", spacing=1.16)

# ===================================================================== cut
sh.add_picture(f"{A}/cut_band.png", Mm(0), Mm(203.0), Mm(420), Mm(14.5)).name = \
    "hazard chevron (decoration)"
rect(146.5, 201.2, 127, 14.8, INK, "cut message plate")
txt(148.5, 202.6, 123, 12,
    [[("Tyumen’s ", 13.2, True, WHITE), ("low bank", 13.2, True, HI),
      (" sits 11 m above the river.", 13.2, True, WHITE)],
     [("So does Frankwell, in Shrewsbury.", 13.2, True, WHITE)]],
    name="THE CUT — message", align=PP_ALIGN.CENTER, spacing=1.05)

# ================================================================== BRITAIN
rect(10, 219.9, 71.9, 8.9, RED, "tag — what could happen here")
txt(12.6, 221.8, 68, 6, [[("WHAT COULD HAPPEN HERE", 13.0, True, WHITE)]],
    name="tag text — Britain")
txt(84.9, 219.5, 325, 10,
    [[("The Severn at Shrewsbury has the same shape as the Tura at Tyumen: a "
       "medieval town on the ", 11.3, False, INK), ("high bank", 11.3, True, INK),
      (", and a district on the ", 11.3, False, INK), ("low bank", 11.3, True, INK),
      (" that floods. Same section, different country.", 11.3, False, INK)]],
    name="Britain intro", spacing=1.2)

sh.add_picture(f"{A}/section_shrewsbury.png", Mm(10), Mm(231.5), Mm(214), Mm(51.9)).name = \
    "SECTION — Shrewsbury, the Severn"

txt(228, 231.0, 182, 11, [[("6.3m → 8m", 31.2, True, RED)]],
    name="stat — 6.3m to 8m", spacing=0.95, font=DISPLAY)
txt(228, 242.6, 182, 10,
    [[("English properties in areas at risk of flooding today, and by mid-century "
       "on the Environment Agency’s own projection — ", 10.4, False, INK),
      ("one property in four", 10.4, True, INK), (".", 10.4, False, INK)]],
    name="stat text — England at risk", spacing=1.16)
txt(228, 254.4, 182, 22,
    [[("What the two sections say.", 10.4, True, INK),
      (" Height above the river predicts flooding better than any line on a map, "
       "and it costs nothing to measure — the elevation data is free, global "
       "and open. The question is not whether a river floods, but how far above "
       "it we are building, and where the next ", 10.4, False, INK),
      ("river terrace", 10.4, True, INK), (" up begins.", 10.4, False, INK)]],
    name="Britain conclusion", spacing=1.16)

# =================================================================== footer
txt(10, 282.5, 400, 13,
    [[("Method.", 10.4, True, INK),
      (" Copernicus DEM GLO-30 elevations; flood extent from Sentinel-2 L2A using "
       "MNDWI (Xu 2006) constrained by elevation and connectivity to the channel. "
       "Imagery and elevation data © European Union / ESA, free and open "
       "licence; every map and section here is my own work from them. ",
       10.4, False, GREY),
      ("Sources:", 10.4, True, INK),
      (" Britannica; WWF/TNC Freshwater Ecoregions of the World; Eurasian "
       "Development Bank 2025; Environment Agency NaFRA 2024. Full list in the "
       "repository.", 10.4, False, GREY)]],
    name="footer — method and sources", spacing=1.14)

prs.save(OUT)
print("wrote", OUT, "|", len(sh), "native objects")
