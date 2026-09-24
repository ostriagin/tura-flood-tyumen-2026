"""
Editable A3 draft of the v4 poster (PowerPoint / Keynote).

Every element is a native, movable object: colour fields are rectangles,
every circle is a real oval, images that read as circles are given an
ellipse geometry so PowerPoint crops them properly, and all text is live.
Fonts are deliberately Arial / Arial Black so the file opens identically
on any Mac or PC; the PDF is the typeset version.
"""
import os

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Mm, Pt

A = os.environ.get("POSTER_ASSETS", "assets")
OUT = os.environ.get("POSTER_PPTX", "the_ground_remembers_EDITABLE_A3.pptx")

YEL = RGBColor(0xFF, 0xD4, 0x00)
INK = RGBColor(0x10, 0x16, 0x1C)
RED = RGBColor(0xE6, 0x33, 0x29)
WHT = RGBColor(0xFF, 0xFF, 0xFF)
GRY = RGBColor(0x6E, 0x77, 0x7E)
DIM = RGBColor(0x6A, 0x58, 0x00)
PALE = RGBColor(0xE7, 0xEA, 0xEC)
PALE2 = RGBColor(0xAE, 0xB6, 0xBC)
SAND = RGBColor(0xD9, 0xD2, 0xB4)

DISPLAY = "Arial Black"
BODY = "Arial"

prs = Presentation()
prs.slide_width = Mm(297)
prs.slide_height = Mm(420)
slide = prs.slides.add_slide(prs.slide_layouts[6])
sh = slide.shapes


def rect(x, y, w, h, fill, name):
    r = sh.add_shape(MSO_SHAPE.RECTANGLE, Mm(x), Mm(y), Mm(w), Mm(h))
    r.fill.solid()
    r.fill.fore_color.rgb = fill
    r.line.fill.background()
    r.shadow.inherit = False
    r.name = name
    return r


def oval(cx, cy, d, fill=None, line=None, name="circle", lw=1.0):
    o = sh.add_shape(MSO_SHAPE.OVAL, Mm(cx - d / 2), Mm(cy - d / 2), Mm(d), Mm(d))
    if fill is None:
        o.fill.background()
    else:
        o.fill.solid()
        o.fill.fore_color.rgb = fill
    if line is None:
        o.line.fill.background()
    else:
        o.line.color.rgb = line
        o.line.width = Pt(lw * 2.83)
    o.shadow.inherit = False
    o.name = name
    return o


def txt(x, y, w, h, lines, size=11, font=BODY, color=INK, bold=False,
        align=PP_ALIGN.LEFT, name="text", spacing=1.15, anchor=None):
    """lines: str, or list of (text, size, bold, color) tuples for runs."""
    tb = sh.add_textbox(Mm(x), Mm(y), Mm(w), Mm(h))
    tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    if anchor is not None:
        tf.vertical_anchor = anchor
    if isinstance(lines, str):
        lines = [lines]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        if isinstance(ln, str):
            runs = [(ln, size, bold, color)]
        elif ln and isinstance(ln[0], str):
            runs = [(ln[0], size, bold, color)]
        else:
            runs = ln
        for t, s, b, c in runs:
            r = p.add_run()
            r.text = t
            r.font.name = font
            r.font.size = Pt(s)
            r.font.bold = b
            r.font.color.rgb = c
    return tb


def circle_image(path, cx, cy, d, name="circle image"):
    pic = sh.add_picture(path, Mm(cx - d / 2), Mm(cy - d / 2), Mm(d), Mm(d))
    pic.name = name
    spPr = pic._element.spPr
    for g in spPr.findall(qn("a:prstGeom")):
        spPr.remove(g)
    geom = etree.SubElement(spPr, qn("a:prstGeom"))
    geom.set("prst", "ellipse")
    etree.SubElement(geom, qn("a:avLst"))
    return pic


def bubble(cx, cy, d, big, small, fill, big_col, small_col, name, big_pt, small_pt):
    oval(cx, cy, d, fill=fill, name=name)
    txt(cx - d / 2, cy - d / 2, d, d,
        [[(big, big_pt, True, big_col)], [(small, small_pt, False, small_col)]],
        align=PP_ALIGN.CENTER, spacing=1.0, anchor=MSO_ANCHOR.MIDDLE,
        name=name + " — label")


# ============================== background ==============================
rect(0, 0, 297, 420, WHT, "BACKGROUND — paper")

# ============================== masthead ================================
rect(0, 0, 297, 80, YEL, "MASTHEAD — yellow field")
txt(13, 6, 190, 6,
    "RGS Young Geographer of the Year 2026   ·   From Source to Sea   ·   KS5".upper(),
    size=11, color=DIM, name="eyebrow")
txt(13, 12.4, 200, 40, [["THE GROUND"], ["REMEMBERS"]],
    size=62, font=DISPLAY, color=INK, spacing=0.86, name="TITLE")
txt(13, 54.5, 172, 22,
    [[("Every old river town in Britain stands where it does because somebody "
       "once read the ground and worked out where the water goes. We have spent "
       "a century building on the parts they left alone. In July 2026 a Siberian "
       "city found out what that costs — ", 11.8, False, INK),
      ("so I measured it, and cut the same section through Shropshire.",
       11.8, True, INK)]],
    spacing=1.24, name="standfirst")
circle_image(f"{A}/sq_flood.png", 239.5, 40, 73, "MASTHEAD IMAGE — Tura at the peak")
txt(214, 61.5, 52, 10, [["The Tura at Tyumen,"], ["29 July 2026"]],
    size=11, bold=True, color=WHT, align=PP_ALIGN.RIGHT, spacing=1.2,
    name="masthead image caption")

# ============================== hero ====================================
oval(15, 85.9, 4, fill=RED, name="kicker dot")
txt(20, 82.6, 175, 8,
    "Two towns, 4,205 km apart, cut to the same scale".upper(),
    size=15, bold=True, color=INK, name="kicker")
txt(150, 82.9, 134, 7, "Sasha Ostriagin  ·  Bromsgrove School",
    size=12.5, bold=True, color=INK, align=PP_ALIGN.RIGHT, name="byline")
pic = sh.add_picture(f"{A}/twin_profiles.png", Mm(13), Mm(90.2), Mm(266), Mm(106.4))
pic.name = "HERO — twin cross-sections (Tyumen / Shrewsbury)"

# ============================== the finding =============================
bubble(28.5, 213.7, 31, "4,205", "km apart", INK, YEL, SAND,
       "finding circle", 20, 11)
txt(49, 199.5, 235, 30,
    [[("The two low banks match to within a metre.", 13.6, True, INK)],
     [("Nobody coordinated this. Two river towns, five centuries and four "
       "thousand kilometres apart — and the ground their founders refused sits "
       "at almost exactly the same height above the water, as does the ground "
       "their descendants later accepted. Read the section and you can see the "
       "decision, and the drift away from it.", 11, False, GRY)]],
    spacing=1.24, name="the finding")

# ============================== evidence ================================
circle_image(f"{A}/sq_pre.png", 32, 250.8, 38, "EVIDENCE — before, 18 June")
circle_image(f"{A}/sq_flood.png", 75, 250.8, 38, "EVIDENCE — peak, 29 July")
txt(13, 271.3, 40, 9, [[("18 JUNE 2026", 11, True, INK)],
                       [("137 ha of water", 11, False, GRY)]],
    spacing=1.15, name="caption — before")
txt(56, 271.3, 40, 9, [[("29 JULY 2026", 11, True, INK)],
                       [("415 ha of water", 11, False, GRY)]],
    spacing=1.15, name="caption — peak")
txt(99, 231.8, 185, 12,
    [[("The Tura ", 11.9, False, INK), ("tripled", 11.9, True, RED),
      (". A record 8.9 m rise put 281 hectares of dry land under water — "
       "40 km of road on the low bank against 11 km on the high — and almost "
       "all of the damage fell on the side the founders had left empty.",
       11.9, False, INK)]],
    spacing=1.26, name="evidence text")

STATS = [("1 in 6", "buildings flooded, low bank", True),
         ("1 in 250", "buildings flooded, high bank", False),
         ("9×", "more people in the water", True),
         ("40 km", "of road under water", False)]
for i, (n, t, hot) in enumerate(STATS):
    cx = 99 + 14.25 + i * 31.5
    if hot:
        oval(cx, 265.5, 28.5, fill=RED, name=f"stat {i+1}")
        nc, tc = WHT, WHT
    else:
        oval(cx, 265.5, 28.5, fill=None, line=INK, lw=1.0, name=f"stat {i+1}")
        nc, tc = INK, INK
    txt(cx - 13, 265.5 - 13, 26, 26,
        [[(n, 14, True, nc)], [(t, 11, False, tc)]],
        align=PP_ALIGN.CENTER, spacing=1.0, anchor=MSO_ANCHOR.MIDDLE,
        name=f"stat {i+1} — label")

# ============================== threshold ===============================
oval(20.5, 290, 15, fill=RED, name="threshold mark")
txt(13, 285.2, 15, 10, "!", size=24, font=DISPLAY, bold=True, color=WHT,
    align=PP_ALIGN.CENTER, name="threshold mark — glyph")
txt(32.5, 283.4, 251, 24,
    [[("THE OLD RULE HELD FOR 440 YEARS. THEN IT DIDN'T.", 14.5, True, INK)],
     [("The 2026 peak climbed onto the ", 11.9, False, INK),
      ("second terrace", 11.9, True, INK),
      (" — ground raised above the floodplain, built on in the belief that it "
       "stood clear — and it went under for the first time in living memory. "
       "Four centuries of siting logic is not a boundary but a ", 11.9, False, INK),
      ("threshold", 11.9, True, INK),
      (", and a record flood is what finds it.", 11.9, False, INK)]],
    spacing=1.26, name="threshold")

# ============================== britain =================================
rect(0, 310, 297, 76, INK, "BRITAIN — dark field")
txt(13, 314.4, 270, 10,
    [[("SO WHAT DOES THIS MEAN ", 21, True, WHT), ("HERE?", 21, True, YEL)]],
    font=DISPLAY, spacing=1.0, name="britain heading")
txt(13, 325.8, 97, 36,
    [[("Shrewsbury's gauge board at the Welsh Bridge starts at ", 11.6, False, PALE),
      ("47.0 m above sea level", 11.6, True, YEL),
      ("; the highest water ever recorded there, in 1795, stood 5.70 m up it. "
       "The medieval town, 27 m up, has never been the problem. ", 11.6, False, PALE),
      ("Frankwell", 11.6, True, YEL),
      (", eleven metres up, flooded three times in six weeks in 2000.",
       11.6, False, PALE)]],
    spacing=1.26, name="britain — Shrewsbury")
txt(116, 325.0, 72, 36,
    [[("6.3m → 8m", 31, True, YEL)],
     [("properties in England in areas at risk of flooding today, and by "
       "mid-century on the Environment Agency's own projection — one property "
       "in four.", 11, False, PALE2)]],
    font=DISPLAY, spacing=1.0, name="britain — the number")
txt(194, 325.8, 90, 36,
    [[("Free satellite imagery, a free 30 m elevation model, a few hundred "
       "lines of Python. ", 11.6, False, PALE),
      ("Any town in Britain can be sectioned this way in an afternoon.",
       11.6, True, YEL),
      (" The question is not whether a river floods, but how far above the "
       "water we are building now.", 11.6, False, PALE)]],
    spacing=1.26, name="britain — the method")

# source-to-sea ribbon
RIB = [("TURA", 13), ("TOBOL", 52), ("IRTYSH", 96), ("OB", 140),
       ("KARA SEA", 166), ("SEVERN", 209), ("BRISTOL CHANNEL", 246)]
for nm, x in RIB:
    col = YEL if nm in ("KARA SEA", "BRISTOL CHANNEL") else WHT
    txt(x, 365.5, 40, 6, nm, size=11.3, bold=True, color=col,
        name=f"ribbon — {nm}")
for x0, x1 in ((28, 50), (72, 94), (110, 138), (150, 164), (228, 244)):
    ln = sh.add_shape(MSO_SHAPE.RECTANGLE, Mm(x0), Mm(367.5), Mm(x1 - x0), Mm(0.6))
    ln.fill.solid(); ln.fill.fore_color.rgb = RGBColor(0x3A, 0x44, 0x4C)
    ln.line.fill.background(); ln.shadow.inherit = False
    ln.name = "ribbon rule"
txt(13, 371.5, 271, 10,
    [[("Tyumen's gauge zero sits ", 11, False, PALE2),
      ("48.5 m above sea level", 11, True, WHT),
      (", and the water that came over the embankment still has the Tobol, the "
       "Irtysh and the Ob to cross before it reaches the Arctic. Two continents, "
       "one habit: keep the oldest streets up on the bank, then build downhill.",
       11, False, PALE2)]],
    spacing=1.24, name="ribbon note")

# ============================== footer ==================================
FOOT = [
    (13, [("Method. ", True), ("Sentinel-2 L2A (10 m), 18 June and 29 July 2026. "
     "MNDWI (Xu, 2006) constrained by elevation and by connectivity to the "
     "channel. Terrain: Copernicus DEM GLO-30, 5 m sampling.", False)]),
    (105, [("Limits. ", True), ("GLO-30 is a surface model — rooftops, not bare "
     "earth — so no flood depth is modelled for Shrewsbury. The Tyumen figures "
     "are a lower bound: the image precedes the peak.", False)]),
    (197, [("Sasha Ostriagin", True), (", Bromsgrove School. I filled sandbags on "
     "the north bank for two days as the water came up. Code, data and QGIS "
     "project are public.", False)]),
]
for x, parts in FOOT:
    txt(x, 387.0, 87, 20,
        [[(t, 11, b, INK if b else GRY) for t, b in parts]],
        spacing=1.22, name="footer")
txt(13, 410.5, 271, 9,
    "Sources: Copernicus (ESA) · OpenStreetMap · WorldPop · Shropshire Council "
    "Welsh Bridge gauge board · Environment Agency NaFRA 2024.",
    size=11, color=GRY, spacing=1.22, name="sources")

prs.save(OUT)
print("wrote", OUT, "|", len(sh), "native objects")
