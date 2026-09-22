import os, json
import numpy as np
import rasterio
from rasterio.plot import reshape_as_image
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib import font_manager

ROOT = os.getcwd()
FIG = f"{ROOT}/figures"
os.makedirs(FIG, exist_ok=True)

# ---------- helper: build true-colour-ish RGB from B04/B03/B02 with stretch ----------
def load_rgb(datedir):
    with rasterio.open(f"{ROOT}/data/raw/{datedir}/*B02*") as s:
        pass

import glob
def band_path(datedir, band):
    matches = glob.glob(f"{ROOT}/data/raw/{datedir}/*{band}*")
    return matches[0]

def load_rgb_stack(datedir):
    r = rasterio.open(band_path(datedir, "B04")).read(1).astype(np.float32)
    g = rasterio.open(band_path(datedir, "B03")).read(1).astype(np.float32)
    b = rasterio.open(band_path(datedir, "B02")).read(1).astype(np.float32)
    def stretch(a, lo=2, hi=98):
        lo_v, hi_v = np.percentile(a, [lo, hi])
        return np.clip((a - lo_v) / (hi_v - lo_v + 1e-6), 0, 1)
    rgb = np.dstack([stretch(r), stretch(g), stretch(b)])
    with rasterio.open(band_path(datedir, "B04")) as s:
        transform = s.transform
        crs = s.crs
        extent = rasterio.transform.array_bounds(s.height, s.width, s.transform)
    return rgb, transform, crs, extent

rgb_pre, tr, crs, extent_pre = load_rgb_stack("s2_20260618")
rgb_flood, tr2, crs2, extent_flood = load_rgb_stack("s2_20260729")

# rasterio array_bounds returns (left, bottom, right, top)
def imshow_extent(e):
    left, bottom, right, top = e
    return [left, right, bottom, top]

# ---------- Figure 1: pre-flood vs flood extent maps ----------
pre_water = gpd.read_file(f"{ROOT}/data/processed/river_extent_20260618.geojson")
flood_water = gpd.read_file(f"{ROOT}/data/processed/flood_extent_20260729.geojson")
divider = gpd.read_file(f"{ROOT}/data/processed/ns_divider.geojson")

fig, axes = plt.subplots(1, 2, figsize=(13, 9))
for ax, rgb, ext, title in [
    (axes[0], rgb_pre, extent_pre, "Pre-flood: 18 June 2026"),
    (axes[1], rgb_flood, extent_flood, "Flood peak: 29 July 2026"),
]:
    ax.imshow(rgb, extent=imshow_extent(ext))
    pre_water.boundary.plot(ax=ax, color="#00e5ff", linewidth=1.1)
    if title.startswith("Flood"):
        flood_water.boundary.plot(ax=ax, color="#ff3d00", linewidth=1.1)
        flood_water.plot(ax=ax, color="#ff3d00", alpha=0.25)
    else:
        pre_water.plot(ax=ax, color="#00e5ff", alpha=0.3)
    divider.plot(ax=ax, color="yellow", linewidth=1.2, linestyle="--")
    ax.set_xlim(extent_flood[0], extent_flood[2])
    ax.set_ylim(extent_flood[1], extent_flood[3])
    ax.set_title(title, fontsize=12)
    ax.set_xticks([]); ax.set_yticks([])

legend_elems = [
    Patch(facecolor="#00e5ff", alpha=0.4, label="River / permanent water"),
    Patch(facecolor="#ff3d00", alpha=0.4, label="Flood extent (29 Jul)"),
    plt.Line2D([0],[0], color="yellow", linestyle="--", label="North/south divider (river axis)"),
]
fig.legend(handles=legend_elems, loc="lower center", ncol=3, fontsize=9, frameon=False)
fig.suptitle("Figure 1. Tura river flood extent at Tyumen, pre-flood vs peak", fontsize=13)
plt.tight_layout(rect=[0,0.05,1,0.95])
plt.savefig(f"{FIG}/fig1_flood_extent.png", dpi=160)
plt.close()
print("fig1 done")
