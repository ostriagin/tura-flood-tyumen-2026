import os, glob
import numpy as np
import rasterio
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

ROOT = os.getcwd()
FIG = f"{ROOT}/figures"

def band_path(datedir, band):
    return glob.glob(f"{ROOT}/data/raw/{datedir}/*{band}*")[0]

def load_rgb(datedir):
    r = rasterio.open(band_path(datedir, "B04")).read(1).astype(np.float32)
    g = rasterio.open(band_path(datedir, "B03")).read(1).astype(np.float32)
    bl = rasterio.open(band_path(datedir, "B02")).read(1).astype(np.float32)
    def stretch(a, lo=2, hi=98):
        lo_v, hi_v = np.percentile(a, [lo, hi])
        return np.clip((a - lo_v) / (hi_v - lo_v + 1e-6), 0, 1)
    return np.dstack([stretch(r), stretch(g), stretch(bl)])

with rasterio.open(band_path("s2_20260618", "B04")) as s:
    b = s.bounds
extent = [b.left, b.right, b.bottom, b.top]

rgb_pre = load_rgb("s2_20260618")
rgb_flood = load_rgb("s2_20260729")

pre_water = gpd.read_file(f"{ROOT}/data/processed/river_extent_20260618.geojson")
flood_water = gpd.read_file(f"{ROOT}/data/processed/flood_extent_20260729.geojson")
divider = gpd.read_file(f"{ROOT}/data/processed/ns_divider.geojson")

fig = plt.figure(figsize=(8.6, 11.2))
axL = fig.add_axes([0.045, 0.085, 0.44, 0.855])
axR = fig.add_axes([0.515, 0.085, 0.44, 0.855])

def scalebar(ax, bar=500):
    x0, y0 = b.left + 180, b.bottom + 280
    ax.add_patch(Rectangle((x0, y0), bar, 62, fc="black", ec="black", zorder=9))
    ax.add_patch(Rectangle((x0, y0), bar/2, 62, fc="white", ec="black", zorder=9))
    ax.text(x0, y0 - 105, "0", fontsize=8, ha="center", color="white", zorder=9,
            bbox=dict(boxstyle="square,pad=0.08", fc="black", ec="none", alpha=0.55))
    ax.text(x0 + bar, y0 - 105, "500 m", fontsize=8, ha="center", color="white", zorder=9,
            bbox=dict(boxstyle="square,pad=0.08", fc="black", ec="none", alpha=0.55))

def northarrow(ax):
    nx, ny = b.right - 300, b.bottom + 520
    ax.annotate("", xy=(nx, ny + 350), xytext=(nx, ny),
                arrowprops=dict(arrowstyle="-|>", color="white", lw=2.0), zorder=9)
    ax.text(nx, ny + 400, "N", fontsize=12, fontweight="bold", color="white",
            ha="center", va="bottom", zorder=9)

for ax, rgb, title in [
    (axL, rgb_pre,   "(a) Pre-flood: 18 June 2026"),
    (axR, rgb_flood, "(b) Flood peak: 29 July 2026"),
]:
    ax.imshow(rgb, extent=extent, origin="upper")
    pre_water.plot(ax=ax, facecolor="none", edgecolor="#00e5ff", linewidth=1.2, zorder=4)
    if ax is axL:
        pre_water.plot(ax=ax, color="#00e5ff", alpha=0.30, zorder=3)
    else:
        flood_water.plot(ax=ax, color="#ff3d00", alpha=0.35, zorder=3)
        flood_water.plot(ax=ax, facecolor="none", edgecolor="#ff3d00", linewidth=0.9, zorder=5)
    divider.plot(ax=ax, color="yellow", linewidth=1.3, linestyle="--", zorder=6)
    ax.set_xlim(b.left, b.right); ax.set_ylim(b.bottom, b.top)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=11.5, pad=7)
    scalebar(ax)

northarrow(axR)

# north / south labels on the left panel
axL.text(652350, 6340600, "NORTH\nBANK", fontsize=9, color="white", fontweight="bold",
         ha="center", va="center", zorder=8,
         bbox=dict(boxstyle="round,pad=0.25", fc="black", ec="none", alpha=0.5))
axL.text(654400, 6335600, "SOUTH\nBANK", fontsize=9, color="white", fontweight="bold",
         ha="center", va="center", zorder=8,
         bbox=dict(boxstyle="round,pad=0.25", fc="black", ec="none", alpha=0.5))

legend_elems = [
    Patch(facecolor="#00e5ff", alpha=0.45, edgecolor="#00e5ff",
          label="Permanent river channel (18 Jun): 137.4 ha"),
    Patch(facecolor="#ff3d00", alpha=0.45, edgecolor="#ff3d00",
          label="Flood extent (29 Jul): 415.0 ha"),
    plt.Line2D([0], [0], color="yellow", linestyle="--", label="North/south divider (river axis)"),
]
fig.legend(handles=legend_elems, loc="lower center", ncol=1, fontsize=9.5,
           frameon=False, bbox_to_anchor=(0.5, 0.005))

plt.savefig(f"{FIG}/fig2_flood_extent.png", dpi=175)
print("fig2 flood extent done")
