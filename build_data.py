"""
Airline On-Time Performance & Delay Analysis — data prep
Source: US DOT / BTS-style flight operations data (nycflights13):
all 336,776 flights departing the 3 major NYC airports (JFK, LGA, EWR) in 2013,
joined with carrier, airport, weather and aircraft reference tables.
"""
import nycflights13 as nf
import pandas as pd
import numpy as np

OUT = "data"

flights = nf.flights.copy()
airlines = nf.airlines.copy()
airports = nf.airports.copy()
weather = nf.weather.copy()
planes = nf.planes.copy()

# ---------- CLEAN ----------
n_raw = len(flights)

# Cancelled flights have no departure time. Flag, don't drop (cancellations are a KPI).
flights["is_cancelled"] = flights["dep_time"].isna().astype(int)

# Derived delay flags (industry standard: "delayed" = 15+ minutes late)
flights["dep_delayed_15"] = (flights["dep_delay"] >= 15).astype("Int64")
flights["arr_delayed_15"] = (flights["arr_delay"] >= 15).astype("Int64")
flights["arr_on_time"]    = (flights["arr_delay"] <= 0).astype("Int64")

# Scheduled departure hour (operational time-of-day bucket)
flights["sched_dep_hour"] = flights["hour"]

# Day of week from the date
flights["flight_date"] = pd.to_datetime(flights[["year", "month", "day"]])
flights["day_of_week"] = flights["flight_date"].dt.day_name()
flights["dow_num"] = flights["flight_date"].dt.dayofweek  # 0=Mon

# Route
flights["route"] = flights["origin"] + "-" + flights["dest"]

# Time-in-air recovery: how much delay was made up (or added) between wheels-up and gate
flights["delay_recovery"] = flights["dep_delay"] - flights["arr_delay"]

# Join carrier full names
flights = flights.merge(airlines, on="carrier", how="left").rename(columns={"name": "carrier_name"})

# ---------- WEATHER FEATURES (origin + hour) ----------
w = weather[["origin", "time_hour", "temp", "wind_speed", "precip", "visib"]].copy()
w["adverse_weather"] = (
    (w["precip"] > 0) | (w["wind_speed"] >= 20) | (w["visib"] < 5)
).astype(int)
flights = flights.merge(w, on=["origin", "time_hour"], how="left")

# ---------- EXPORT (Power BI / Excel ready) ----------
# Fact table — trimmed to analysis columns, readable headers
fact = flights[[
    "flight_date", "year", "month", "day", "day_of_week", "dow_num",
    "carrier", "carrier_name", "flight", "tailnum",
    "origin", "dest", "route", "sched_dep_hour",
    "dep_delay", "arr_delay", "air_time", "distance",
    "is_cancelled", "dep_delayed_15", "arr_delayed_15", "arr_on_time",
    "delay_recovery", "adverse_weather", "precip", "wind_speed", "visib",
]].copy()
fact.to_csv(f"{OUT}/fact_flights.csv", index=False)

# Dimension tables
airlines.rename(columns={"name": "carrier_name"}).to_csv(f"{OUT}/dim_carrier.csv", index=False)
airports[["faa", "name", "lat", "lon", "alt", "tz", "tzone"]].to_csv(f"{OUT}/dim_airport.csv", index=False)

print(f"Raw rows: {n_raw:,}")
print(f"Fact rows exported: {len(fact):,}")
print(f"Cancelled: {fact['is_cancelled'].sum():,}")
print(f"Weather matched: {fact['adverse_weather'].notna().sum():,}")
print("Files:", "fact_flights.csv, dim_carrier.csv, dim_airport.csv")
