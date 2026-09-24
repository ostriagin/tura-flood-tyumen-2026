"""
make_twin_profiles.py
---------------------
The poster's hero graphic: the Tura at Tyumen and the Severn at Shrewsbury,
same DEM, same sampling routine, same scales, drawn one above the other as
height above the river so the two sections can be compared directly.

Output: poster/assets/twin_profiles.png  (280 x 112 mm, drawn 1:1 so that
matplotlib point sizes are the final printed point sizes)
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
os.makedirs(ASSETS, exist_ok=True)

INK = "#10161C"
RED = "#E63329"
YEL = "#FFD400"
GREY = "#707A82"

for fam in ("Poppins", "TeX Gyre Heros Cn", "DejaVu Sans"):
    if any(fam in f.name for f in matplotlib.font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam
        break
plt.rcParams["text.color"] = INK

MM = 1 / 25.4
W_MM, H_MM = 280.0, 76.0
FIG_W, FIG_H = W_MM * MM, H_MM * MM


def fx(mm):      # mm from the left -> figure fraction
    return mm / W_MM


def fy(mm):      # mm from the bottom -> figure fraction
    return mm / H_MM


ty = np.load(os.path.join(PROC, "cross_section_profile_v2.npz"))
sh = np.load(os.path.join(PROC, "shrewsbury_cross_section_profile.npz"))

PANELS = [
    dict(
        d=ty["dist"], e=ty["elev"].astype(float),
        town="TYUMEN", sub="the Tura  ·  western Siberia",
        flood_abs=57.43,
        flood_label="31 July 2026\nthe river came up 8.9 m",
        high_label="THE OLD TOWN",
        high_note="chosen in 1586.  Dry throughout.",
        low_label="THE NEW DISTRICT",
        low_note="120 of its 716 buildings went under",
        bottom=48.0,
    ),
    dict(
        d=sh["dist"], e=sh["elev"].astype(float),
        town="SHREWSBURY", sub="the Severn  ·  England",
        flood_abs=52.25,
        flood_label="1 November 2000\nthe river came up 5.3 m",
        high_label="THE OLD TOWN",
        high_note="castle, abbey, market.  Dry throughout.",
        low_label="FRANKWELL",
        low_note="flooded three times in six weeks",
        bottom=14.0,
    ),
]

Y_TOP = 63.0          # metres above the channel, shared by both panels
PAN_H_MM = 24.0
L_MM, R_MM = 13.0, 278.0

fig = plt.figure(figsize=(FIG_W, FIG_H))
fig.patch.set_alpha(0)

for spec in PANELS:
    ax = fig.add_axes([fx(L_MM), fy(spec["bottom"]),
                       fx(R_MM - L_MM), fy(PAN_H_MM)])
    ax.patch.set_alpha(0)
    d, e = spec["d"], spec["e"]
    base = e.min()
    h = e - base
    flood_h = spec["flood_abs"] - base

    # water first, as a flat sheet across the whole section; the landform is
    # drawn over it, so red shows exactly where the ground lies below the peak
    ax.fill_between([-450, 450], 0, flood_h, color=RED, linewidth=0, zorder=2)
    ax.fill_between(d, 0, h, color=INK, linewidth=0, zorder=3)
    ax.plot(d, h, color=INK, linewidth=1.2, zorder=4)

    # --- height of each bank above the water --------------------------------
    hi = h[d <= -150].mean()
    lo = h[d >= 150].mean()
    for x, val in ((-300, hi), (355, lo)):
        ax.annotate("", xy=(x, val), xytext=(x, 0),
                    arrowprops=dict(arrowstyle="<->", color=YEL, linewidth=2.4,
                                    shrinkA=0, shrinkB=0), zorder=9)
        ax.text(x + 14, val / 2, "+%.0f m" % val, ha="left", va="center",
                fontsize=13, fontweight="bold", color=YEL, zorder=10,
                path_effects=[withStroke(linewidth=3.4, foreground=INK)])

    # --- bank captions, in the clear air above each side --------------------
    ax.text(-448, Y_TOP - 0.5, spec["high_label"], ha="left", va="top",
            fontsize=12.5, fontweight="bold", color=INK, zorder=8)
    ax.text(-448, Y_TOP - 5.6, spec["high_note"], ha="left", va="top",
            fontsize=10.9, color=GREY, zorder=8)
    ax.text(448, Y_TOP - 0.5, spec["low_label"], ha="right", va="top",
            fontsize=12.5, fontweight="bold", color=RED, zorder=8)
    ax.text(448, Y_TOP - 5.6, spec["low_note"], ha="right", va="top",
            fontsize=10.9, color=GREY, zorder=8)

    # --- flood caption, lifted clear and tied down to the water surface -----
    ax.plot([34, 34], [flood_h + 0.4, 29.6], color=RED, linewidth=1.1, zorder=8)
    ax.text(42, 30.0, spec["flood_label"], ha="left", va="top",
            fontsize=11, fontweight="bold", color=RED, zorder=8,
            linespacing=1.25)

    ax.set_xlim(-450, 450)
    ax.set_ylim(0, Y_TOP)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)

    # --- town name, hung under the section ----------------------------------
    y = fy(spec["bottom"] - 2.5)
    fig.text(fx(L_MM), y, spec["town"], ha="left", va="top",
             fontsize=14, fontweight="bold", color=INK)
    fig.text(fx(L_MM + 60), y - fy(1.4), spec["sub"], ha="left", va="top",
             fontsize=11, color=GREY)
    fig.text(fx(R_MM), y - fy(1.4), "river surface  %.0f m" % base,
             ha="right", va="top", fontsize=10, color=GREY)

# --- scale bar and method line, in the bottom margin ------------------------
axs = fig.add_axes([fx(L_MM), fy(3.4), fx(58), fy(2.6)])
axs.set_xlim(0, 900)
axs.set_ylim(0, 1)
axs.axis("off")
axs.plot([0, 500], [0.5, 0.5], color=INK, linewidth=2.4, solid_capstyle="butt")
for x in (0, 500):
    axs.plot([x, x], [0.05, 0.95], color=INK, linewidth=2.4)
axs.text(525, 0.5, "500 m", ha="left", va="center", fontsize=10.4, color=INK)

x_mm = R_MM - L_MM
ve = (900.0 / x_mm) / (Y_TOP / PAN_H_MM)
fig.text(fx(R_MM), fy(4.7), "vertical exaggeration ×%.0f    ·    "
         "Copernicus DEM GLO-30, 5 m sampling, 900 m section" % round(ve),
         ha="right", va="center", fontsize=10, color=GREY)

out = os.path.join(ASSETS, "twin_profiles.png")
fig.savefig(out, dpi=400, transparent=True)
plt.close(fig)
print("wrote", out, "| vertical exaggeration x%.2f" % ve)

for spec in PANELS:
    d, e = spec["d"], spec["e"]
    base = e.min()
    h = e - base
    print("%-12s river %.2f m | old town +%.1f m | low bank +%.1f m | peak +%.1f m"
          % (spec["town"], base, h[d <= -150].mean(), h[d >= 150].mean(),
             spec["flood_abs"] - base))
