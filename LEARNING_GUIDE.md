# 📘 Learning Guide — Airline On-Time Performance Analysis

This guide walks you through **how this whole project works and how to rebuild it yourself**,
so you can learn the end-to-end data analyst workflow — and talk about it confidently in an interview.

Read it top to bottom once. Then do the "Your turn" boxes to actually practise. Everything here
uses **free tools** (you're on Windows, so Power BI Desktop is free; Excel is replaced with free
Google Sheets or LibreOffice Calc).

---

## 0. The analyst mindset (read this first)

A data analyst doesn't just "make charts." The job is a loop:

> **Business question → get data → clean it → explore it → find the insight → show it clearly → recommend an action.**

This project answers one real business question an airline operations team would actually ask:

> **"Where do our flight delays come from, and what would most improve on-time performance?"**

Keep that question in your head the whole way through. Every step exists to answer it.

---

## 1. The toolchain (and your free versions)

| Step | What this project uses | Your free option (Windows) |
|------|------------------------|-----------------------------|
| Clean & shape data | Python + pandas | Same — free. Install via Anaconda (you already have `.conda`) |
| Query & analyse | PostgreSQL / SQL | **DuckDB** (free, no server — `pip install duckdb`) or [db-fiddle.com](https://www.db-fiddle.com) |
| Dashboard (BI) | Power BI | **Power BI Desktop** — free on Windows, get it from the Microsoft Store |
| Spreadsheet dashboard | Excel | **Google Sheets** (free, browser) or **LibreOffice Calc** (free) |
| Version control | Git + GitHub | Same — free |

You do **not** need Excel. The `.xlsx` I built opens in Google Sheets and LibreOffice, and every
formula in it (`SUMPRODUCT`, `INDEX/MATCH`, pivot tables) works the same way in both.

---

## 2. The dataset

**Source:** US DOT / BTS–style flight operations data (the `nycflights13` dataset) — every flight
that departed the three major New York airports (JFK, LGA, EWR) in 2013: **336,776 flights**, joined
with reference tables for carriers, airports and hourly weather.

Why this dataset is good for a portfolio:
- It's **big enough to be real** (336k rows) but clean enough to finish.
- It has a **time dimension, categories, geography and weather** — so you can show many analysis types.
- It maps to a real job (you applied to Jazz Aviation — this is literally their domain).

The files after cleaning:
- `data/fact_flights.csv` — one row per flight (the "fact" table)
- `data/dim_carrier.csv`, `data/dim_airport.csv` — "dimension" (lookup) tables

> **Fact vs dimension** is the core idea of data modelling: a big table of *events* (flights), plus
> small tables of *things* those events reference (carriers, airports). BI tools join them on a key.

---

## 3. Phase 1 — Clean & feature-engineer the data (`build_data.py`)

Raw data is never ready to analyse. Open `build_data.py` and follow along. The important moves:

**a) Handle missing / special rows instead of ignoring them.**
Cancelled flights have no departure time. We *flag* them (`is_cancelled`) rather than delete them —
because a cancellation is itself a KPI, and silently dropping rows hides reality.

**b) Create the fields the question needs ("feature engineering").** Raw data rarely has the exact
column you want, so you derive it:
- `arr_delayed_15` — was the flight 15+ min late? (the US DOT industry definition of "delayed")
- `sched_dep_hour` — the hour of day, so we can see the daily pattern
- `route` = origin + "-" + destination
- `delay_recovery` = departure delay − arrival delay (minutes made up in the air)
- `adverse_weather` — a flag combining rain, high wind, or low visibility

**c) Join weather** onto each flight by origin + hour, so we can ask "do delays rise in bad weather?"

> **Why this matters in interviews:** "data cleaning is 80% of the job" is a cliché because it's true.
> Being able to say *"I flagged cancellations instead of dropping them, and engineered a 15-minute
> delay flag to match the DOT standard"* shows judgment, not just tool knowledge.

**▶️ Your turn:** Install Anaconda/Python, `pip install nycflights13 pandas duckdb`, and run
`python build_data.py`. Open the CSV and scroll through it. Find one cancelled flight and confirm its
`arr_delay` is blank but `is_cancelled` is 1.

---

## 4. Phase 2 — Explore with SQL (`sql/analysis.sql`)

SQL is the #1 tested skill in data analyst interviews. This file answers the business question in
six queries. Open it and read each one alongside these notes.

**Q1 — Headline KPIs.** Simple aggregation: total flights, % delayed, cancel rate. Always start by
sizing the problem.

**Q2 — Carrier league table.** This uses a **CTE** (the `WITH carrier_stats AS (...)` block) to
compute per-carrier stats first, then a **window function** `RANK() OVER (ORDER BY ...)` to rank them.
- A **CTE** is a named temporary result you can read from — it makes complex queries readable.
- A **window function** computes across rows *without collapsing them* (unlike `GROUP BY`). `RANK()`
  gives each carrier its position. This is the single most impressive SQL concept for an interview.

**Q3 — When do delays happen?** Three `GROUP BY` queries: by month, by departure hour, by weekday.
This is where the main story appears (see Phase 3).

**Q4 — Worst routes.** `GROUP BY route ... HAVING COUNT(*) >= 500`. The `HAVING` filters *after*
grouping — we only keep routes with enough flights for the rate to be trustworthy. (Filtering out
small samples is a real analyst habit — a route with 3 flights at 100% "delayed" is noise.)

**Q5 — Weather impact.** Compares delay rates in adverse vs normal conditions.

**Q6 — In-air recovery.** Of flights that left late, how many caught up? This answers "should we
try to recover in the air, or fix the gate?"

> **Window functions, CTEs, HAVING, and aggregation** are exactly the SQL concepts job posts list.
> You now have a project that uses all of them for a real reason — that's what makes it portfolio-worthy.

**▶️ Your turn:** Run `python run_analysis.py` (it executes every query and prints the results).
Then open `sql/analysis.sql` and change one thing — e.g. change `>= 500` to `>= 1000` in Q4 — rerun,
and see how the worst-routes list changes. Changing a query and predicting the result is how you learn SQL.

---

## 5. Phase 3 — The findings (the story you tell)

The numbers only matter if you can explain them. Here's the narrative this analysis produced:

1. **~1 in 4 flights (23.8%) arrived 15+ min late**, average 6.9 min, 2.45% cancelled. Real, but predictable.
2. **Delays cascade through the day.** 6 a.m. flights run *early* (~11% late); 9 p.m. flights hit
   **35.9% late**. Each delayed flight hands its delay to the next one using that aircraft.
3. **Late departures don't recover** — only **6.8%** of flights that left 15+ min late clawed back to
   on-time. So punctuality is won **at the gate, not in the air.** (This is the "aha" insight.)
4. **Bad weather ~doubles the delay rate** (36% vs 22%).
5. **Delay concentrates** by carrier (regionals worst), by airport (Newark worst) and by route.

**The recommendation:** on-time performance is mostly an *operational scheduling* problem, not a
weather problem — protect morning departures, add buffer to evening/peak-season banks, and target the
worst Newark routes.

> **Interview gold:** finding #3 is counterintuitive and memorable. Lead with it. "I found that once a
> flight leaves late, it almost never recovers — only 7% — so the leverage is in gate punctuality, not
> speeding up en route." That one sentence shows you can turn data into a decision.

Full write-up: [`docs/INSIGHTS.md`](docs/INSIGHTS.md).

---

## 6. Phase 4 — Build the dashboards

### 6a. The spreadsheet dashboard (free: Google Sheets or LibreOffice)

Open `airline_otp.xlsx` in **Google Sheets** (drive.google.com → New → upload) or **LibreOffice Calc**.
Look at the **Dashboard** sheet and click a KPI cell — you'll see it's a *formula*, not a typed number:
- `Total Flights` = `SUM('By Carrier'!B2:B17)`
- `Avg Arrival Delay` = `SUMPRODUCT(weight, avg_delay) / SUM(weight)` — a **weighted average**
- `Worst month` = `INDEX(..., MATCH(MAX(...), ...))` — a **lookup** that finds the month with the highest rate

**Learn these four functions — they're the backbone of analyst Excel/Sheets work:**
- `SUMIFS` / `COUNTIFS` / `AVERAGEIFS` — conditional aggregation
- `SUMPRODUCT` — weighted sums (and array math)
- `INDEX` + `MATCH` — flexible lookups (better than VLOOKUP)
- **PivotTables** (called "Pivot tables" in Google Sheets) — drag-and-drop summarisation

**▶️ Your turn (this is the Excel skill your resume claims):** In Google Sheets, open the raw
`data/fact_flights.csv`, then `Insert → Pivot table`. Put `carrier_name` in Rows and `arr_delay` in
Values (summarise by Average). You just rebuilt the carrier analysis in 60 seconds — that's what a
PivotTable does. Do another with `sched_dep_hour` in Rows to see the daily cascade.

### 6b. The Power BI dashboard (free on your Windows machine)

Install **Power BI Desktop** from the Microsoft Store (free). Then follow the step-by-step build in
[`docs/POWERBI_BUILD_GUIDE.md`](docs/POWERBI_BUILD_GUIDE.md) — it gives you the exact data model,
the DAX measures to type, and the four dashboard pages to build. ~45–60 min.

When it's done: `File → Publish`, and copy the public link. Put that link in your resume and the
README — a live dashboard link is what makes a recruiter stop scrolling.

> DAX (Power BI's formula language) looks scary but starts simple: `Total Flights = COUNTROWS(fact_flights)`.
> The build guide gives you all the measures to copy; type them yourself once to learn the pattern.

---

## 7. Phase 5 — Publish to GitHub

Covered step-by-step in [`GITHUB_SETUP.md`](GITHUB_SETUP.md). The short version of *why*: GitHub is
where employers look to see that you can actually do the work. A clean repo with a good README is
itself a portfolio piece.

---

## 8. How to talk about this project (interview script)

When asked "tell me about a project," use this structure (STAR-ish):

- **Situation/Task:** "I wanted to understand what drives airline delays, using real operations data."
- **Action:** "I cleaned 336,000 flights in Python, analysed them in SQL using CTEs and window
  functions, and built a Power BI dashboard."
- **Result:** "The key finding was that delays cascade through the day and late departures recover only
  7% of the time — so the recommendation was to protect morning gate punctuality rather than chase
  recovery in the air."
- **Reflection:** "The hardest part was deciding how to treat cancelled flights — I flagged them as a
  separate KPI instead of dropping them, so the delay rate wasn't distorted."

Practise saying that out loud until it's natural.

---

## 9. Make it yours (extend it)

Once you understand it, change it — that's the best learning and it makes the project *yours*:
- Add a 7th SQL query: which **aircraft** (tail number) had the worst delays? (join `planes`)
- Add a **day-of-week × hour heatmap** in Power BI.
- Swap in a **Canadian** dataset (StatCan or a Halifax open-data set) and redo the analysis — that
  localises your portfolio for NS employers.

---

*You built this. Now you understand it. Go talk about it like you own it.*
