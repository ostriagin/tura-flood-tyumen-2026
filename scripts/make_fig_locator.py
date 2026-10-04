"""
make_fig_locator.py
Where Tyumen is. Country outlines, lakes and rivers from Natural Earth
(public domain, naturalearthdata.com), drawn in a Lambert conformal conic
projection. The four rivers that carry Tyumen's water to the Arctic are
highlighted.
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patheffects import withStroke

NE, OUT = sys.argv[1], sys.argv[2]

for fam in ("Poppins", "DejaVu Sans"):
    if any(fam in f.name for f in matplotlib.font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam
        break

# ---- Lambert conformal conic ------------------------------------------------
P1, P2, LAT0, LON0 = map(np.deg2rad, (48.0, 66.0, 58.0, 42.0))
n = np.log(np.cos(P1) / np.cos(P2)) / np.log(
    np.tan(np.pi / 4 + P2 / 2) / np.tan(np.pi / 4 + P1 / 2))
F = np.cos(P1) * np.tan(np.pi / 4 + P1 / 2) ** n / n
rho0 = F / np.tan(np.pi / 4 + LAT0 / 2) ** n


def proj(lon, lat):
    lon = np.deg2rad(np.asarray(lon, float))
    lat = np.deg2rad(np.clip(np.asarray(lat, float), -80, 89.5))
    rho = F / np.tan(np.pi / 4 + lat / 2) ** n
    th = n * (lon - LON0)
    return rho * np.sin(th) * 6371.0, (rho0 - rho * np.cos(th)) * 6371.0


def rings(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "Polygon":
        yield from c
    elif t == "MultiPolygon":
        for poly in c:
            yield from poly
    elif t == "LineString":
        yield c
    elif t == "MultiLineString":
        yield from c


LAND, RUS, SEA, EDGE = "#EEE9DD", "#DCD3BD", "#CFE3EE", "#B5AD98"
INK, RED, RIVER = "#14181C", "#D92B1E", "#1C6E8C"

fig = plt.figure(figsize=(8.4, 4.9))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_facecolor(SEA)

for f in json.load(open(f"{NE}/ne_50m_admin_0_countries.geojson"))["features"]:
    rus = f["properties"].get("ADM0_A3") == "RUS"
    for r in rings(f["geometry"]):
        a = np.array(r)
        if a[:, 0].max() < -30 or a[:, 0].min() > 130 or a[:, 1].max() < 25:
            continue
        x, y = proj(a[:, 0], a[:, 1])
        ax.fill(x, y, facecolor=RUS if rus else LAND, edgecolor=EDGE, linewidth=0.5, zorder=1)

for f in json.load(open(f"{NE}/ne_50m_lakes.geojson"))["features"]:
    for r in rings(f["geometry"]):
        a = np.array(r)
        x, y = proj(a[:, 0], a[:, 1])
        ax.fill(x, y, facecolor=SEA, edgecolor="none", zorder=2)

WANT = {"Tura", "Tobol", "Irtysh", "Ob", "Malaya Ob"}
for f in json.load(open(f"{NE}/ne_10m_rivers_lake_centerlines.geojson"))["features"]:
    name = f["properties"].get("name_en") or f["properties"].get("name") or ""
    if name not in WANT or f["geometry"] is None:
        continue
    for r in rings(f["geometry"]):
        a = np.array(r)
        x, y = proj(a[:, 0], a[:, 1])
        ax.plot(x, y, color=RIVER, linewidth=2.0 if name != "Tura" else 2.4,
                solid_capstyle="round", zorder=4)

halo = [withStroke(linewidth=2.6, foreground="white")]


def label(lon, lat, text, dx=0, dy=0, **kw):
    x, y = proj(lon, lat)
    kw.setdefault("fontsize", 9.5)
    kw.setdefault("color", INK)
    ax.text(x + dx, y + dy, text, zorder=9, path_effects=halo, **kw)


def city(lon, lat, name, dx=60, dy=0, big=False, **kw):
    x, y = proj(lon, lat)
    ax.plot(x, y, "o", ms=9 if big else 4.5, color=RED if big else INK,
            markeredgecolor="white", markeredgewidth=1.2 if big else 0.8, zorder=8)
    kw.setdefault("ha", "left")
    kw.setdefault("va", "center")
    label(lon, lat, name, dx, dy, fontsize=13 if big else 9.5,
          fontweight="bold" if big else "normal", color=RED if big else INK, **kw)


city(65.53, 57.15, "TYUMEN", dx=90, dy=-10, big=True)
city(-0.13, 51.5, "London", dx=-70, ha="right")
city(37.62, 55.75, "Moscow", dx=70)

# river names, placed by hand along each course
label(61.0, 59.0, "Tura", fontsize=9, color=RIVER, fontweight="bold", ha="right", dy=40)
label(65.3, 54.6, "Tobol", fontsize=9, color=RIVER, fontweight="bold", ha="right")
label(73.5, 56.6, "Irtysh", fontsize=9, color=RIVER, fontweight="bold", ha="left", dx=40)
label(78.5, 60.7, "Ob", fontsize=9, color=RIVER, fontweight="bold", ha="left", dx=30)

label(59.3, 63.2, "URAL\nMOUNTAINS", fontsize=8, color="#7A705A", ha="center",
      rotation=78, linespacing=1.0)
label(72, 75.6, "KARA SEA", fontsize=9, color="#4F7E94", ha="center", fontstyle="italic")
label(88, 66, "R U S S I A", fontsize=11, color="#8C8166", ha="center")
label(67, 50.0, "KAZAKHSTAN", fontsize=8.5, color="#8C8166", ha="center")

# distance from London to Tyumen
x1, y1 = proj(-0.13, 51.5)
x2, y2 = proj(65.53, 57.15)
ax.annotate("", xy=(x2 - 90, y2 + 40), xytext=(x1 + 60, y1 + 60),
            arrowprops=dict(arrowstyle="-", color=INK, lw=0.9, linestyle=(0, (4, 3)),
                            connectionstyle="arc3,rad=-0.18"), zorder=6)
mx, my = proj(30, 62.0)
ax.text(mx, my + 330, "about 4,100 km", fontsize=9, ha="center", color=INK,
        path_effects=halo, zorder=9)

xl, _ = proj(-9, 50)
xr, _ = proj(92, 58)
_, yb_ = proj(42, 45.5)
_, yt_ = proj(60, 79.5)
ax.set_xlim(xl, xr)
ax.set_ylim(yb_, yt_)
ax.set_aspect("equal")
fig.set_size_inches(8.4, 8.4 * (yt_ - yb_) / (xr - xl))
ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values():
    s.set_visible(False)

fig.savefig(OUT, dpi=220)
print("wrote", OUT)
