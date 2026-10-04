"""
make_fig1_setting.py
Figure 1 of the report: the study area shown twice at the same scale -
(a) what it looks like (Sentinel-2 true colour, 18 June 2026, before the flood)
(b) how high it is (Copernicus DEM GLO-30).
Replaces the earlier fig1_context.png, whose second panel (a drainage-chain
schematic) did not belong in this report.
"""
import os, glob, json
import numpy as np
import rasterio
import geopandas as gpd
from shapely.geometry import Point
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.patheffects import withStroke

ROOT = os.getcwd()
FIG = f"{ROOT}/figures"

def band(datedir, b):
    return glob.glob(f"{ROOT}/data/raw/{datedir}/*{b}*")[0]

def stretch(a, lo=2, hi=98):
    lo_v, hi_v = np.percentile(a, [lo, hi])
    return np.clip((a - lo_v) / (hi_v - lo_v + 1e-6), 0, 1)

rgb = np.dstack([stretch(rasterio.open(band("s2_20260618", x)).read(1).astype("float32"))
                 for x in ("B04", "B03", "B02")])
with rasterio.open(band("s2_20260618", "B04")) as s:
    b = s.bounds; crs = s.crs
extent = [b.left, b.right, b.bottom, b.top]

dem = np.load(f"{ROOT}/data/processed/water_masks_dem_constrained.npz")["dem_elev"]
river = gpd.read_file(f"{ROOT}/data/processed/river_extent_20260618.geojson")
line = json.load(open(f"{ROOT}/data/processed/cross_section_line.json"))
start, end = np.array(line["start"]), np.array(line["end"])
gauge = np.array(line["gauge_utm"])
kremlin = gpd.GeoSeries([Point(65.5333, 57.1539)], crs="EPSG:4326").to_crs(crs).iloc[0]

halo = [withStroke(linewidth=3, foreground="white")]
fig = plt.figure(figsize=(8.4, 9.6))
axA = fig.add_axes([0.03, 0.04, 0.40, 0.90])
axB = fig.add_axes([0.47, 0.04, 0.40, 0.90])
cax = fig.add_axes([0.895, 0.33, 0.02, 0.32])

axA.imshow(rgb, extent=extent, origin="upper")
im = axB.imshow(dem, extent=extent, cmap="terrain", vmin=45, vmax=100, origin="upper")
river.plot(ax=axB, color="#4fc3f7", alpha=0.85, zorder=2)
river.boundary.plot(ax=axB, color="#01579b", linewidth=0.8, zorder=3)

def box(ax, x, y, txt, col):
    ax.text(x, y, txt, fontsize=9.5, color=col, fontweight="bold", ha="center", va="center",
            zorder=8, bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=col, alpha=0.9, lw=0.9))

for ax in (axA, axB):
    ax.plot([start[0], end[0]], [start[1], end[1]], color="#c62828", lw=2.4, zorder=6,
            solid_capstyle="butt")
    ax.plot(*gauge, marker="v", color="black", markersize=8, zorder=7,
            markeredgecolor="white", markeredgewidth=0.8)
    ax.plot(kremlin.x, kremlin.y, marker="*", color="#6a1b9a", markersize=15, zorder=7,
            markeredgecolor="white", markeredgewidth=0.8)
    ax.set_xlim(b.left, b.right); ax.set_ylim(b.bottom, b.top)
    ax.set_xticks([]); ax.set_yticks([])

box(axA, 653350, 6340250, "NORTH BANK\nlow ground", "#0d47a1")
box(axA, 653850, 6336000, "SOUTH BANK\nhigh ground, old city", "#4e342e")
box(axB, 652800, 6339900, "NORTH BANK\n59–63 m", "#0d47a1")
box(axB, 653850, 6336000, "SOUTH BANK\nup to ~90 m", "#4e342e")

axA.text(gauge[0] + 110, gauge[1] + 40, "River gauge", fontsize=8.8, ha="left", va="bottom",
         zorder=8, path_effects=halo)
axA.text(kremlin.x + 110, kremlin.y - 40, "Historic centre\n(founded 1586)", fontsize=8.8,
         ha="left", va="top", color="#4a148c", fontweight="bold", zorder=8, path_effects=halo)
axA.text(end[0] + 90, end[1] + 60, "Line of the\ncross-section", fontsize=8.8, color="#b71c1c",
         ha="left", va="bottom", fontweight="bold", zorder=8, path_effects=halo)
axA.text(652500, 6338330, "TURA RIVER", fontsize=9, color="white", fontweight="bold",
         ha="center", va="center", rotation=-8, zorder=8,
         path_effects=[withStroke(linewidth=2.5, foreground="#01579b")])

x0, y0, bar = b.left + 200, b.bottom + 300, 500
for ax in (axA, axB):
    ax.add_patch(Rectangle((x0, y0), bar, 62, fc="black", ec="white", lw=0.6, zorder=9))
    ax.add_patch(Rectangle((x0, y0), bar / 2, 62, fc="white", ec="black", lw=0.6, zorder=9))
    ax.text(x0 + bar + 60, y0 + 31, "500 m", fontsize=8.5, ha="left", va="center", zorder=9,
            path_effects=halo)
nx, ny = b.right - 330, b.bottom + 500
axA.annotate("", xy=(nx, ny + 360), xytext=(nx, ny),
             arrowprops=dict(arrowstyle="-|>", color="white", lw=2.2), zorder=9)
axA.text(nx, ny + 410, "N", fontsize=12, fontweight="bold", ha="center", va="bottom",
         color="white", zorder=9, path_effects=[withStroke(linewidth=2.5, foreground="black")])

axA.set_title("(a) From above: satellite image, 18 June 2026", fontsize=10.5, pad=6)
axB.set_title("(b) The same area by height above sea level", fontsize=10.5, pad=6)
cb = fig.colorbar(im, cax=cax)
cb.set_label("Elevation (m above sea level)", fontsize=9)
cb.ax.tick_params(labelsize=8)

plt.savefig(f"{FIG}/fig1_setting.png", dpi=200)
print("wrote figures/fig1_setting.png")
