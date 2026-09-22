import os, json
import numpy as np
import rasterio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape, LineString, Point
from shapely.ops import unary_union, split
import shapely

ROOT = os.getcwd()

with rasterio.open(f"{ROOT}/data/processed/mndwi_20260618.tif") as src:
    transform = src.transform
    crs = src.crs
    shape_ = src.shape

npz = np.load(f"{ROOT}/data/processed/water_masks_dem_constrained.npz")
pre_water = npz["pre_water"]
flood_water = npz["flood_water"]

def polygonize(mask, transform, crs, min_area_m2=500):
    polys = []
    for geom, val in shapes(mask.astype(np.uint8), mask=mask, transform=transform):
        g = shape(geom)
        if g.area >= min_area_m2:
            polys.append(g)
    gdf = gpd.GeoDataFrame(geometry=polys, crs=crs)
    return gdf

pre_gdf = polygonize(pre_water, transform, crs)
flood_gdf = polygonize(flood_water, transform, crs)
print("pre polygons:", len(pre_gdf), "flood polygons:", len(flood_gdf))

pre_union = unary_union(pre_gdf.geometry)
flood_union = unary_union(flood_gdf.geometry)

# new inundated area = flood extent minus the permanent (pre-flood) river channel
new_inundation = flood_union.difference(pre_union.buffer(10))
gpd.GeoDataFrame(geometry=[flood_union], crs=crs).to_file(f"{ROOT}/data/processed/flood_extent_20260729.geojson", driver="GeoJSON")
gpd.GeoDataFrame(geometry=[pre_union], crs=crs).to_file(f"{ROOT}/data/processed/river_extent_20260618.geojson", driver="GeoJSON")
gpd.GeoDataFrame(geometry=[new_inundation], crs=crs).to_file(f"{ROOT}/data/processed/new_inundation_20260729.geojson", driver="GeoJSON")

print("flood_union area ha:", flood_union.area/10000)
print("pre_union area ha:", pre_union.area/10000)
print("new_inundation area ha:", new_inundation.area/10000)

# --- load OSM data, reproject to same CRS ---
lines = gpd.read_file(f"{ROOT}/data/raw/osm_tyumen_extract.osm", layer="lines").to_crs(crs)
mp = gpd.read_file(f"{ROOT}/data/raw/osm_tyumen_extract.osm", layer="multipolygons").to_crs(crs)

river_line = lines[lines["waterway"] == "river"]
river_geom = unary_union(river_line.geometry)
print("river line length m:", river_geom.length)

# Build a long north/south dividing line by extending the river centerline
# (approximated as a straight line through its endpoints, since the reach is
# fairly straight through the historic centre) far beyond the raster extent.
coords = list(river_geom.coords) if river_geom.geom_type == "LineString" else list(list(river_geom.geoms)[0].coords)
x0, y0 = coords[0]
x1, y1 = coords[-1]
dx, dy = x1 - x0, y1 - y0
length = (dx**2 + dy**2) ** 0.5
ux, uy = dx / length, dy / length
ext = 5000
divider = LineString([(x0 - ux*ext, y0 - uy*ext), (x1 + ux*ext, y1 + uy*ext)])
gpd.GeoDataFrame(geometry=[divider], crs=crs).to_file(f"{ROOT}/data/processed/ns_divider.geojson", driver="GeoJSON")

# side test using cross product sign relative to divider direction
def side_of_line(geom, x0, y0, ux, uy):
    c = geom.centroid
    vx, vy = c.x - x0, c.y - y0
    cross = ux*vy - uy*vx
    return "north" if cross > 0 else "south"
# NOTE: sign convention checked below against known south-bank historic centre point

buildings = mp[mp["building"].notna()].copy()
buildings["side"] = buildings.geometry.apply(lambda g: side_of_line(g, x0, y0, ux, uy))

roads = lines[lines["highway"].notna()].copy()
roads["side"] = roads.geometry.apply(lambda g: side_of_line(g, x0, y0, ux, uy))

# sanity check: historic centre / kremlin area (south bank, high bluff) should be "south"
# Tyumen kremlin ~ 57.1539N 65.5333E
check_pt = gpd.GeoSeries([Point(65.5333, 57.1539)], crs="EPSG:4326").to_crs(crs).iloc[0]
print("historic centre side:", side_of_line(check_pt, x0, y0, ux, uy))

flood_gdf_all = gpd.GeoDataFrame(geometry=[flood_union], crs=crs)

buildings_flooded = buildings[buildings.intersects(flood_union)]
roads_flooded = roads[roads.intersects(flood_union)]

print("\n--- EXPOSURE COUNTS ---")
print("buildings total:", len(buildings), "flooded:", len(buildings_flooded))
for s in ["north", "south"]:
    tot = (buildings["side"] == s).sum()
    fl = (buildings_flooded["side"] == s).sum()
    print(f"  buildings {s}: total={tot} flooded={fl}")

roads_flooded_len = roads_flooded.length.sum()
print("roads flooded count:", len(roads_flooded), "length km:", roads_flooded_len/1000)
for s in ["north", "south"]:
    sub = roads_flooded[roads_flooded["side"] == s]
    print(f"  roads {s}: count={len(sub)} length_km={sub.length.sum()/1000:.2f}")

buildings.to_file(f"{ROOT}/data/processed/buildings.geojson", driver="GeoJSON")
roads.to_file(f"{ROOT}/data/processed/roads.geojson", driver="GeoJSON")
buildings_flooded.to_file(f"{ROOT}/data/processed/buildings_flooded.geojson", driver="GeoJSON")
roads_flooded.to_file(f"{ROOT}/data/processed/roads_flooded.geojson", driver="GeoJSON")

# export flood polygon split by side for WorldPop queries
flood_north = flood_union.intersection(shapely.geometry.Polygon(
    [(x0-ux*ext-uy*ext*0, y0-uy*ext, ), ]) ) if False else None

# simpler: buffer divider into two half-plane polygons using a big box split
from shapely.geometry import box
minx, miny, maxx, maxy = flood_union.bounds
pad = 2000
bbox = box(minx-pad, miny-pad, maxx+pad, maxy+pad)
divider_line_for_split = LineString([(x0 - ux*ext - uy*ext, y0 - uy*ext + ux*ext), (x1 + ux*ext - uy*ext, y1 + uy*ext + ux*ext)])
# use simple normal-offset approach instead: classify by side function via fine polygon split
try:
    pieces = split(bbox, divider)
    polys = list(pieces.geoms)
    p_north = [p for p in polys if side_of_line(p, x0, y0, ux, uy) == "north"]
    p_south = [p for p in polys if side_of_line(p, x0, y0, ux, uy) == "south"]
    north_half = unary_union(p_north)
    south_half = unary_union(p_south)
    flood_north = flood_union.intersection(north_half)
    flood_south = flood_union.intersection(south_half)
    print("flood north ha:", flood_north.area/10000, "flood south ha:", flood_south.area/10000)
    gpd.GeoDataFrame(geometry=[flood_north], crs=crs).to_file(f"{ROOT}/data/processed/flood_north.geojson", driver="GeoJSON")
    gpd.GeoDataFrame(geometry=[flood_south], crs=crs).to_file(f"{ROOT}/data/processed/flood_south.geojson", driver="GeoJSON")
except Exception as e:
    print("split failed:", e)

summary = {
    "flood_extent_ha": flood_union.area/10000,
    "pre_flood_water_ha": pre_union.area/10000,
    "new_inundation_ha": new_inundation.area/10000,
    "buildings_total": int(len(buildings)),
    "buildings_flooded_total": int(len(buildings_flooded)),
    "buildings_flooded_north": int((buildings_flooded["side"]=="north").sum()),
    "buildings_flooded_south": int((buildings_flooded["side"]=="south").sum()),
    "buildings_total_north": int((buildings["side"]=="north").sum()),
    "buildings_total_south": int((buildings["side"]=="south").sum()),
    "roads_flooded_length_km": float(roads_flooded_len/1000),
    "roads_flooded_length_km_north": float(roads_flooded[roads_flooded['side']=='north'].length.sum()/1000),
    "roads_flooded_length_km_south": float(roads_flooded[roads_flooded['side']=='south'].length.sum()/1000),
}
with open(f"{ROOT}/data/processed/exposure_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print(json.dumps(summary, indent=2))
