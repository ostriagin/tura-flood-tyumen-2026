import os, json
import numpy as np
import rasterio
import geopandas as gpd
from shapely.geometry import Point
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = os.getcwd()
FIG = f"{ROOT}/figures"
os.makedirs(FIG, exist_ok=True)

with rasterio.open(f"{ROOT}/data/processed/mndwi_20260618.tif") as src:
    b = src.bounds
    crs = src.crs
extent = [b.left, b.right, b.bottom, b.top]

dem = np.load(f"{ROOT}/data/processed/water_masks_dem_constrained.npz")["dem_elev"]
river = gpd.read_file(f"{ROOT}/data/processed/river_extent_20260618.geojson")
line = json.load(open(f"{ROOT}/data/processed/cross_section_line.json"))
start, end = np.array(line["start"]), np.array(line["end"])
gauge = np.array(line["gauge_utm"])
kremlin = gpd.GeoSeries([Point(65.5333, 57.1539)], crs="EPSG:4326").to_crs(crs).iloc[0]

fig = plt.figure(figsize=(7.4, 9.7))
ax  = fig.add_axes([0.045, 0.045, 0.385, 0.885])
cax = fig.add_axes([0.445, 0.33,  0.019, 0.31])
axd = fig.add_axes([0.58,  0.045, 0.40,  0.885]); axd.axis("off")

im = ax.imshow(dem, extent=extent, cmap="terrain", vmin=45, vmax=100, origin="upper")
river.plot(ax=ax, color="#4fc3f7", alpha=0.8, zorder=2)
river.boundary.plot(ax=ax, color="#01579b", linewidth=0.9, zorder=3)

ax.plot([start[0], end[0]], [start[1], end[1]], color="#c62828", linewidth=2.6,
        solid_capstyle="butt", zorder=5)
for p in (start, end):
    ax.plot(*p, marker="_", color="#c62828", markersize=12, markeredgewidth=2.6, zorder=5)
ax.text(end[0] + 80, end[1] + 80, "Transect\n(Fig. 3)", fontsize=8.5,
        color="#c62828", ha="left", va="bottom", fontweight="bold", zorder=6)

ax.plot(*gauge, marker="v", color="black", markersize=8, zorder=6)
ax.text(gauge[0] + 90, gauge[1] - 70, "City gauge", fontsize=8.5, ha="left", va="top", zorder=6)
ax.plot(kremlin.x, kremlin.y, marker="*", color="#4a148c", markersize=15, zorder=6)
ax.text(kremlin.x + 90, kremlin.y - 50, "Historic centre\n& kremlin (1586)", fontsize=8.5,
        ha="left", va="top", color="#4a148c", fontweight="bold", zorder=6)

ax.annotate("NORTH BANK\nlow terrace\n59–63 m", xy=(652640, 6339900), fontsize=9,
            color="#1a237e", fontweight="bold", ha="center", va="center", zorder=6,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#1a237e", alpha=0.82, lw=0.8))
ax.annotate("SOUTH BANK\nhigh bluff\nto ~90 m", xy=(653950, 6336000), fontsize=9,
            color="#4e342e", fontweight="bold", ha="center", va="center", zorder=6,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#4e342e", alpha=0.82, lw=0.8))

x0, y0, bar = b.left + 200, b.bottom + 300, 500
ax.add_patch(Rectangle((x0, y0), bar, 62, fc="black", ec="black", zorder=7))
ax.add_patch(Rectangle((x0, y0), bar/2, 62, fc="white", ec="black", zorder=7))
ax.text(x0, y0 - 105, "0", fontsize=8, ha="center", zorder=7)
ax.text(x0 + bar, y0 - 105, "500 m", fontsize=8, ha="center", zorder=7)

nx, ny = b.right - 330, b.bottom + 560
ax.annotate("", xy=(nx, ny + 350), xytext=(nx, ny),
            arrowprops=dict(arrowstyle="-|>", color="black", lw=1.8), zorder=7)
ax.text(nx, ny + 400, "N", fontsize=11.5, fontweight="bold", ha="center", va="bottom", zorder=7)

ax.set_xlim(b.left, b.right); ax.set_ylim(b.bottom, b.top)
ax.set_xticks([]); ax.set_yticks([])
ax.set_title("(a) Terrain of the study reach", fontsize=11, pad=7)

cb = fig.colorbar(im, cax=cax)
cb.set_label("Elevation (m a.s.l.)", fontsize=9)
cb.ax.tick_params(labelsize=8)

# --- vertical drainage chain ---
axd.set_xlim(0, 1); axd.set_ylim(0, 1)
axd.text(0.5, 0.985, "(b) Drainage chain: source to sea", fontsize=11,
         ha="center", va="top")
axd.text(0.5, 0.945, "(schematic, not to scale)", fontsize=8.5, style="italic",
         ha="center", va="top", color="#555555")

chain = ["Tura", "Tobol", "Irtysh", "Ob", "Kara Sea\n(Arctic Ocean)"]
ys = np.linspace(0.85, 0.12, len(chain))
for i, (y, name) in enumerate(zip(ys, chain)):
    is_end = (i == len(chain) - 1)
    axd.text(0.5, y, name, fontsize=12 if not is_end else 11, ha="center", va="center",
             fontweight="bold" if i in (0, len(chain) - 1) else "normal",
             color="#006064" if is_end else "#01579b",
             bbox=dict(boxstyle="round,pad=0.5",
                       fc="#e0f7fa" if is_end else "#e1f5fe",
                       ec="#006064" if is_end else "#01579b", lw=1.3))
    if i < len(chain) - 1:
        axd.annotate("", xy=(0.5, ys[i + 1] + 0.055), xytext=(0.5, y - 0.055),
                     arrowprops=dict(arrowstyle="-|>", color="#0277bd", lw=2.0))

axd.annotate("Tyumen\n(this study)", xy=(0.585, 0.85), xytext=(0.90, 0.85),
             fontsize=9.5, color="#c62828", fontweight="bold", ha="center", va="center",
             arrowprops=dict(arrowstyle="-|>", color="#c62828", lw=1.5))
axd.text(0.5, 0.045, "Flow direction: south-west → north-east,\ndraining the eastern flank of the Urals",
         fontsize=8.5, ha="center", va="top", color="#555555", style="italic")

plt.savefig(f"{FIG}/fig1_context.png", dpi=190)
print("fig1 context done")
