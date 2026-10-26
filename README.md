# ✈️ Airline On-Time Performance & Delay Analysis

End-to-end data analysis of **336,776 flights** — from raw operational data to a
business-ready Power BI dashboard — answering where flight delays come from and which
levers would most improve on-time performance.

**Stack:** PostgreSQL · SQL (CTEs, window functions) · Python (pandas) · Power BI · Excel

---

## 📌 TL;DR findings
- **1 in 4 flights (23.8%)** arrived 15+ min late; 2.45% were cancelled.
- **Delays cascade through the day:** 6 a.m. departures run early (~11% late); 9 p.m.
  departures are **35.9% late**. Lateness compounds flight to flight.
- **Late departures don't recover:** only **6.8%** of flights that left 15+ min late
  clawed back to an on-time arrival. Departure punctuality is the real lever.
- **Adverse weather ~doubles the delay rate** (36.0% vs 21.6%).
- Delay concentrates by **carrier, route and origin** (Newark worst of the NYC airports).

➡️ Full write-up: [`docs/INSIGHTS.md`](docs/INSIGHTS.md)

## 📊 Dashboards
- **Power BI** — interactive report with four pages (Executive Overview, Time Analysis,
  Route & Airport map, Weather Impact), all cross-filterable. Build guide + DAX measures:
  [`docs/POWERBI_BUILD_GUIDE.md`](docs/POWERBI_BUILD_GUIDE.md).
- **Excel** — `airline_otp.xlsx`: a KPI dashboard driven by live formulas (`SUMPRODUCT`,
  `INDEX`/`MATCH`) with summary sheets and native charts. Opens in Excel, Google Sheets or LibreOffice.

<!-- Add a screenshot once built: ![dashboard](docs/dashboard.png) -->

## 🗂️ Data
US DOT / BTS-style flight operations data (`nycflights13`): all flights from the three
major NYC airports (JFK, LGA, EWR) in 2013, joined with carrier, airport, aircraft and
hourly weather reference tables.

| File | Rows | Description |
|------|------|-------------|
| `data/fact_flights.csv` | 336,776 | Cleaned fact table (one row per flight) with delay flags, route, weather — shipped gzipped (`gunzip data/fact_flights.csv.gz`), or regenerate with `build_data.py` |
| `data/dim_carrier.csv` | 16 | Carrier code → airline name |
| `data/dim_airport.csv` | 1,458 | Airport reference incl. lat/lon for mapping |

### Cleaning & feature engineering (`build_data.py`)
- Flagged cancellations (no departure time) as a KPI instead of dropping them.
- Derived `dep_delayed_15` / `arr_delayed_15` (US DOT 15-min standard), `arr_on_time`,
  scheduled-departure-hour, day-of-week, `route`, and `delay_recovery`
  (minutes made up in the air = dep_delay − arr_delay).
- Joined hourly weather on origin + time, and flagged `adverse_weather`
  (precip > 0, or wind ≥ 20 mph, or visibility < 5 mi).

## 🔍 Analysis (`sql/analysis.sql`)
Six business questions answered in SQL:
1. Overall on-time KPIs
2. Carrier performance league table (`RANK()` window function)
3. When delays happen — by month, hour, and weekday
4. Most delay-prone routes (min 500 flights)
5. Weather impact — adverse vs normal
6. In-air delay recovery

## ▶️ Reproduce
```bash
pip install nycflights13 pandas duckdb
python build_data.py        # writes the cleaned CSVs to data/
python run_analysis.py      # runs sql/analysis.sql and prints every result
```

## 📁 Structure
```
airline-otp-analysis/
├── README.md
├── build_data.py              # clean + feature-engineer + export CSVs
├── run_analysis.py            # run the SQL and print results
├── build_excel.py             # build the Excel dashboard
├── airline_otp.xlsx           # Excel KPI dashboard (live formulas + charts)
├── data/                      # fact + dimension CSVs (Power BI ready)
├── sql/analysis.sql           # the 6 analytical queries
└── docs/
    ├── INSIGHTS.md            # 1-page business write-up
    └── POWERBI_BUILD_GUIDE.md # data model, DAX measures, dashboard layout
```

---
*Built by Jenoah Gonsalves · [GitHub](https://github.com/Jenzzzz7) · [LinkedIn](https://www.linkedin.com/in/jenoah-gonsalves-106113146/)*
