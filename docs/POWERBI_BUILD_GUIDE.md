# Power BI Build Guide

Follow this to turn the three CSVs into the four-page dashboard. ~45–60 min.

## 1. Load data
`Home → Get data → Text/CSV` and import all three: `fact_flights.csv`,
`dim_carrier.csv`, `dim_airport.csv`. In Power Query, confirm numeric columns
(`dep_delay`, `arr_delay`, `air_time`, `distance`, `*_delayed_15`) are typed as
whole/decimal numbers, then **Close & Apply**.

### Add a Date table
`Modeling → New table`:
```DAX
DimDate =
ADDCOLUMNS(
    CALENDAR(DATE(2013,1,1), DATE(2013,12,31)),
    "Month", MONTH([Date]),
    "Month Name", FORMAT([Date],"MMM"),
    "Weekday", WEEKDAY([Date],2),
    "Weekday Name", FORMAT([Date],"ddd")
)
```
Mark it as a date table (`Table tools → Mark as date table → Date`).

## 2. Model (relationships)
Drag to create these (all one-to-many, single direction):
- `fact_flights[carrier]` → `dim_carrier[carrier]`
- `fact_flights[origin]` → `dim_airport[faa]`  (active)
- `fact_flights[dest]` → `dim_airport[faa]`  (create a 2nd, inactive — for a dest map)
- `fact_flights[flight_date]` → `DimDate[Date]`

## 3. Core measures (create in a new "Measures" table)
```DAX
Total Flights   = COUNTROWS(fact_flights)
Cancelled       = SUM(fact_flights[is_cancelled])
Cancel Rate %   = DIVIDE([Cancelled], [Total Flights])
Avg Arr Delay   = AVERAGE(fact_flights[arr_delay])
Avg Dep Delay   = AVERAGE(fact_flights[dep_delay])
Delayed 15+     = SUM(fact_flights[arr_delayed_15])
% Delayed 15+   = DIVIDE([Delayed 15+], COUNTROWS(FILTER(fact_flights, NOT ISBLANK(fact_flights[arr_delayed_15]))))
On-Time Rate %  = 1 - [% Delayed 15+]
```
Format the three `%` measures as Percentage, the delay measures as 1 decimal.

## 4. Pages & visuals

**Page 1 — Executive Overview**
- KPI cards (top row): `Total Flights`, `On-Time Rate %`, `Avg Arr Delay`, `Cancel Rate %`
- Line chart: `% Delayed 15+` by `DimDate[Month Name]` (shows the summer + December spikes)
- Bar chart: `% Delayed 15+` by `dim_carrier[carrier_name]`, sorted descending
- Slicers down the side: Month, Carrier, Origin

**Page 2 — Time Analysis (the headline story)**
- Column chart: `% Delayed 15+` by `sched_dep_hour` (the cascade — morning low, evening high)
- Matrix heatmap: rows = `Weekday Name`, columns = `sched_dep_hour`, values = `% Delayed 15+`,
  conditional-formatted background (green→red)
- Card: `% Delayed 15+` with an hour slicer so viewers can test "book before 9am"

**Page 3 — Route & Airport**
- Map: `dim_airport[lat]`/`[lon]` as location, bubble size = `Total Flights`,
  bubble colour = `% Delayed 15+` (origin relationship)
- Table: `route`, `Total Flights`, `Avg Arr Delay`, `% Delayed 15+` — top 10 by delay,
  with a `Total Flights >= 500` visual-level filter

**Page 4 — Weather Impact**
- Clustered bar: `% Delayed 15+` and `Avg Arr Delay` by `adverse_weather`
  (relabel 0/1 as Normal / Adverse)
- Scatter: `wind_speed` (x) vs `Avg Arr Delay` (y), one dot per origin-hour

## 5. Polish
- Consistent title on each page; a single accent colour for the "delayed" series (red-ish).
- Turn on cross-filtering so clicking a carrier filters every chart.
- Add one text box per page with the key takeaway (pull from `INSIGHTS.md`).
- Publish to Power BI Service and grab the public/share link for your resume + GitHub README.

## Excel companion (optional, 15 min — shows Excel skill, the #1 requested tool)
1. Open `fact_flights.csv` in Excel → `Insert → PivotTable`.
2. PivotTable A — Rows: `carrier_name`; Values: Count of flights, Average of `arr_delay`,
   and `% delayed` (add `arr_delayed_15` as Average, format %).
3. PivotTable B — Rows: `sched_dep_hour`; Values: Average of `arr_delay`.
4. Insert a PivotChart on each, add Slicers for `month` and `origin`, drop them on one
   "Dashboard" sheet. Save as `airline_otp.xlsx` and add it to the repo.
