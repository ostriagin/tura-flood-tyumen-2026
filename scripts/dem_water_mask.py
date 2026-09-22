import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from scipy import ndimage
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import os
ROOT = os.getcwd()

# --- load MNDWI rasters (already on S2 grid, EPSG:32641) ---
with rasterio.open(f"{ROOT}/data/processed/mndwi_20260618.tif") as src:
    pre = src.read(1)
    profile = src.profile
    transform = src.transform
    crs = src.crs
    shape = src.shape

with rasterio.open(f"{ROOT}/data/processed/mndwi_20260729.tif") as src:
    flood = src.read(1)

# --- reproject DEM onto the same grid ---
dem_elev = np.zeros(shape, dtype=np.float32)
with rasterio.open(f"{ROOT}/data/raw/Copernicus_DSM_COG_10_N57_00_E065_00_DEM.tif") as dsrc:
    reproject(
        source=rasterio.band(dsrc, 1),
        destination=dem_elev,
        src_transform=dsrc.transform,
        src_crs=dsrc.crs,
        dst_transform=transform,
        dst_crs=crs,
        resampling=Resampling.bilinear,
    )

print("DEM reprojected. elev stats:", np.nanmin(dem_elev), np.nanmax(dem_elev), np.nanmean(dem_elev))

# gauge datum: gauge zero = 48.52 m a.s.l.; flood peak 891cm = 57.43 m a.s.l.
GAUGE_ZERO = 48.52
FLOOD_ELEV = GAUGE_ZERO + 8.91  # 57.43

def hydro_water(mndwi, elev, seed_thresh, cand_thresh, elev_cutoff, struct):
    """Water = spectrally plausible AND topographically low AND connected to a
    high-confidence seed pixel (also spectrally+topographically constrained)."""
    candidate = (mndwi > cand_thresh) & (elev < elev_cutoff)
    candidate = ndimage.binary_opening(candidate, structure=struct)
    seed = (mndwi > seed_thresh) & (elev < elev_cutoff)
    labeled, n = ndimage.label(candidate, structure=np.ones((3, 3)))
    seed_labels = set(labeled[seed & candidate].tolist()) - {0}
    keep = np.isin(labeled, list(seed_labels))
    keep = ndimage.binary_dilation(keep, structure=struct)
    return keep

struct = np.ones((3, 3))

# Pre-flood: river should sit near bed elevation (~48-52 m); allow a modest
# margin above bankfull for immediate floodplain / point bars.
pre_water = hydro_water(pre, dem_elev, seed_thresh=0.05, cand_thresh=-0.15,
                         elev_cutoff=53.0, struct=struct)

# Flood date: water can rise to the observed peak elevation (57.43 m) plus a
# small freeboard margin for imagery-DEM misregistration/vertical error.
flood_water = hydro_water(flood, dem_elev, seed_thresh=-0.05, cand_thresh=-0.35,
                           elev_cutoff=FLOOD_ELEV + 1.5, struct=struct)

pixel_area_ha = (transform.a * abs(transform.e)) / 10000.0
pre_ha = pre_water.sum() * pixel_area_ha
flood_ha = flood_water.sum() * pixel_area_ha
print("pre water ha (DEM-constrained):", pre_ha)
print("flood water ha (DEM-constrained):", flood_ha)

np.savez(f"{ROOT}/data/processed/water_masks_dem_constrained.npz",
         pre_water=pre_water, flood_water=flood_water,
         transform=np.array(transform)[:6], dem_elev=dem_elev)

fig, axes = plt.subplots(2, 3, figsize=(15, 12))
axes[0,0].imshow(pre, cmap="RdBu", vmin=-0.6, vmax=0.6); axes[0,0].set_title("MNDWI pre (18 Jun)")
axes[0,1].imshow(dem_elev, cmap="terrain"); axes[0,1].set_title("DEM elevation (m)")
axes[0,2].imshow(pre_water, cmap="Blues"); axes[0,2].set_title(f"Pre water DEM-constrained ({pre_ha:.1f} ha)")
axes[1,0].imshow(flood, cmap="RdBu", vmin=-0.6, vmax=0.6); axes[1,0].set_title("MNDWI flood (29 Jul)")
axes[1,1].imshow(dem_elev < (FLOOD_ELEV+1.5), cmap="gray"); axes[1,1].set_title(f"Elev < {FLOOD_ELEV+1.5:.1f} m mask")
axes[1,2].imshow(flood_water, cmap="Blues"); axes[1,2].set_title(f"Flood water DEM-constrained ({flood_ha:.1f} ha)")
for ax in axes.flat:
    ax.set_xticks([]); ax.set_yticks([])
plt.tight_layout()
plt.savefig(f"{ROOT}/data/processed/mndwi_check5_dem.png", dpi=110)
print("saved check5")
