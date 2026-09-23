import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.getcwd()
FIG = f"{ROOT}/figures"
s = json.load(open(f"{ROOT}/data/processed/exposure_summary.json"))

fig, axes = plt.subplots(1, 3, figsize=(12, 4.2))

# buildings
cats = ["North bank", "South bank"]
tot = [s["buildings_total_north"], s["buildings_total_south"]]
fl = [s["buildings_flooded_north"], s["buildings_flooded_south"]]
x = np.arange(2)
axes[0].bar(x, tot, width=0.5, color="#cfd8dc", label="Total buildings")
axes[0].bar(x, fl, width=0.5, color="#e53935", label="Flooded buildings")
for i in range(2):
    pct = 100*fl[i]/tot[i]
    axes[0].text(x[i], tot[i]+max(tot)*0.02, f"{fl[i]}/{tot[i]}\n({pct:.1f}%)", ha="center", fontsize=8.5)
axes[0].set_xticks(x); axes[0].set_xticklabels(cats)
axes[0].set_title("Buildings")
axes[0].legend(fontsize=7.5, loc="upper right")

# roads
rl = [s["roads_flooded_length_km_north"], s["roads_flooded_length_km_south"]]
axes[1].bar(x, rl, width=0.5, color="#fb8c00")
for i in range(2):
    axes[1].text(x[i], rl[i]+max(rl)*0.02, f"{rl[i]:.1f} km", ha="center", fontsize=9)
axes[1].set_xticks(x); axes[1].set_xticklabels(cats)
axes[1].set_title("Flooded road length")

# area
ar = [391.16, 23.87]
axes[2].bar(x, ar, width=0.5, color="#8e24aa")
for i in range(2):
    axes[2].text(x[i], ar[i]+max(ar)*0.02, f"{ar[i]:.0f} ha", ha="center", fontsize=9)
axes[2].set_xticks(x); axes[2].set_xticklabels(cats)
axes[2].set_title("Flood extent area")

fig.suptitle("Flood exposure by bank, Tura at Tyumen, 29 July 2026", fontsize=12.5)
plt.tight_layout(rect=[0,0,1,0.93])
plt.savefig(f"{FIG}/fig4_exposure.png", dpi=160)
print("fig4 exposure done")
