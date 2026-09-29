"""
make_section.py
---------------
Valley cross-sections for the poster, one town per image, drawn at the width
each is actually placed so every label stays above the competition's 10 pt
minimum. Palette is set for a light yellow (hazard) background.

Terms used, and used consistently across the whole poster:
    HIGH BANK  - the side of the valley well above the river
    LOW BANK   - the side barely above it

Outputs: poster/assets/section_tyumen.png
         poster/assets/section_shrewsbury.png
"""

import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patheffects import withStroke

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(ROOT, "data", "processed")
ASSETS = os.path.join(ROOT, "poster", "assets")

INK = "#14181C"
RED = "#D92B1E"
WATER = "#D92B1E"
GREY = "#6A6550"
CREAM = "#FFFFFF"

for fam in ("Poppins", "TeX Gyre Heros Cn", "DejaVu Sans"):
    if any(fam in f.name for f in matplotlib.font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam
        break
plt.rcParams["text.color"] = INK

MM = 1 / 25.4

TOWNS = {
    "tyumen": dict(
        npz="cross_section_profile_v2.npz",
        flood_abs=57.49,
        flood_label="2 Aug 2026 — the river came up 9 m",
        high="HIGH BANK", high_sub="",
        low="LOW BANK", low_sub="",
        out="section_tyumen.png", w=214.0, h=52.0),
    "shrewsbury": dict(
        npz="shrewsbury_cross_section_profile.npz",
        flood_abs=52.25,
        flood_label="1 Nov 2000 — the river came up 5 m",
        high="HIGH BANK", high_sub="",
        low="LOW BANK", low_sub="",
        out="section_shrewsbury.png", w=214.0, h=52.0),
}


def draw(key):
    s = TOWNS[key]
    npz = np.load(os.path.join(PROC, s["npz"]))
    d = npz["dist"]
    e = npz["elev"].astype(float)
    base = e.min()
    h = e - base
    fh = s["flood_abs"] - base

    W_MM, H_MM = s["w"], s["h"]
    L, R, B, PH = 3.0, W_MM - 3.0, 13.0, 26.0
    Y_TOP = 52.0

    fig = plt.figure(figsize=(W_MM * MM, H_MM * MM))
    fig.patch.set_alpha(0)
    ax = fig.add_axes([L / W_MM, B / H_MM, (R - L) / W_MM, PH / H_MM])
    ax.patch.set_alpha(0)

    ax.fill_between([-450, 450], 0, fh, color=WATER, linewidth=0, zorder=2)
    ax.fill_between(d, 0, h, color=INK, linewidth=0, zorder=3)

    hi = h[d <= -150].mean()
    lo = h[d >= 150].mean()
    for x, v in ((-300, hi), (330, lo)):
        ax.annotate("", xy=(x, v), xytext=(x, 0),
                    arrowprops=dict(arrowstyle="<->", color=CREAM, linewidth=2.0,
                                    shrinkA=0, shrinkB=0), zorder=9)
        ax.text(x + 18, v / 2, "+%.0f m" % v, ha="left", va="center",
                fontsize=13, fontweight="bold", color=CREAM, zorder=10,
                path_effects=[withStroke(linewidth=2.8, foreground=INK)])

    # the flood level, captioned out over the channel
    ax.plot([30, 30], [fh + 0.6, 31.0], color=RED, linewidth=1.1, zorder=8)
    ax.text(38, 32.0, s["flood_label"], ha="left", va="top", fontsize=10.8,
            fontweight="bold", color=RED, zorder=8)

    ax.set_xlim(-450, 450)
    ax.set_ylim(0, Y_TOP)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)

    # bank captions, under the section
    fig.text(L / W_MM, (B - 2.2) / H_MM, s["high"], ha="left", va="top",
             fontsize=11.6, fontweight="bold", color=INK)
    if s["high_sub"]: fig.text(L / W_MM, (B - 7.0) / H_MM, s["high_sub"], ha="left", va="top",
             fontsize=10.6, color=GREY)
    fig.text(R / W_MM, (B - 2.2) / H_MM, s["low"], ha="right", va="top",
             fontsize=11.6, fontweight="bold", color=RED)
    if s["low_sub"]: fig.text(R / W_MM, (B - 7.0) / H_MM, s["low_sub"], ha="right", va="top",
             fontsize=10.6, color=GREY)

    # scale bar, top left of the plot
    fig.text(L / W_MM, (B + PH + 5.0) / H_MM,
             "900 m across  ·  vertical exaggeration ×%.0f"
             % ((900.0 / (R - L)) / (Y_TOP / PH)),
             ha="left", va="top", fontsize=10.6, color=GREY)
    fig.text(R / W_MM, (B + PH + 5.0) / H_MM,
             "Copernicus DEM GLO-30", ha="right", va="top",
             fontsize=10.6, color=GREY)

    out = os.path.join(ASSETS, s["out"])
    fig.savefig(out, dpi=400, transparent=True)
    plt.close(fig)
    print("wrote %-28s high bank +%.1f m  low bank +%.1f m  flood +%.1f m"
          % (s["out"], hi, lo, fh))


for k in TOWNS:
    draw(k)
