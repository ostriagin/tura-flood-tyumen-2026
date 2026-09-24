"""
extract_transects.py
--------------------
Extracts two terrain cross-sections from Copernicus DEM GLO-30, using one
identical sampling routine so that the two profiles are directly comparable:

  1. Tura at Tyumen, western Siberia   (tile N57_00_E065_00)
  2. Severn at Shrewsbury, England     (tile N52_00_W003_00)

Both transects are 900 m long, sampled at 5 m spacing (181 points) by bilinear
interpolation, centred on the DEM channel minimum, and oriented so that
negative distance runs towards the historic core of the town and positive
distance towards the low-lying district on the opposite bank.

The Copernicus DEM is a *surface* model: over built-up ground the returned
elevation is the top of buildings and trees, not the bare earth. This is stated
in the report and on the poster, and is the reason no inundation depth is
modelled for Shrewsbury here.

Tiles are public and unauthenticated:
  https://copernicus-dem-30m.s3.amazonaws.com/<NAME>/<NAME>.tif

Usage:
  python scripts/extract_transects.py            # both, if both tiles present
"""

import json
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "processed")

M_PER_DEG_LAT = 111320.0


def bilinear_profile(tif_path, lat0, lon0, u_east, u_north,
                     half_length_m=450.0, step_m=5.0):
    """Sample a straight transect from a geographic (EPSG:4326) DEM.

    lat0, lon0    centre of the transect
    u_east,u_north  unit vector, in metres, for the +distance direction
    """
    import rasterio

    dist = np.arange(-half_length_m, half_length_m + step_m / 2, step_m)
    m_per_deg_lon = M_PER_DEG_LAT * np.cos(np.deg2rad(lat0))
    lat = lat0 + dist * u_north / M_PER_DEG_LAT
    lon = lon0 + dist * u_east / m_per_deg_lon

    with rasterio.open(tif_path) as src:
        t = src.transform
        # fractional pixel coordinates
        fc = (lon - t.c) / t.a
        fr = (lat - t.f) / t.e
        r0 = np.floor(fr).astype(int)
        c0 = np.floor(fc).astype(int)
        dr = fr - r0
        dc = fc - c0
        band = src.read(1)

        def at(rr, cc):
            rr = np.clip(rr, 0, band.shape[0] - 1)
            cc = np.clip(cc, 0, band.shape[1] - 1)
            return band[rr, cc].astype(float)

        elev = (at(r0, c0) * (1 - dr) * (1 - dc)
                + at(r0, c0 + 1) * (1 - dr) * dc
                + at(r0 + 1, c0) * dr * (1 - dc)
                + at(r0 + 1, c0 + 1) * dr * dc)

    return dist, elev.astype("float32"), lat, lon


# ---------------------------------------------------------------- Tyumen ----
# The transect runs due north-south through the historic centre, crossing the
# Tura at the Tyumen gauge. Negative = south bank (the 1586 fort bluff),
# positive = north bank (the low terrace).
TYUMEN = dict(
    tile="Copernicus_DSM_COG_10_N57_00_E065_00_DEM.tif",
    lat0=57.161589, lon0=65.534900,
    u_east=0.0, u_north=1.0,
    out="cross_section_profile_v2.npz",
    gauge_zero=48.52,
    flood_level=57.43,          # 891 cm on the Tyumen gauge, 31 July 2026
)

# ------------------------------------------------------------ Shrewsbury ----
# The transect runs NW-SE across the Severn at the Welsh Bridge.
# Negative = SE, into the medieval town inside the meander (high ground).
# Positive = NW, into Frankwell, outside the meander (low ground).
SHREWSBURY = dict(
    tile="Copernicus_DSM_COG_10_N52_00_W003_00_DEM.tif",
    lat0=52.710271, lon0=-2.755777,
    u_east=-0.8860, u_north=0.4634,
    out="shrewsbury_cross_section_profile.npz",
    gauge_zero=47.00,           # Welsh Bridge gaugeboard datum, m AOD
    flood_level=52.25,          # 5.25 m gauge, 1 November 2000
    highest_known=52.70,        # 5.70 m gauge, 1795
)


def run(spec):
    path = os.path.join(RAW, spec["tile"])
    if not os.path.exists(path):
        print(f"SKIP {spec['out']}: tile not present at {path}")
        return None
    dist, elev, lat, lon = bilinear_profile(
        path, spec["lat0"], spec["lon0"], spec["u_east"], spec["u_north"])
    np.savez(os.path.join(OUT, spec["out"]),
             dist=dist, elev=elev, lat=lat, lon=lon)
    base = float(elev.min())
    hi = elev[dist <= -150]
    lo = elev[dist >= 150]
    print(f"{spec['out']}")
    print(f"  channel minimum           {base:6.2f} m")
    print(f"  historic core, mean above channel   {hi.mean() - base:5.1f} m")
    print(f"  low-bank district, mean above       {lo.mean() - base:5.1f} m")
    return dict(channel=base, high=float(hi.mean() - base),
                low=float(lo.mean() - base))


if __name__ == "__main__":
    summary = {}
    for name, spec in (("tyumen", TYUMEN), ("shrewsbury", SHREWSBURY)):
        r = run(spec)
        if r:
            summary[name] = r
    if summary:
        # great-circle separation of the two study sites
        la1, lo1 = np.deg2rad([TYUMEN["lat0"], TYUMEN["lon0"]])
        la2, lo2 = np.deg2rad([SHREWSBURY["lat0"], SHREWSBURY["lon0"]])
        d = 2 * np.arcsin(np.sqrt(np.sin((la2 - la1) / 2) ** 2
                                  + np.cos(la1) * np.cos(la2)
                                  * np.sin((lo2 - lo1) / 2) ** 2))
        summary["separation_km"] = round(float(d * 6371.0), 0)
        print("\nsite separation: %.0f km" % summary["separation_km"])
        json.dump(summary, open(os.path.join(OUT, "transect_comparison.json"), "w"),
                  indent=2)
