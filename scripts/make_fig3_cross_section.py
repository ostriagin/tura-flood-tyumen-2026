import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.getcwd()
FIG = f"{ROOT}/figures"

npz = np.load(f"{ROOT}/data/processed/cross_section_profile.npz")
dist = npz["dist"]
elev = npz["elev"]

GAUGE_ZERO = 48.52
FLOOD_ELEV = GAUGE_ZERO + 8.97  # 57.49 m a.s.l., the 897 cm peak of 2 Aug 2026

fig, ax = plt.subplots(figsize=(11, 5.5))
ax.plot(dist, elev, color="#4d4d4d", linewidth=1.8, zorder=3)
ax.fill_between(dist, elev, FLOOD_ELEV, where=(elev <= FLOOD_ELEV), color="#ff7043", alpha=0.45,
                 label="Inundated at 897 cm peak (57.49 m a.s.l.)", zorder=2)
ax.axhline(FLOOD_ELEV, color="#d32f2f", linestyle="--", linewidth=1.4, zorder=4,
           label="897 cm flood peak, 2 Aug 2026 (57.49 m a.s.l.)")
ax.axhline(GAUGE_ZERO, color="#1565c0", linestyle=":", linewidth=1.1, zorder=1,
           label="Gauge zero (48.52 m a.s.l.)")

ax.annotate("North bank\n(low terrace — new embankment)", xy=(320, elev[np.argmin(np.abs(dist-320))]),
            xytext=(230, 74), fontsize=9.5, ha="center",
            arrowprops=dict(arrowstyle="->", color="#333"))
ax.annotate("South bank\n(1586 fort site — steep bluff)", xy=(-320, elev[np.argmin(np.abs(dist+320))]),
            xytext=(-380, 80), fontsize=9.5, ha="center",
            arrowprops=dict(arrowstyle="->", color="#333"))
ax.annotate("River channel\n(~48-50 m)", xy=(0, elev[np.argmin(np.abs(dist))]),
            xytext=(60, 65), fontsize=9, ha="left",
            arrowprops=dict(arrowstyle="->", color="#333"))

ax.set_xlabel("Distance from river centreline (m)  —  south (–) to north (+)")
ax.set_ylabel("Elevation (m a.s.l., Copernicus DEM GLO-30)")
ax.set_title("Terrain cross-section through the historic centre, Tura at Tyumen,\nperpendicular to the river, with the 2 August 2026 flood peak (897 cm) ruled across it", fontsize=11.5)
ax.set_xlim(dist.min(), dist.max())
ax.legend(loc="upper right", fontsize=9, framealpha=0.9)
ax.grid(alpha=0.25)
plt.tight_layout()
plt.savefig(f"{FIG}/fig3_cross_section.png", dpi=160)
plt.close()
print("fig3 cross-section done")

# print some numbers for the report
below_flood = elev <= FLOOD_ELEV
print("width inundated at 897cm (m):", dist[below_flood].max() - dist[below_flood].min() if below_flood.any() else 0)
# north half only
north_mask = dist > 0   # positive distance is the north bank
south_mask = dist < 0   # negative distance is the south bank
print("north side max elev in transect:", elev[north_mask].max(), "min:", elev[north_mask].min())
print("south side max elev in transect:", elev[south_mask].max(), "min:", elev[south_mask].min())
