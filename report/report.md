---
title: "Does the 1586 siting of Tyumen still determine which bank of the Tura floods?"
subtitle: "A Sentinel-2 flood-extent analysis of the July 2026 Tura flood"
author: "Sasha Ostriagin"
date: "September 2026"
geometry: margin=2.2cm
fontsize: 11pt
papersize: a4
---

## Research question

In 1586, Tyumen was founded as a Russian fort on the high, steep southern bank of the Tura river, while the low northern bank was left undeveloped. Four centuries later, in July 2026, the Tura flooded to a record level of 891 cm on the city gauge — a level exceeding the entire prior observation history — and a state of emergency was declared. The flood reached and, in places, overtopped a "second tier" of the city on the north bank that residents describe as never having flooded before. This raises a question that sits at the intersection of historical geography and hydrology: does the 1586 siting decision — placing the city on the defensible high bank — still determine which side of the river floods today, or has the record 2026 event shown that the old siting logic only holds up to a threshold, beyond which even the historically "safe" pattern of exposure breaks down? This report uses Sentinel-2 optical imagery, a global DEM and OpenStreetMap data to map the flood extent, quantify exposure on each bank, and test this question against a real, recent, catastrophic event.

## Study area

Tyumen (57.15°N, 65.53°E) is the oldest Russian city in Siberia, sited on the Tura river, a right-bank tributary of the Tobol (itself a tributary of the Irtysh, which joins the Ob and drains to the Kara Sea). The historic centre and kremlin sit on a steep bluff on the south bank, rising roughly 30–40 m above the river within a few hundred metres; the north bank is a much gentler terrace, historically the site of docks, industry and, more recently, a landscaped embankment and residential development, including the "second tier" (вторая надпойменная терраса) referred to locally, an area of the city built above the first, lower terrace and popularly understood to lie above the reach of ordinary floods.

In July 2026, sustained rainfall and upstream snowmelt runoff drove the Tura to a record level. The city gauge, whose zero corresponds to 48.52 m above sea level in the Baltic height system, read 891 cm at its peak on 31 July 2026 — equivalent to 57.43 m a.s.l. — comfortably the highest level in the gauge's observation history. A state of emergency was declared, the new embankment was overtopped, and volunteers (including the author) filled sandbags on the north bank over two days as water encroached on residential streets above the normal floodplain.

## Data and method

**Imagery.** Two Sentinel-2 L2A (surface reflectance) scenes covering MGRS tile T41VPD (UTM zone 41N, EPSG:32641) were obtained from the Copernicus Data Space Ecosystem via the Copernicus Browser: a cloud-free pre-flood scene from **18 June 2026** and a flood-peak scene from **29 July 2026** (two days before the 31 July gauge maximum, the closest available cloud-free Sentinel-2 pass to the peak). Bands B02 (blue), B03 (green), B04 (red) and B11 (SWIR1, resampled to 10 m) were exported for both dates, co-registered on an identical grid (535 × 1599 pixels, ~5 m pixel spacing after the browser's resampling, bounds 652,040–654,950 mE, 6,333,099–6,341,879 mN).

**Water index.** For each date, the Modified Normalised Difference Water Index was computed as

MNDWI = (B3 − B11) / (B3 + B11)

Water has high green reflectance and strongly absorbs SWIR, giving MNDWI values that are strongly positive over open water and negative over vegetation, soil and impervious surfaces.

**Masking.** A fixed threshold of MNDWI > 0 — the standard literature default — correctly picked out the permanent river channel in the 18 June scene, but badly under-estimated flooding in the 29 July scene: a first pass found the flooded-pixel count only ~4.5% higher than the pre-flood baseline, contradicted by clear visual widening of the river in the true-colour preview. Sampling band values directly along the cross-section transect showed why: at the historic-centre reach, visible-band reflectance dropped 4–5× between the two dates while SWIR reflectance stayed comparable — the signature of cloud shadow, not open water, suppressing MNDWI. Two conventional fixes were tried and rejected: Otsu automatic thresholding classified large parts of the built-up city as "water" (the reflectance distribution is not bimodal in an urban scene), and a naive region-growing/connected-component approach on a lower threshold leaked through shadowed streets and dark rooftops across the whole city while still failing to recover the true flooded area near the gauge.

The method finally adopted constrains the *spectral* water mask with a *topographic* one, using the Copernicus DEM GLO-30 (30 m, reprojected to the Sentinel-2 grid by bilinear resampling): a pixel is classed as water only if (i) its MNDWI exceeds a permissive threshold (−0.15 for the pre-flood date, −0.35 for the flood date, to tolerate shadow-suppressed values), (ii) its DEM elevation is below a hydrologically plausible cut-off (53 m a.s.l. for the pre-flood channel; 58.9 m a.s.l., i.e. the observed peak plus 1.5 m freeboard, for the flood date), and (iii) it is spatially connected, through other qualifying pixels, to a strict high-confidence seed (MNDWI > 0.05 pre-flood, > −0.05 flood) — implemented as 3×3 morphological opening followed by connected-component labelling in `scipy.ndimage`. This removes dark, low-elevation, but hydrologically disconnected false positives (shadowed roofs on distant blocks) while keeping genuine flood water that is spectrally weak but topographically and spatially consistent with the river. The resulting masks were polygonised in Python (`rasterio.features.shapes` + `geopandas`), which is functionally equivalent to raster-to-vector conversion and MNDWI band-math in QGIS; the QGIS project supplied with this report reproduces the same layers for inspection.

**Elevation profile.** A 900 m cross-section (450 m either side of the river centreline), perpendicular to the river and passing through the point on the channel nearest the gauge (57.1619°N, 65.5349°E), was sampled from the DEM at 5 m intervals.

**Exposure.** Buildings and roads were extracted from OpenStreetMap via the Overpass API (bounding box 65.50–65.56°E, 57.14–57.17°N; 5,153 building polygons, full road network). A north/south dividing line was constructed from the local tangent of the OSM river centreline at the gauge, calibrated against the known south-bank location of the Tyumen kremlin. Buildings and road segments intersecting the flood polygon were counted on each side. Population exposure was queried directly from the WorldPop Global Project Population Data (unconstrained, 2020, 100 m resolution) REST API for the flooded area on each bank, split into administrable sub-polygons.

All processing (band math, masking, polygonisation, cross-section extraction, exposure counting) is implemented as Python scripts using `rasterio`, `geopandas`, `shapely`, `scipy.ndimage` and `matplotlib`, included in the accompanying repository; the pipeline is designed so that the whole analysis can be re-run from the raw Sentinel-2 exports, the DEM tile and the OSM extract.

## Results

**Flood extent.** Figure 1 shows the pre-flood and flood-peak scenes with the derived water masks overlaid. The pre-flood channel covers 137.4 ha (including the meander lake north of the historic centre); the flood-peak extent covers 415.0 ha, of which 280.8 ha (68%) is newly inundated land beyond the permanent channel. The flood clearly spreads much further, and into denser built fabric, north of the river than south of it (Figure 1; Figure 3).

![Figure 1. Sentinel-2 true-colour composites (B04/B03/B02) for Tyumen, 18 June 2026 (pre-flood, left) and 29 July 2026 (flood peak, right), with the permanent river channel (cyan) and 29 July flood extent (orange) derived in this report overlaid, and the north/south dividing line (yellow dashed) used for exposure counts. Source: Sentinel-2 L2A, Copernicus Data Space Ecosystem / Copernicus Browser; author's analysis.](../figures/fig1_flood_extent.png)

**Cross-section.** Figure 2 shows the DEM elevation profile through the historic centre, perpendicular to the river, with the 891 cm gauge peak (57.43 m a.s.l.) ruled across it. The channel bed sits at approximately 48–50 m a.s.l., consistent with the gauge datum (zero = 48.52 m). The south bank rises steeply, reaching roughly 90 m within about 400 m of the channel — a genuine bluff, and the site the 1586 fort occupied. The north bank is far gentler: it climbs to only 59–63 m across the same distance, and at several points along the wider terrace it sits only 1–3 m above the 891 cm flood line. The flood line intersects roughly 515 m of the transect, almost all of it on the low north-bank side.

![Figure 2. Terrain cross-section perpendicular to the Tura through the historic centre, with the 31 July 2026 flood peak (891 cm gauge reading = 57.43 m a.s.l.) ruled across it. Source: Copernicus DEM GLO-30; author's analysis.](../figures/fig2_cross_section.png)

**Exposure.** Table 1 summarises exposure by bank (also Figure 3).

| | North bank | South bank |
|---|---:|---:|
| Flood extent | 391.2 ha | 23.9 ha |
| Buildings (total, OSM) | 716 | 4,437 |
| Buildings flooded | 120 (16.8%) | 18 (0.4%) |
| Roads flooded | 39.8 km | 11.4 km |
| Population exposed (WorldPop 2020) | ≈5,080 | ≈560 |

*Table 1. Flood exposure by bank, 29 July 2026. Sources: buildings and roads, OpenStreetMap contributors (via Overpass API); population, WorldPop Global Project Population Data (unconstrained, 2020, 100 m); flood extent, author's analysis (see Data and method).*

![Figure 3. Flood exposure by bank: buildings flooded (of total), flooded road length, and flood-extent area. Source: author's analysis, OpenStreetMap contributors, WorldPop.](../figures/fig3_exposure.png)

Despite the south bank holding six times more buildings overall (the historic centre and most of the modern city), the north bank's flooded area is over sixteen times larger, its share of buildings flooded is around forty times higher, and its estimated exposed population is roughly nine times greater. This is a striking, consistent result across every exposure metric, and it is exactly what the 1586 siting decision — high south bank for the city, low north bank left as floodplain — would predict, 440 years later.

**The second-tier question.** The cross-section shows why the story is not simply "north floods, south doesn't." Along much of the transect the north-bank terrace sits several metres above the flood line and stays dry; the flooded fraction of the north bank's buildings (16.8%) is high in relative terms but the majority of the terrace was not inundated. But where the terrace elevation drops to within 1–3 m of the flood line, as it does at several points in the cross-section and in the newly-inundated blocks visible in Figure 1, the record 891 cm event was enough to cross it. That is consistent with local reports that the "second tier" flooded for the first time in living memory: the old siting logic (south = safe, north = exposed) is not a strict binary but a *threshold* relationship — the north bank has always been closer to the water table of risk, and a flood large enough (record by a wide margin) pushed part of the terrace that had previously stayed just above that threshold below it.

## Limitations

Several limitations affect the precision, though not the overall direction, of these results. First, the MNDWI/DEM masking approach, while it corrects for the worst shadow contamination, will still under-count water under vegetation canopy or in deep shadow that also falls below the elevation cut-off, and it may over-count very shallow, disconnected wet ground picked up by the permissive threshold; the 3–4% area change introduced by geometry simplification for the WorldPop population query is a further, quantified source of imprecision. Second, all Sentinel-2 bands used here are natively 10–20 m resolution (B11 resampled from 20 m); a single pixel can straddle a real flood boundary, and small buildings or short road segments near the edge of the flood extent may be mis-classified as flooded or dry. Third, and most importantly, the 29 July scene is a single satellite overpass, two days before the 31 July gauge maximum — it captures the flood in an advanced state but not the true observed peak, so the mapped extent in this report is very likely a conservative (smaller) estimate of the maximum flooded area and exposure reported here should be read as a lower bound on the 891 cm event. Cloud cover prevented a cloud-free Sentinel-2 acquisition any closer to the peak; Sentinel-1 SAR, which is unaffected by cloud, is available as a fallback for a future, closer-to-peak extent map but was not required for this analysis given the acceptable quality of the 29 July optical scene. Finally, the north/south divide is a straight line derived from the local river tangent, a simplification of the Tura's actual meandering course, which will slightly misclassify buildings and roads very close to the river itself.

## Implications

The results support the research question's premise directly: 440 years after Tyumen's founders chose the defensible high south bank for their fort, the same asymmetry — steep, high south bank; gentle, low north bank — still structures almost the entire pattern of flood exposure in the city, visible in the DEM cross-section, the satellite-derived flood extent, and every exposure metric computed here. That is a genuinely long-lived piece of historical-geographical path dependency: a sixteenth-century military siting decision continues, via the terrain it exploited, to sort twenty-first-century flood risk.

But the 2026 event complicates a simple reading of that thesis. The north-bank "second tier," built and occupied on the understanding that it sat safely above the floodplain, was inundated for what residents describe as the first time — not because the old geography stopped mattering, but because a record flood, exceeding the entire prior observation history, was large enough to cross a threshold that smaller floods never reached. The 1586 siting logic is best understood not as a fixed boundary between a flooded bank and a safe one, but as a gradient of exposure keyed to elevation above the channel — one that held reliably for four centuries of ordinary floods and one exceptional event large enough to expose its limit. As climate and hydrological conditions change the frequency of such record events, the practical safety margin the north bank's terrace has long provided may need to be reassessed rather than assumed.
