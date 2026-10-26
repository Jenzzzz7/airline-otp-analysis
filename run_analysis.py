"""
Run every query in sql/analysis.sql against the cleaned CSVs and print the results.
Uses DuckDB so no database server is needed; the SQL is standard and also runs on
PostgreSQL after loading fact_flights.csv into a table.
"""
import duckdb

con = duckdb.connect()
con.execute("CREATE TABLE fact_flights AS SELECT * FROM read_csv_auto('data/fact_flights.csv')")

sql = open("sql/analysis.sql").read()
statements = [s.strip() for s in sql.split(";") if "SELECT" in s.upper()]

for i, stmt in enumerate(statements, 1):
    # pull the first comment line above the query as a label, if present
    print(f"\n{'='*70}\nQuery {i}\n{'='*70}")
    print(con.execute(stmt).fetchdf().to_string(index=False))
