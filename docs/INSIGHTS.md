# Airline On-Time Performance — Key Insights

**Question for the business:** Where do flight delays come from, and which levers
would most improve on-time performance?

**Data:** 336,776 flights from the three major NYC airports (JFK, LGA, EWR), 2013,
joined with carrier, airport, aircraft and hourly weather tables (US DOT / BTS-style).
"Delayed" = 15 or more minutes late on arrival (industry standard). Analysis in
PostgreSQL + Python; dashboard in Power BI.

---

## Headline
**Roughly 1 in 4 flights (23.8%) arrived 15+ minutes late**, the average flight landed
6.9 minutes behind schedule, and 2.45% were cancelled. The delay problem is real but
**highly predictable** — it concentrates in specific hours, months, carriers and routes.

## The five findings that matter

**1. Delays cascade through the day — the single biggest pattern.**
Early flights run ahead of schedule; lateness compounds hour by hour. 6–7 a.m.
departures averaged ~5 minutes *early* with ~11% delayed, while 9 p.m. departures hit
**35.9% delayed, +18 min on average.** The aircraft and crew inherit each earlier
delay. *Lever: protect morning schedules and build recovery buffer into evening banks.*

**2. Once a flight leaves late, it stays late.**
Of 72,914 flights that pushed back 15+ min late, aircraft recovered only **3.8 minutes**
in the air on average, and just **6.8% clawed back to an on-time arrival.** *Departure
punctuality — not speeding up en route — is where on-time performance is won.*

**3. Season swings performance by more than 2x.**
Worst months were December (32.2% delayed), July (31.0%) and June (30.2%) — holiday
peak and summer thunderstorms. Best was September, when flights actually averaged
4 minutes *early* (13.4% delayed). *Lever: seasonal staffing and schedule padding.*

**4. Weather roughly doubles the delay rate.**
In adverse conditions (precipitation, wind ≥20 mph, or visibility <5 mi) **36.0%** of
flights were delayed vs **21.6%** in normal weather — avg delay 22.2 vs 4.3 minutes.
Weather explains a large, but not the majority, share of delay.

**5. Delay is concentrated by carrier, route and origin.**
- **Carriers:** regional/low-cost operators led the delay table (AirTran 33.7%,
  ExpressJet 30.3%, JetBlue 26.7%); legacy carriers were best (US Airways 18.2%,
  Delta 18.8%, American 19.0%). Regionals also cancelled most (ExpressJet/Endeavor ~5%+).
- **Origin:** Newark (EWR) was the worst NYC airport — 25.5% delayed vs 22.4% at LaGuardia.
- **Routes:** EWR→Richmond (39.5%), EWR→Milwaukee (37.4%) and JFK→Columbus (36.5%) were
  the most delay-prone of all routes with 500+ flights — all short/regional, mostly from Newark.

## Recommendation
On-time performance is mostly an **operational scheduling problem, not a weather problem.**
The highest-ROI moves: (1) ruthlessly protect early-day departures to stop the cascade,
(2) add recovery buffer to evening and peak-season banks, and (3) target the worst
carrier/route combinations out of Newark for schedule or process intervention.

*Dashboard lets an ops manager filter all of the above by month, hour, carrier, route and weather.*
