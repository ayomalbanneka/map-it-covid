import csv
import json
from datetime import date

START = date(2020, 1, 1)
STEP = 7
DAYS = 988  # day indices 0..987, sampled every 7th day

keep = set()
with open("waves.csv", newline="") as f:
    for r in csv.DictReader(f):
        keep.add(r["location_key"])

by_country = {k: {} for k in keep}
with open("countries_epi.csv", newline="") as f:
    for r in csv.DictReader(f):
        k = r["location_key"]
        if k in by_country and r["cumulative_confirmed"]:
            i = (date.fromisoformat(r["date"]) - START).days
            by_country[k][i] = float(r["cumulative_confirmed"])

series = {}
for k, vals in by_country.items():
    cur = 0.0
    out = []
    for i in range(DAYS):
        if i in vals:
            cur = max(cur, vals[i])  # running maximum, so data corrections can't shrink a total
        if i % STEP == 0:
            out.append(int(cur))
    series[k] = out

open("series.js", "w").write("const SERIES = " + json.dumps(series, separators=(",", ":")) + ";\n")
print(len(series), "countries,", len(next(iter(series.values()))), "weekly points each")
print("Sri Lanka, last point:", series["LK"][-1], "| Canada, last point:", series["CA"][-1])
