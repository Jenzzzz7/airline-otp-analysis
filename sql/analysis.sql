-- ============================================================================
-- Airline On-Time Performance & Delay Analysis
-- Dialect: PostgreSQL (also runs on DuckDB). Fact table loaded from fact_flights.csv
-- "Delayed" = 15+ minutes late (US DOT standard). Cancelled flights flagged separately.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Q1. Overall on-time performance (headline KPIs)
-- ----------------------------------------------------------------------------
SELECT
    COUNT(*)                                              AS total_flights,
    SUM(is_cancelled)                                     AS cancelled,
    ROUND(100.0 * SUM(is_cancelled) / COUNT(*), 2)        AS cancel_rate_pct,
    ROUND(AVG(dep_delay), 1)                              AS avg_dep_delay_min,
    ROUND(AVG(arr_delay), 1)                              AS avg_arr_delay_min,
    ROUND(100.0 * SUM(arr_delayed_15) / COUNT(arr_delayed_15), 2) AS pct_arr_delayed_15
FROM fact_flights;

-- ----------------------------------------------------------------------------
-- Q2. Carrier performance league table (ranked worst to best on arrival delay)
--     Window function RANK() benchmarks each airline against the fleet.
-- ----------------------------------------------------------------------------
WITH carrier_stats AS (
    SELECT
        carrier_name,
        COUNT(*)                                                     AS flights,
        ROUND(AVG(arr_delay), 1)                                     AS avg_arr_delay,
        ROUND(100.0 * SUM(arr_delayed_15) / COUNT(arr_delayed_15),1) AS pct_delayed_15,
        ROUND(100.0 * SUM(is_cancelled) / COUNT(*), 2)               AS cancel_rate_pct
    FROM fact_flights
    GROUP BY carrier_name
    HAVING COUNT(*) >= 1000          -- ignore tiny carriers
)
SELECT
    RANK() OVER (ORDER BY pct_delayed_15 DESC) AS worst_rank,
    carrier_name, flights, avg_arr_delay, pct_delayed_15, cancel_rate_pct
FROM carrier_stats
ORDER BY pct_delayed_15 DESC;

-- ----------------------------------------------------------------------------
-- Q3a. When do delays happen? — by month
-- ----------------------------------------------------------------------------
SELECT
    month,
    COUNT(*)                                                      AS flights,
    ROUND(AVG(arr_delay), 1)                                      AS avg_arr_delay,
    ROUND(100.0 * SUM(arr_delayed_15) / COUNT(arr_delayed_15), 1) AS pct_delayed_15
FROM fact_flights
GROUP BY month
ORDER BY month;

-- Q3b. When do delays happen? — by scheduled departure hour
SELECT
    sched_dep_hour,
    COUNT(*)                                                      AS flights,
    ROUND(AVG(arr_delay), 1)                                      AS avg_arr_delay,
    ROUND(100.0 * SUM(arr_delayed_15) / COUNT(arr_delayed_15), 1) AS pct_delayed_15
FROM fact_flights
WHERE sched_dep_hour BETWEEN 5 AND 23
GROUP BY sched_dep_hour
ORDER BY sched_dep_hour;

-- Q3c. When do delays happen? — by day of week
SELECT
    dow_num, day_of_week,
    ROUND(AVG(arr_delay), 1)                                      AS avg_arr_delay,
    ROUND(100.0 * SUM(arr_delayed_15) / COUNT(arr_delayed_15), 1) AS pct_delayed_15
FROM fact_flights
GROUP BY dow_num, day_of_week
ORDER BY dow_num;

-- ----------------------------------------------------------------------------
-- Q4. Most delay-prone routes (min 500 flights so the rate is meaningful)
-- ----------------------------------------------------------------------------
SELECT
    route, origin, dest,
    COUNT(*)                                                      AS flights,
    ROUND(AVG(arr_delay), 1)                                      AS avg_arr_delay,
    ROUND(100.0 * SUM(arr_delayed_15) / COUNT(arr_delayed_15), 1) AS pct_delayed_15
FROM fact_flights
GROUP BY route, origin, dest
HAVING COUNT(*) >= 500
ORDER BY pct_delayed_15 DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- Q5. Weather impact — adverse vs normal conditions at origin
-- ----------------------------------------------------------------------------
SELECT
    CASE WHEN adverse_weather = 1 THEN 'Adverse (rain/wind/low-vis)'
         ELSE 'Normal' END                                        AS condition,
    COUNT(*)                                                      AS flights,
    ROUND(AVG(arr_delay), 1)                                      AS avg_arr_delay,
    ROUND(100.0 * SUM(arr_delayed_15) / COUNT(arr_delayed_15), 1) AS pct_delayed_15
FROM fact_flights
WHERE adverse_weather IS NOT NULL
GROUP BY 1
ORDER BY pct_delayed_15 DESC;

-- ----------------------------------------------------------------------------
-- Q6. In-air delay recovery — do late departures still land on time?
--     Of flights that pushed back 15+ min late, how many recovered to on-time?
-- ----------------------------------------------------------------------------
SELECT
    COUNT(*)                                                      AS late_departures,
    ROUND(AVG(delay_recovery), 1)                                 AS avg_min_recovered,
    SUM(arr_on_time)                                              AS recovered_to_on_time,
    ROUND(100.0 * SUM(arr_on_time) / COUNT(*), 1)                 AS pct_recovered
FROM fact_flights
WHERE dep_delayed_15 = 1 AND is_cancelled = 0;
