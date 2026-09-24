import os
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=os.getcwd(); OUT=f"{ROOT}/poster/assets"
PAPER="#FBF7EF"; INK="#22303A"; TEAL="#0E7C86"; FLOOD="#C7432A"; OCHRE="#A9761F"; TAN="#E4D8BF"

# ---- square crops for circular framing ----
def square(src,dst,top_frac=0.06):
    im=Image.open(src).convert("RGB"); w,h=im.size
    top=int(h*top_frac); box=(0,top,w,top+w)
    if box[3]>h: box=(0,h-w,w,h)
    im.crop(box).save(dst); print("wrote",os.path.basename(dst),im.crop(box).size)

square(f"{OUT}/lt_panel_flood.png", f"{OUT}/sq_flood.png", 0.02)
square(f"{OUT}/lt_panel_pre.png",   f"{OUT}/sq_pre.png",   0.02)

# ---- long profile as a light PNG (for tools that can't take SVG) ----
stops=[("SOURCE · MIDDLE URALS",370),("TYUMEN",48.52),("TURA MOUTH",42.2),
       ("TOBOLSK",32),("KHANTY-MANSIYSK",20),("KARA SEA",0)]
xs=[0.085,0.27,0.45,0.625,0.79,0.925]
ys=[s[1] for s in stops]
fig=plt.figure(figsize=(13,3.0)); ax=fig.add_axes([0.02,0.16,0.96,0.72])
fig.patch.set_facecolor(PAPER); ax.set_facecolor(PAPER)
ax.fill_between(xs,ys,0,color=TEAL,alpha=0.16)
ax.plot(xs,ys,color=TEAL,lw=3.0)
ax.axhspan(-28,0,color=TAN)
for x,(nm,el) in zip(xs,stops):
    ax.plot([x,x],[el,-28],color="#C9BBA4",lw=1)
    ax.text(x,-46,nm,ha="center",va="top",fontsize=11,family="TeX Gyre Heros",color=INK)
    ax.text(x,-80,f"{el:g} m",ha="center",va="top",fontsize=11,family="DejaVu Sans Mono",color=INK)
ax.plot(xs[1],ys[1],"o",ms=13,color=FLOOD,zorder=6)
ax.text(xs[1],-46,"TYUMEN",ha="center",va="top",fontsize=11,family="TeX Gyre Heros",
        color=FLOOD,weight="bold")
ax.annotate("",xy=(0.92,215),xytext=(0.30,215),
            arrowprops=dict(arrowstyle="-",color=OCHRE,lw=1.4,ls=(0,(5,4))))
ax.text(0.61,232,"from Tyumen: the whole Tobol, Irtysh and Ob still ahead — and only 48.5 m of descent left",
        ha="center",fontsize=12,color=OCHRE,family="TeX Gyre Heros")
for x0,x1,lab in [(0.05,0.44,"TURA · 1,030 km"),(0.44,0.62,"TOBOL · 1,591 km"),
                  (0.62,0.79,"IRTYSH · 4,248 km"),(0.79,0.935,"OB · 3,700 km")]:
    ax.text((x0+x1)/2,120,lab,ha="center",fontsize=11,family="DejaVu Sans Mono",color="#6D7C85")
ax.set_xlim(-0.02,1.02); ax.set_ylim(-95,270); ax.axis("off")
fig.savefig(f"{OUT}/lt_profile.png",dpi=300,facecolor=PAPER,transparent=False)
print("wrote lt_profile.png")
