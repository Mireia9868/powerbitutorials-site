---
title: "Power BI Map Visuals: Choosing the Right One"
description: "Power BI ships with several map visuals, and they are not interchangeable."
pubDate: 2026-10-13
category: visualization
tags: ["maps", "visualization"]
difficulty: Beginner
author: Mireia
featured: false
draft: false
---

Power BI ships with several map visuals, and they are not interchangeable. Picking the wrong one produces a report that either misleads the reader, renders blank tiles, or silently aggregates your data into a shape nobody asked for. This article walks through the map visuals available in the standard Power BI visuals pane, explains what each one is actually good at, and shows the data setup that makes them work.

## The map visuals available in Power BI

The built-in visuals pane contains five map-type visuals:

| Visual | Best for | Geometry |
|---|---|---|
| Map | Points, simple bubbles, quick exploration | Bubble |
| Filled map (choropleth) | Rates and ratios by region | Polygon |
| Shape map | Custom or non-standard boundaries | Polygon (custom TopoJSON) |
| Azure Map | Rich point clustering, heatmaps, live traffic layers | Point + layers |
| ArcGIS for Power BI | Enterprise GIS analysis, reference layers | Full GIS |

There is also the "Globe" style for the Map visual, which is the same visual rendered on a 3D sphere. It looks impressive and reads poorly, so reserve it for one or two top-level numbers.

## Map visual: the default point map

The plain Map visual places bubbles at latitude/longitude or at named locations it geocodes for you. It has a hard limit: **3,500 data points** before it starts dropping rows to protect rendering performance. Above a few hundred bubbles, individual points overlap and the visual stops communicating anything.

Use Map when:

- You have under roughly 1,000 distinct locations.
- Latitude and longitude columns already exist in your model.
- The question is "where are these things" rather than "how do regions compare".

Configuration basics:

1. Add the visual from the Visualizations pane.
2. Drop a geographic field (Country, State, City) into **Location**.
3. Optionally add Latitude and Longitude fields into their dedicated wells. Doing this bypasses geocoding and is more reliable.
4. Put a numeric measure into **Bubble size**.
5. Put a descriptive field into **Legend** if you want colour categories.

Latitude and longitude should be numeric decimal degrees, not text. If your source stores `"51.5074 N"` you need to convert it in Power Query first.

```powerquery
let
    Source = Csv.Document(File.Contents("C:\data\stores.csv"), [Delimiter=",", Encoding=65001]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    // Strip hemisphere letters and convert to signed decimals
    SplitLat = Table.SplitColumn(Promoted, "Latitude", Splitter.SplitTextByAnyDelimiter({" ", "°"}),
        {"LatDeg", "LatHemi"}),
    SplitLon = Table.SplitColumn(SplitLat, "Longitude", Splitter.SplitTextByAnyDelimiter({" ", "°"}),
        {"LonDeg", "LonHemi"}),
    Typed = Table.TransformColumnTypes(SplitLon,
        {{"LatDeg", type number}, {"LonDeg", type number}}),
    SignedLat = Table.TransformColumns(Typed, {"LatDeg", each if Text.Upper([LatHemi]) = "S" then -_ else _, type number}),
    SignedLon = Table.TransformColumns(SignedLat, {"LonDeg", each if Text.Upper([LonHemi]) = "W" then -_ else _, type number})
in
    SignedLon
```

Note the asymmetry: latitude is North/South, longitude is East/West. Getting that backwards puts your stores in the ocean.

## Filled map: choropleths and their pitfalls

The Filled map shades entire regions based on a measure. It only works with a single geographic category in the **Location** well and a single measure in **Legend**, because it is drawing one polygon per location.

The classic mistake is putting an **additive measure** on a filled map. Population totals, revenue totals, and headcount totals all reward big regions. A country or state with ten times the land area will look ten times as red even if its per-capita value is low. Choropleths must use rates, ratios, or averages:

```dax
Revenue per Capita =
DIVIDE(
    SUM(Sales[Revenue]),
    SUM(Population[TotalPopulation]),
    BLANK()
)
```

If you genuinely need to compare totals across regions of wildly different sizes, use a bar chart instead. A sorted bar chart beats a filled map for ranking every time.

Two more filled map behaviours worth knowing:

- **Disputed borders.** If a location name is ambiguous or claimed by more than one country, tiles may render blank or be omitted. Bing's geocoder handles these inconsistently.
- **No drill-down.** The filled map does not drill from country to state to city the way the Map visual can, because it renders one polygon set per level.

## Shape map: when standard boundaries fail

The Shape map visual accepts a custom TopoJSON file, which is the only way to render boundaries that Bing does not know about: sales territories, hospital catchment areas, custom administrative zones.

The workflow is:

1. Obtain a TopoJSON file with a `properties` key on each feature. The value inside that key is the identifier you will join on.
2. Add the Shape map visual, go to **Format > Map settings**, and supply the JSON.
3. Put a field whose values match the JSON `properties` key into **Location**.
4. Put a measure into **Color saturation**.

Shape map is static. The geometry is baked into the report file, so editing boundaries means re-importing. It also has no basemap, so you cannot show roads or cities underneath.

## Azure Maps: the modern replacement

Azure Maps is the direction Microsoft is pushing. It supports bubble and heatmap layers, clustering that handles tens of thousands of points, and optional reference layers. For point-based geographic analysis at scale, it is the right choice over the legacy Map visual.

One caveat: Azure Maps requires an Azure Maps account for some features and is subject to a view limit per render. On very dense datasets, enable clustering rather than plotting raw points.

## Choosing in practice

Run through this decision sequence:

1. **Are you comparing a rate across administrative regions?** Use Filled map. If regions are non-standard, use Shape map.
2. **Are you locating discrete things (stores, patients, incidents)?** Use Azure Maps, or Map for small datasets.
3. **Are you doing real GIS work with reference layers?** Use ArcGIS.
4. **Is the geographic attribute genuinely the point of the analysis, or just a dimension?** If it is just a dimension, a bar chart sorted by the region name is faster to read and never renders blank.

That last question matters more than the others. Maps are expensive in screen space and low in precision. A map with twelve cities tells you less than a twelve-row bar chart, and it costs the reader more effort.

## Keeping the map readable

- Set the visual's data limit consciously. Map stops at 3,500 points; Azure Maps goes much higher with clustering.
- Turn off auto-zoom if you are presenting to a live audience; the map will jump between pages.
- Avoid putting categories with more than about eight distinct values into the Legend of a Map visual. The colour palette runs out and the legend becomes a list.
- If a region renders as a blank tile, check the spelling against Bing's expected names. "US" and "USA" and "United States" can behave differently depending on the other fields in the visual.
- Latitude/Longitude fields must be categorised as such for some visuals to accept them. Right-click the column in the Fields list, then **Data category > Latitude** / **Longitude**.

## FAQ

### Q: Why does my filled map show only one colour?

The measure in the Legend well is almost certainly a total rather than a rate, and the values span such a wide range that everything below the maximum looks identical. Switch to a per-capita or percentage measure. If that is not what you want, switch to a bar chart.

### Q: Does the Map visual work with postcodes?

It works with postcodes in some countries (UK, US ZIP codes, Canada) through Bing geocoding, but reliability varies and it is slow. The reliable route is to store latitude and longitude in your model, joined by postcode, and use those columns instead.

### Q: Can I use conditional formatting on map bubbles?

Bubble colour follows the Legend field, not the conditional formatting engine. To drive colour from a measure you need to create a calculated column that bucketises the value and place that column in the Legend well. Formats like gradient rules that work on tables and bar charts do not apply here.

### Q: Why is my Shape map blank?

Three usual causes: the TopoJSON file has no `properties` key, the values in your Location field do not exactly match the property values (case and whitespace matter), or the visual has no measure in Color saturation. Fix the join first.

### Q: Do map visuals work in DirectQuery?

Yes, but they can be slow, because geocoding and polygon lookups add latency on top of the query round-trip. If your map is sluggish under DirectQuery, consider importing just the geographic dimension table while leaving the fact table in DirectQuery. The trade-offs are covered in our DirectQuery vs Import mode guide.

## Related Reading

- [Power BI Dashboard Design Principles](/tutorials/power-bi-dashboard-design-principles/)
- [Power BI Common Mistakes for Beginners](/tutorials/power-bi-common-mistakes-beginners/)
- [Data Modeling: Star Schema Guide](/tutorials/data-modeling-star-schema/)
- [Measure vs Calculated Column](/tutorials/measure-vs-calculated-column/)
- [Conditional Formatting in Power BI Charts](/tutorials/conditional-formatting-charts-power-bi/)
- [DirectQuery vs Import Mode](/tutorials/directquery-vs-import-mode/)
- [DAX Basics](/tutorials/dax-basics/)

- [Power BI Matrix Visual: Best Practices and Tips](/tutorials/power-bi-matrix-visual/)