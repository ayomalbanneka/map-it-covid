import pandas as pd

epi = pd.read_csv("countries_epi.csv", parse_dates=["date"])
countries = pd.read_csv("countries.csv")

# Hand-placed centroids for the four countries the dataset has no coordinates for
patch = {
    "Armenia": (40.07, 45.04),
    "Georgia": (42.32, 43.36),
    "Macedonia": (41.61, 21.75),
    "Palestine": (31.95, 35.23),
}
for name, (lat, lon) in patch.items():
    countries.loc[countries["country_name"] == name, ["latitude", "longitude"]] = [lat, lon]

# Under 100k people, one case swings the per-100k rate too much to trust
countries = countries[countries["population"] >= 100_000]

df = epi.merge(countries, on="location_key").sort_values(["location_key", "date"])
# Running maximum, so data corrections that make the total dip can't delay a crossing
df["peak_cum"] = df.groupby("location_key")["cumulative_confirmed"].cummax()
df["per100k"] = df["peak_cum"] / df["population"] * 100_000

waves = countries.set_index("location_key")
for t in (10, 100, 1000):
    first = df[df["per100k"] >= t].groupby("location_key")["date"].min()
    waves[f"d{t}"] = first
waves = waves.reset_index()
waves.to_csv("waves.csv", index=False)

print(len(waves), "countries kept")
print("no case data at all:", waves[waves["d10"].isna() & ~waves["location_key"].isin(df[df["per100k"] > 0]["location_key"])]["country_name"].tolist())
for t in (10, 100, 1000):
    print(f"crossed {t} per 100k:", waves[f"d{t}"].notna().sum())
ok = waves.dropna(subset=["d10"]).sort_values("d10")
print("first to 10 per 100k:", ok.head(5)[["country_name", "d10"]].astype(str).values.tolist())
print("last to 10 per 100k:", ok.tail(5)[["country_name", "d10"]].astype(str).values.tolist())
print(waves[waves["location_key"] == "LK"][["country_name", "d10", "d100", "d1000"]].to_string(index=False))
