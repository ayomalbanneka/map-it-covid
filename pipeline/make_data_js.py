import json
import pandas as pd

w = pd.read_csv("waves.csv")

def d(x):
    return None if pd.isna(x) else str(x)[:10]

rows = [{"k": r.location_key, "n": r.country_name,
         "lat": round(r.latitude, 3), "lon": round(r.longitude, 3),
         "pop": int(r.population),
         "d10": d(r.d10), "d100": d(r.d100), "d1000": d(r.d1000)}
        for r in w.itertuples()]
open("data.js", "w").write("const WAVES = " + json.dumps(rows) + ";\n")
print(len(rows), "countries written;", sum(r["d1000"] is not None for r in rows), "reach 1000 per 100k")
