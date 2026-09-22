import os, uuid, json
import geopandas as gpd
import rasterio

ROOT = os.getcwd()
QGIS_DIR = f"{ROOT}/qgis"
os.makedirs(QGIS_DIR, exist_ok=True)

def vector_layer_xml(path, name, layer_id, geomtype):
    gdf = gpd.read_file(path)
    minx, miny, maxx, maxy = gdf.total_bounds
    crs_authid = gdf.crs.to_string()  # e.g. EPSG:32641
    rel = os.path.relpath(path, QGIS_DIR)
    return f'''    <maplayer type="vector" geometry="{geomtype}" hasScaleBasedVisibilityFlag="0" autoRefreshTime="0" autoRefreshEnabled="0" refreshOnNotifyEnabled="0" simplifyMaxScale="1" simplifyDrawingHints="1" simplifyLocal="1" labelsEnabled="0" simplifyAlgorithm="0" symbologyReferenceScale="-1" simplifyDrawingTol="1" styleCategories="AllStyleCategories" minScale="100000000" maxScale="0" wkbType="{geomtype}">
      <extent>
        <xmin>{minx}</xmin>
        <ymin>{miny}</ymin>
        <xmax>{maxx}</xmax>
        <ymax>{maxy}</ymax>
      </extent>
      <id>{layer_id}</id>
      <datasource>./{rel}</datasource>
      <layername>{name}</layername>
      <srs>
        <spatialrefsys>
          <authid>{crs_authid}</authid>
        </spatialrefsys>
      </srs>
      <provider encoding="UTF-8">ogr</provider>
    </maplayer>
'''

def raster_layer_xml(path, name, layer_id):
    with rasterio.open(path) as s:
        b = s.bounds
        crs_authid = s.crs.to_string()
    rel = os.path.relpath(path, QGIS_DIR)
    return f'''    <maplayer type="raster" hasScaleBasedVisibilityFlag="0" autoRefreshTime="0" autoRefreshEnabled="0" refreshOnNotifyEnabled="0" styleCategories="AllStyleCategories" minScale="1e+08" maxScale="0">
      <extent>
        <xmin>{b.left}</xmin>
        <ymin>{b.bottom}</ymin>
        <xmax>{b.right}</xmax>
        <ymax>{b.top}</ymax>
      </extent>
      <id>{layer_id}</id>
      <datasource>./{rel}</datasource>
      <layername>{name}</layername>
      <srs>
        <spatialrefsys>
          <authid>{crs_authid}</authid>
        </spatialrefsys>
      </srs>
      <provider>gdal</provider>
    </maplayer>
'''

layers = [
    ("vector", f"{ROOT}/data/processed/flood_extent_20260729.geojson", "Flood extent 29 Jul 2026", "Polygon"),
    ("vector", f"{ROOT}/data/processed/river_extent_20260618.geojson", "River extent 18 Jun 2026 (pre-flood)", "Polygon"),
    ("vector", f"{ROOT}/data/processed/new_inundation_20260729.geojson", "New inundation (flood minus pre-flood river)", "Polygon"),
    ("vector", f"{ROOT}/data/processed/buildings_flooded.geojson", "Buildings flooded", "Polygon"),
    ("vector", f"{ROOT}/data/processed/buildings.geojson", "Buildings (all, OSM)", "Polygon"),
    ("vector", f"{ROOT}/data/processed/roads_flooded.geojson", "Roads flooded", "LineString"),
    ("vector", f"{ROOT}/data/processed/roads.geojson", "Roads (all, OSM)", "LineString"),
    ("vector", f"{ROOT}/data/processed/ns_divider.geojson", "North/south divider (river axis)", "LineString"),
    ("raster", f"{ROOT}/data/processed/mndwi_20260618.tif", "MNDWI 18 Jun 2026 (pre-flood)", None),
    ("raster", f"{ROOT}/data/processed/mndwi_20260729.tif", "MNDWI 29 Jul 2026 (flood peak)", None),
]

layer_xmls = []
layer_ids = []
layertree_entries = []
for kind, path, name, geomtype in layers:
    if not os.path.exists(path):
        print("SKIP missing", path); continue
    lid = f"{name.replace(' ','_').replace('(','').replace(')','').replace('/','_')}_{uuid.uuid4().hex[:8]}"
    layer_ids.append((lid, name))
    if kind == "vector":
        layer_xmls.append(vector_layer_xml(path, name, lid, geomtype))
    else:
        layer_xmls.append(raster_layer_xml(path, name, lid))
    layertree_entries.append(f'      <layer-tree-layer expanded="1" providerKey="{"ogr" if kind=="vector" else "gdal"}" checked="Qt::Checked" name="{name}" id="{lid}"/>')

qgs = f'''<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis projectname="Tura flood at Tyumen, July 2026" version="3.34.0">
  <homePath path=""/>
  <title>Tura flood at Tyumen — July 2026 (RGS Young Geographer project)</title>
  <projectCrs>
    <spatialrefsys>
      <authid>EPSG:32641</authid>
    </spatialrefsys>
  </projectCrs>
  <layer-tree-group>
{chr(10).join(layertree_entries)}
  </layer-tree-group>
  <projectlayers>
{chr(10).join(layer_xmls)}
  </projectlayers>
</qgis>
'''

with open(f"{QGIS_DIR}/tura_flood_tyumen.qgs", "w") as f:
    f.write(qgs)
print("wrote qgis project with", len(layer_ids), "layers")
