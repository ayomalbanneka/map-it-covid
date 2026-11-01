import sys
import pandas as pd

cols = ["date", "location_key", "new_confirmed", "new_deceased",
        "cumulative_confirmed", "cumulative_deceased"]
kept = []
for chunk in pd.read_csv(sys.stdin, usecols=cols, chunksize=500_000):
    is_sub = chunk["location_key"].str.contains("_", na=True)
    kept.append(chunk[~is_sub])

df = pd.concat(kept)
df.to_csv("countries_epi.csv", index=False)
print(len(df), "rows,", df["location_key"].nunique(), "countries")