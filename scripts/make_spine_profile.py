"""
make_spine_profile.py
---------------------
The poster's spine: the long profile of the Tura -> Tobol -> Irtysh -> Ob,
from the source in the Middle Urals to the Kara Sea.

Valley-floor elevations are the minimum of Copernicus DEM GLO-30 within about
1.8 km of each waypoint, which reliably finds the water surface. Distances are
cumulative great-circle distances along the waypoint polyline, so they are
shorter than the true channel length (the rivers meander); published channel
lengths are quoted separately.

Output: poster/assets/long_profile.png  (396 x 84 mm, drawn 1:1)
"""

import json
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
BLUE = "#1C6E8C"

for fam in ("Poppins", "TeX Gyre Heros Cn", "DejaVu Sans"):
    if any(fam in f.name for f in matplotlib.font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam
        break
plt.rcParams["text.color"] = INK

# name, river, lat, lon, DEM valley-floor elevation (m), note
WAYPOINTS = [
    ("Source, Middle Urals", "Tura", 58.3936, 59.3656, 370.0,
     "published 370 m; DEM 349 m within 2 km"),
    ("Verkhoturye", "Tura", 58.8620, 60.8060, 92.1, ""),
    ("Turinsk", "Tura", 58.0450, 63.7000, 54.5, ""),
    ("TYUMEN", "Tura", 57.1616, 65.5349, 46.4, "gauge zero 48.52 m"),
    ("Tura joins the Tobol", "Tobol", 57.6600, 66.8800, 44.2, "published 42.2 m"),
    ("Tobolsk", "Irtysh", 58.1960, 68.2550, 33.1, "Tobol joins the Irtysh"),
    ("Uvat", "Irtysh", 59.1400, 68.9000, 30.5, ""),
    ("Khanty-Mansiysk", "Ob", 61.0000, 69.0200, 22.1, "Irtysh joins the Ob"),
    ("Oktyabrskoye", "Ob", 62.4500, 66.0500, 9.1, ""),
    ("Salekhard", "Ob", 66.5300, 66.6000, 0.0, "DEM −2.0 m; GLO-30 is ±2 m"),
    ("Gulf of Ob", "Ob", 68.9000, 73.5000, 0.0, "sea level"),
]


def haversine(a, b):
    la1, lo1, la2, lo2 = map(np.deg2rad, [a[0], a[1], b[0], b[1]])
    h = (np.sin((la2 - la1) / 2) ** 2
         + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2)
    return 2 * 6371.0 * np.arcsin(np.sqrt(h))


dist = [0.0]
for i in range(1, len(WAYPOINTS)):
    p, q = WAYPOINTS[i - 1], WAYPOINTS[i]
    dist.append(dist[-1] + haversine((p[2], p[3]), (q[2], q[3])))
dist = np.array(dist)
elev = np.array([w[4] for w in WAYPOINTS])

json.dump(
    {"waypoints": [{"name": w[0], "river": w[1], "lat": w[2], "lon": w[3],
                    "elev_m": w[4], "note": w[5], "dist_km": round(d, 1)}
                   for w, d in zip(WAYPOINTS, dist)],
     "method": ("minimum Copernicus DEM GLO-30 elevation within ~1.8 km of each "
                "waypoint; distances are cumulative great-circle along the polyline"),
     "total_polyline_km": round(float(dist[-1]), 1)},
    open(os.path.join(PROC, "long_profile.json"), "w"), indent=2)

MM = 1 / 25.4
W_MM, H_MM = 396.0, 68.0
L_MM, R_MM, B_MM, T_MM = 26.0, 390.0, 23.0, 53.0

fig = plt.figure(figsize=(W_MM * MM, H_MM * MM))
fig.patch.set_alpha(0)
ax = fig.add_axes([L_MM / W_MM, B_MM / H_MM,
                   (R_MM - L_MM) / W_MM, (T_MM - B_MM) / H_MM])
ax.patch.set_alpha(0)

Y_TOP = 400.0
X0, X1 = -70.0, dist[-1] + 260.0

ax.fill_between([dist[-1], X1], 0, 24, color=BLUE, alpha=.9, linewidth=0, zorder=2)
ax.fill_between(dist, 0, elev, color=INK, linewidth=0, zorder=3)
ax.plot(dist, elev, color=INK, linewidth=1.4, zorder=4)

brk = 1  # Verkhoturye: the end of the mountain descent
ax.plot([dist[brk], dist[brk]], [0, Y_TOP], color=RED, linewidth=1.0,
        linestyle=(0, (3, 3)), zorder=5)

ax.annotate("", xy=(dist[0] + 4, 366), xytext=(dist[brk] - 4, 96),
            arrowprops=dict(arrowstyle="<->", color=RED, linewidth=2.0), zorder=8)
fall1 = elev[0] - elev[brk]
ax.text(dist[brk] + 55, 352, "%.0f m of fall in the first %.0f km" % (fall1, dist[brk]),
        fontsize=12.5, fontweight="bold", color=RED, ha="left", va="top", zorder=9)
ax.text(dist[brk] + 55, 296,
        "The Tura leaves the Middle Urals — and is never steep again.",
        fontsize=10.6, color=GREY, ha="left", va="top", zorder=9)

ax.annotate("", xy=(dist[brk] + 40, 150), xytext=(dist[-1] - 40, 150),
            arrowprops=dict(arrowstyle="<->", color=YEL, linewidth=2.8), zorder=8)
fall2 = elev[brk] - elev[-1]
run2 = dist[-1] - dist[brk]
ax.text((dist[brk] + dist[-1]) / 2, 202,
        "%.0f m of fall in the next %s km" % (fall2, format(int(round(run2, -1)), ",")),
        fontsize=15.5, fontweight="bold", color=INK, ha="center", va="center",
        zorder=9, path_effects=[withStroke(linewidth=3.4, foreground="white")])
ve = ((X1 - X0) / (R_MM - L_MM) * 1000.0) / (Y_TOP / (T_MM - B_MM))
ax.text((dist[brk] + dist[-1]) / 2, 104,
        "about %.0f cm per kilometre. The profile below is exaggerated "
        "×%s to be visible at all." % (100 * fall2 / run2,
                                         format(int(round(ve, -1)), ",")),
        fontsize=10.6, color=GREY, ha="center", va="center", zorder=9,
        path_effects=[withStroke(linewidth=3.0, foreground="white")])

BIG = {"TYUMEN", "Source, Middle Urals", "Gulf of Ob"}
for (name, river, la, lo, e, note), d in zip(WAYPOINTS, dist):
    big = name in BIG
    ax.plot([d], [e], marker="o", markersize=6.8 if big else 4.2,
            color=RED if name == "TYUMEN" else INK, zorder=10,
            markeredgecolor="white", markeredgewidth=1.0)

ax.set_xlim(X0, X1)
ax.set_ylim(0, Y_TOP)
ax.set_yticks([]); ax.set_xticks([])
for s in ax.spines.values():
    s.set_visible(False)


def fx(d):
    return (L_MM + (d - X0) / (X1 - X0) * (R_MM - L_MM)) / W_MM


LABELS = [
    (0, "SOURCE\n370 m", "left", 11.4, True, 0),
    (1, "Verkhoturye\n92 m", "center", 10.4, False, 1),
    (2, "Turinsk\n55 m", "center", 10.4, False, 1),
    (3, "TYUMEN  46 m\nthe 2026 flood", "center", 11.4, True, 0),
    (5, "Tobolsk\nTobol joins the Irtysh", "center", 10.4, False, 1),
    (7, "Khanty-Mansiysk\nIrtysh joins the Ob", "center", 10.4, False, 0),
    (9, "Salekhard\n0 m", "center", 10.4, False, 0),
    (10, "KARA SEA\nArctic Ocean", "right", 11.4, True, 0),
]
ROW_Y = {0: B_MM - 2.6, 1: B_MM - 12.6}
for i, txt, ha, fs, bold, row in LABELS:
    dx = 0.004 if ha == "left" else -0.004 if ha == "right" else 0.0
    if row == 1:
        fig.patches.append(plt.Rectangle(
            (fx(dist[i]) - 0.00035, (B_MM - 11.4) / H_MM), 0.0007, 8.6 / H_MM,
            transform=fig.transFigure, facecolor="#BFC6CB", edgecolor="none"))
    fig.text(fx(dist[i]) + dx, ROW_Y[row] / H_MM, txt, ha=ha, va="top",
             fontsize=fs, fontweight="bold" if bold else "normal",
             color=RED if txt.startswith("TYUMEN") else INK, linespacing=1.22)

SEGS = [("TURA", 0, 4, "#2E3B44"), ("TOBOL", 4, 5, "#4A6473"),
        ("IRTYSH", 5, 7, "#2E3B44"), ("OB", 7, 10, "#4A6473")]
for name, i, j, col in SEGS:
    x0, x1 = fx(dist[i]), fx(dist[j])
    fig.patches.append(plt.Rectangle((x0, (T_MM + 1.6) / H_MM), x1 - x0, 5.2 / H_MM,
                                     transform=fig.transFigure, facecolor=col,
                                     edgecolor="none", zorder=3))
    fig.text((x0 + x1) / 2, (T_MM + 4.2) / H_MM, name, ha="center", va="center",
             fontsize=11.8, fontweight="bold", color="white", zorder=4)

fig.text(L_MM / W_MM, (T_MM + 9.0) / H_MM,
         "Valley-floor elevation from Copernicus DEM GLO-30, measured for this poster "
         "· straight-line distance from source",
         ha="left", va="bottom", fontsize=10.2, color=GREY)
fig.text(R_MM / W_MM, (T_MM + 9.0) / H_MM,
         "channel lengths: Tura 1,030 km · Tobol 1,591 km · Irtysh 4,248 km "
         "· Ob 3,650 km",
         ha="right", va="bottom", fontsize=10.2, color=GREY)

out = os.path.join(ASSETS, "long_profile.png")
fig.savefig(out, dpi=400, transparent=True)
plt.close(fig)
print("wrote", out)
print("polyline %.0f km | source %.0f m" % (dist[-1], elev[0]))
for (n, r, la, lo, e, note), d in zip(WAYPOINTS, dist):
    print("  %-24s %6.0f km %6.1f m  %s" % (n, d, e, note))
