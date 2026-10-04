"""
make_fig_method_steps.py
The masking method shown as three pictures instead of a paragraph:
  1. the water index alone, with a threshold loose enough to catch shadowed
     water - it also catches shadow and dark roofs all over the city
  2. the same, kept only where the ground lies below the flood level
  3. the same, kept only where it is connected to the river  -> final map
All three are computed from the same 29 July 2026 scene.
"""
import os, glob
import numpy as np
import rasterio
from scipy import ndimage
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.getcwd()

def band(b):
    return glob.glob(f"{ROOT}/data/raw/s2_20260729/*{b}*")[0]

def stretch(a, lo=2, hi=98):
    lo_v, hi_v = np.percentile(a, [lo, hi])
    return np.clip((a - lo_v) / (hi_v - lo_v + 1e-6), 0, 1)

rgb = np.dstack([stretch(rasterio.open(band(x)).read(1).astype("float32"))
                 for x in ("B04", "B03", "B02")])
grey = rgb.mean(axis=2)
base = np.dstack([grey * 0.55 + 0.40] * 3)          # pale grey backdrop

with rasterio.open(f"{ROOT}/data/processed/mndwi_20260729.tif") as s:
    mndwi = s.read(1)
z = np.load(f"{ROOT}/data/processed/water_masks_dem_constrained.npz")
dem, final = z["dem_elev"], z["flood_water"]

CAND, CUTOFF = -0.35, 57.43 + 1.5                   # as in dem_water_mask.py
step1 = mndwi > CAND
step2 = step1 & (dem < CUTOFF)
step3 = final

# crop to the central part of the scene so detail is visible
r0, r1 = 110, 900
panels = [(step1, "1  Water index only",
           "catches the flood, but also\nshadow and dark roofs city-wide"),
          (step2, "2  Keep only low ground",
           "anything above the flood\nlevel cannot be flood water"),
          (step3, "3  Keep what joins the river",
           "isolated patches removed:\nthe final flood map")]

fig, axes = plt.subplots(1, 3, figsize=(8.4, 4.9))
fig.subplots_adjust(left=0.01, right=0.99, top=0.86, bottom=0.13, wspace=0.04)
for ax, (mask, title, note) in zip(axes, panels):
    img = base[r0:r1].copy()
    m = mask[r0:r1]
    img[m] = img[m] * 0.25 + np.array([0.85, 0.17, 0.12]) * 0.75
    ax.imshow(img, interpolation="nearest")
    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=6, loc="left")
    ax.text(0.5, -0.03, note, transform=ax.transAxes, fontsize=9, ha="center", va="top",
            color="#444444", linespacing=1.25)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_edgecolor("#888888"); sp.set_linewidth(0.6)
    share = 100.0 * m.sum() / m.size
    ax.text(0.03, 0.03, "%.0f%% of this view flagged" % share, transform=ax.transAxes,
            fontsize=8.5, color="white", va="bottom",
            bbox=dict(boxstyle="round,pad=0.25", fc="#14181C", ec="none", alpha=0.8))
plt.savefig(f"{ROOT}/figures/fig3_method_steps.png", dpi=220)
print("wrote figures/fig3_method_steps.png",
      [round(100.0 * p[0][r0:r1].mean(), 1) for p in panels])
