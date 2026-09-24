import os, glob, json
import numpy as np
import rasterio
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = os.getcwd()
OUT = f"{ROOT}/poster/assets"
os.makedirs(OUT, exist_ok=True)

INK    = "#0A1A22"
BONE   = "#EDE6D8"
WATER  = "#5FD0D8"
FLOOD  = "#F25C2A"
OCHRE  = "#D9A441"
RULE   = "#2E5462"

def band_path(d, b): return glob.glob(f"{ROOT}/data/raw/{d}/*{b}*")[0]

def load_rgb(d):
    r = rasterio.open(band_path(d,"B04")).read(1).astype(np.float32)
    g = rasterio.open(band_path(d,"B03")).read(1).astype(np.float32)
    b = rasterio.open(band_path(d,"B02")).read(1).astype(np.float32)
    def st(a, lo=2, hi=98):
        l, h = np.percentile(a,[lo,hi]); return np.clip((a-l)/(h-l+1e-6),0,1)
    return np.dstack([st(r), st(g), st(b)])

with rasterio.open(band_path("s2_20260618","B04")) as s:
    b = s.bounds
full_extent = [b.left, b.right, b.bottom, b.top]

pre_w   = gpd.read_file(f"{ROOT}/data/processed/river_extent_20260618.geojson")
flood_w = gpd.read_file(f"{ROOT}/data/processed/flood_extent_20260729.geojson")

# crop to the flooded reach + margin
fb = flood_w.total_bounds  # minx miny maxx maxy
ymin = max(b.bottom, fb[1] - 350)
ymax = min(b.top,    fb[3] + 250)
crop = [b.left, b.right, ymin, ymax]
print("crop extent", crop, "aspect", (b.right-b.left)/(ymax-ymin))

rgb = {"pre": load_rgb("s2_20260618"), "flood": load_rgb("s2_20260729")}

def panel(which, fname):
    h_m = crop[3]-crop[2]; w_m = crop[1]-crop[0]
    figw = 5.0
    figh = figw * h_m / w_m
    fig = plt.figure(figsize=(figw, figh))
    ax = fig.add_axes([0,0,1,1])
    ax.imshow(rgb[which], extent=full_extent, origin="upper", interpolation="bilinear")
    if which == "pre":
        pre_w.plot(ax=ax, color=WATER, alpha=0.42, zorder=3)
        pre_w.plot(ax=ax, facecolor="none", edgecolor=WATER, linewidth=1.5, zorder=4)
    else:
        pre_w.plot(ax=ax, facecolor="none", edgecolor=WATER, linewidth=1.4, zorder=5)
        flood_w.plot(ax=ax, color=FLOOD, alpha=0.48, zorder=3)
        flood_w.plot(ax=ax, facecolor="none", edgecolor=FLOOD, linewidth=1.1, zorder=4)
    # scale bar
    x0 = crop[0] + 150; y0 = crop[2] + 170; bar = 500
    ax.add_patch(Rectangle((x0,y0), bar, 52, fc=BONE, ec=BONE, zorder=9))
    ax.add_patch(Rectangle((x0,y0), bar/2, 52, fc=INK, ec=BONE, lw=0.8, zorder=9))
    ax.text(x0+bar/2, y0+140, "500 m", fontsize=8.5, color=BONE, ha="center",
            family="TeX Gyre Heros", zorder=9)
    # north arrow
    nx = crop[1]-230; ny = crop[2]+170
    ax.annotate("", xy=(nx, ny+430), xytext=(nx, ny),
                arrowprops=dict(arrowstyle="-|>", color=BONE, lw=1.6), zorder=9)
    ax.text(nx, ny+470, "N", fontsize=10, color=BONE, ha="center", va="bottom",
            family="TeX Gyre Heros", weight="bold", zorder=9)
    ax.set_xlim(crop[0], crop[1]); ax.set_ylim(crop[2], crop[3])
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color(RULE); sp.set_linewidth(1.2)
    fig.savefig(f"{OUT}/{fname}", dpi=300, facecolor=INK)
    plt.close(fig)
    print("wrote", fname)

panel("pre",   "panel_pre.png")
panel("flood", "panel_flood.png")

# ---------- cross-section, dark, wide ----------
npz = np.load(f"{ROOT}/data/processed/cross_section_profile.npz")
dist, elev = npz["dist"], npz["elev"]
GZ = 48.52; PEAK = GZ + 8.91

fig = plt.figure(figsize=(12.0, 2.62))
ax = fig.add_axes([0.048, 0.175, 0.942, 0.775])
fig.patch.set_facecolor(INK); ax.set_facecolor(INK)

ax.fill_between(dist, elev, PEAK, where=(elev <= PEAK), color=FLOOD, alpha=0.64, zorder=2)
ax.plot(dist, elev, color=BONE, linewidth=2.0, zorder=4)
ax.axhline(PEAK, color=FLOOD, linestyle="--", linewidth=1.5, zorder=5)
ax.axhline(GZ, color=WATER, linestyle=":", linewidth=1.2, zorder=3)

ax.text(dist.min()+12, PEAK+2.0, "891 cm FLOOD PEAK  ·  57.43 m", color=FLOOD,
        fontsize=11.5, family="TeX Gyre Heros", weight="bold", va="bottom")
ax.text(dist.min()+12, GZ-1.7, "gauge zero  48.52 m", color=WATER, fontsize=9.5,
        family="TeX Gyre Heros", ha="left", va="top")

ax.annotate("SOUTH BANK — 1586 fort, historic centre", xy=(-395, 89), xytext=(-330, 72),
            color=OCHRE, fontsize=10.5, family="TeX Gyre Heros", weight="bold",
            arrowprops=dict(arrowstyle="-", color=OCHRE, lw=1.0))
ax.annotate("NORTH BANK — terrace, embankment, “second tier”", xy=(250, 61.5),
            xytext=(105, 78), color=WATER, fontsize=10.5, family="TeX Gyre Heros", weight="bold",
            arrowprops=dict(arrowstyle="-", color=WATER, lw=1.0))

ax.set_xlim(dist.min(), dist.max()); ax.set_ylim(42.5, 96)
ax.set_xlabel("metres from channel centreline        south ←   → north", color=BONE,
              fontsize=10, family="TeX Gyre Heros", labelpad=3)
ax.set_ylabel("m a.s.l.", color=BONE, fontsize=10, family="TeX Gyre Heros")
ax.tick_params(colors=BONE, labelsize=9)
for sp in ax.spines.values(): sp.set_color(RULE)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.grid(color=RULE, alpha=0.35, linewidth=0.6)
for lbl in ax.get_xticklabels()+ax.get_yticklabels(): lbl.set_family("TeX Gyre Heros")

fig.savefig(f"{OUT}/xsection.png", dpi=300, facecolor=INK)
plt.close(fig)
print("wrote xsection.png")
