"""
make_twin_compact.py
--------------------
A small version of the Tyumen / Shrewsbury cross-section comparison, drawn at
the width it is actually placed on the poster (133 mm) so that every label in
it still renders at or above the competition's 10 pt minimum.

Output: poster/assets/twin_compact.png  (133 x 54 mm, drawn 1:1)
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

INK, RED, YEL, GREY = "#10161C", "#E63329", "#FFD400", "#707A82"
for fam in ("Poppins", "TeX Gyre Heros Cn", "DejaVu Sans"):
    if any(fam in f.name for f in matplotlib.font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam
        break
plt.rcParams["text.color"] = INK

ty = np.load(os.path.join(PROC, "cross_section_profile_v2.npz"))
sh = np.load(os.path.join(PROC, "shrewsbury_cross_section_profile.npz"))

PANELS = [
    dict(d=ty["dist"], e=ty["elev"].astype(float), town="TYUMEN, the Tura",
         flood_abs=57.49, bottom=30.0),
    dict(d=sh["dist"], e=sh["elev"].astype(float), town="SHREWSBURY, the Severn",
         flood_abs=52.25, bottom=4.0),
]

MM = 1 / 25.4
W_MM, H_MM = 133.0, 54.0
L_MM, R_MM, PAN_H = 2.0, 131.0, 19.0
Y_TOP = 46.0

fig = plt.figure(figsize=(W_MM * MM, H_MM * MM))
fig.patch.set_alpha(0)

for spec in PANELS:
    ax = fig.add_axes([L_MM / W_MM, spec["bottom"] / H_MM,
                       (R_MM - L_MM) / W_MM, PAN_H / H_MM])
    ax.patch.set_alpha(0)
    d, e = spec["d"], spec["e"]
    base = e.min()
    h = e - base
    fh = spec["flood_abs"] - base

    ax.fill_between([-450, 450], 0, fh, color=RED, linewidth=0, zorder=2)
    ax.fill_between(d, 0, h, color=INK, linewidth=0, zorder=3)

    hi = h[d <= -150].mean()
    lo = h[d >= 150].mean()
    for x, v in ((-300, hi), (330, lo)):
        ax.annotate("", xy=(x, v), xytext=(x, 0),
                    arrowprops=dict(arrowstyle="<->", color=YEL, linewidth=1.6,
                                    shrinkA=0, shrinkB=0), zorder=9)
        ax.text(x + 16, v / 2, "+%.0f m" % v, ha="left", va="center",
                fontsize=11.5, fontweight="bold", color=YEL, zorder=10,
                path_effects=[withStroke(linewidth=2.6, foreground=INK)])

    ax.set_xlim(-450, 450)
    ax.set_ylim(0, Y_TOP)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)

    fig.text(L_MM / W_MM, (spec["bottom"] + PAN_H + 4.6) / H_MM, spec["town"],
             ha="left", va="top", fontsize=11, fontweight="bold", color=INK)
    fig.text(R_MM / W_MM, (spec["bottom"] + PAN_H + 4.6) / H_MM,
             "old town · the ground we added", ha="right", va="top",
             fontsize=10.6, color=GREY)

x_mm = R_MM - L_MM
ve = (900.0 / x_mm) / (Y_TOP / PAN_H)
out = os.path.join(ASSETS, "twin_compact.png")
fig.savefig(out, dpi=400, transparent=True)
plt.close(fig)
print("wrote", out, "| vertical exaggeration x%.1f" % ve)
