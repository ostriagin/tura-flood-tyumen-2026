import os, glob
import numpy as np
import rasterio, geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patheffects as pe

ROOT = os.getcwd()
OUT = f"{ROOT}/poster/assets"
os.makedirs(OUT, exist_ok=True)

PAPER = "#FBF7EF"; INK = "#22303A"; WATER = "#0E7C86"
FLOOD = "#D2452A"; OCHRE = "#B6802A"; RULE = "#C9BBA4"

def bp(d,b): return glob.glob(f"{ROOT}/data/raw/{d}/*{b}*")[0]
def load_rgb(d):
    r=rasterio.open(bp(d,"B04")).read(1).astype(np.float32)
    g=rasterio.open(bp(d,"B03")).read(1).astype(np.float32)
    b=rasterio.open(bp(d,"B02")).read(1).astype(np.float32)
    def st(a,lo=2,hi=98):
        l,h=np.percentile(a,[lo,hi]); return np.clip((a-l)/(h-l+1e-6),0,1)
    return np.dstack([st(r),st(g),st(b)])

with rasterio.open(bp("s2_20260618","B04")) as s: b = s.bounds
full=[b.left,b.right,b.bottom,b.top]
pre_w=gpd.read_file(f"{ROOT}/data/processed/river_extent_20260618.geojson")
fl_w =gpd.read_file(f"{ROOT}/data/processed/flood_extent_20260729.geojson")
fb=fl_w.total_bounds
crop=[b.left,b.right,max(b.bottom,fb[1]-350),min(b.top,fb[3]+250)]
rgb={"pre":load_rgb("s2_20260618"),"flood":load_rgb("s2_20260729")}

def panel(which,fname,figw=5.0):
    h=crop[3]-crop[2]; w=crop[1]-crop[0]
    fig=plt.figure(figsize=(figw, figw*h/w)); ax=fig.add_axes([0,0,1,1])
    ax.imshow(rgb[which],extent=full,origin="upper",interpolation="bilinear")
    if which=="pre":
        pre_w.plot(ax=ax,color=WATER,alpha=0.45,zorder=3)
        pre_w.plot(ax=ax,facecolor="none",edgecolor="#19A5B0",linewidth=1.6,zorder=4)
    else:
        pre_w.plot(ax=ax,facecolor="none",edgecolor="#19A5B0",linewidth=1.5,zorder=5)
        fl_w.plot(ax=ax,color=FLOOD,alpha=0.50,zorder=3)
        fl_w.plot(ax=ax,facecolor="none",edgecolor="#8E2A16",linewidth=1.0,zorder=4)
    halo=[pe.withStroke(linewidth=2.6,foreground="white")]
    x0=crop[0]+150; y0=crop[2]+175; bar=500
    ax.add_patch(Rectangle((x0,y0),bar,54,fc="white",ec=INK,lw=1.0,zorder=9))
    ax.add_patch(Rectangle((x0,y0),bar/2,54,fc=INK,ec=INK,lw=1.0,zorder=9))
    ax.text(x0+bar/2,y0+150,"500 m",fontsize=9.5,color=INK,ha="center",
            family="TeX Gyre Heros",zorder=9,path_effects=halo)
    nx=crop[1]-230; ny=crop[2]+175
    ax.annotate("",xy=(nx,ny+430),xytext=(nx,ny),
        arrowprops=dict(arrowstyle="-|>",color=INK,lw=2.0,
        path_effects=[pe.withStroke(linewidth=3.6,foreground="white")]),zorder=9)
    ax.text(nx,ny+470,"N",fontsize=11,color=INK,ha="center",va="bottom",
            family="TeX Gyre Heros",weight="bold",zorder=9,path_effects=halo)
    ax.set_xlim(crop[0],crop[1]); ax.set_ylim(crop[2],crop[3])
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_color(INK); sp.set_linewidth(1.4)
    fig.savefig(f"{OUT}/{fname}",dpi=300,facecolor=PAPER); plt.close(fig)
    print("wrote",fname)

panel("pre","lt_panel_pre.png")
panel("flood","lt_panel_flood.png")

# ---- cross-section, light ----
npz=np.load(f"{ROOT}/data/processed/cross_section_profile.npz")
dist,elev=npz["dist"],npz["elev"]
GZ=48.52; PEAK=GZ+8.91
fig=plt.figure(figsize=(14.0,2.22)); ax=fig.add_axes([0.045,0.185,0.945,0.765])
fig.patch.set_facecolor(PAPER); ax.set_facecolor(PAPER)
ax.fill_between(dist,elev,PEAK,where=(elev<=PEAK),color=FLOOD,alpha=0.30,zorder=2)
ax.fill_between(dist,elev,42.5,color="#EDE3D0",zorder=1)
ax.plot(dist,elev,color=INK,linewidth=2.1,zorder=4)
ax.axhline(PEAK,color=FLOOD,linestyle="--",linewidth=1.7,zorder=5)
ax.axhline(GZ,color=WATER,linestyle=":",linewidth=1.4,zorder=3)
ax.text(dist.min()+12,PEAK+2.0,"891 cm FLOOD PEAK  ·  57.43 m",color=FLOOD,
        fontsize=11.5,family="TeX Gyre Heros",weight="bold",va="bottom")
ax.text(dist.min()+12,GZ-1.7,"gauge zero  48.52 m",color=WATER,fontsize=9.5,
        family="TeX Gyre Heros",ha="left",va="top")
ax.annotate("SOUTH BANK — the 1586 fort chose this side",xy=(-395,89),xytext=(-330,72),
    color=OCHRE,fontsize=10.5,family="TeX Gyre Heros",weight="bold",
    arrowprops=dict(arrowstyle="-",color=OCHRE,lw=1.1))
ax.annotate("NORTH BANK — terrace, embankment, “second tier”",xy=(250,61.5),
    xytext=(105,78),color=WATER,fontsize=10.5,family="TeX Gyre Heros",weight="bold",
    arrowprops=dict(arrowstyle="-",color=WATER,lw=1.1))
ax.set_xlim(dist.min(),dist.max()); ax.set_ylim(42.5,96)
ax.set_xlabel("metres from channel centreline        south ←   → north",color=INK,
              fontsize=10,family="TeX Gyre Heros",labelpad=3)
ax.set_ylabel("m a.s.l.",color=INK,fontsize=10,family="TeX Gyre Heros")
ax.tick_params(colors=INK,labelsize=9)
for sp in ax.spines.values(): sp.set_color(RULE)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.grid(color=RULE,alpha=0.55,linewidth=0.6)
for l in ax.get_xticklabels()+ax.get_yticklabels(): l.set_family("TeX Gyre Heros")
fig.savefig(f"{OUT}/lt_xsection.png",dpi=300,facecolor=PAPER); plt.close(fig)
print("wrote lt_xsection.png")
