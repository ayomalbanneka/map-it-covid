import pandas as pd

BASE = "https://storage.googleapis.com/covid19-open-data/v3/"

epi = pd.read_csv("countries_epi.csv", parse_dates=["date"])
idx = pd.read_csv(BASE + "index.csv",
                  usecols=["location_key", "country_name", "aggregation_level"])
geo = pd.read_csv(BASE + "geography.csv",
                  usecols=["location_key", "latitude", "longitude"])
dem = pd.read_csv(BASE + "demographics.csv",
                  usecols=["location_key", "population"])

countries = (idx[idx["aggregation_level"] == 0][["location_key", "country_name"]]
             .merge(geo, on="location_key", how="left")
             .merge(dem, on="location_key", how="left"))
countries = countries[countries["location_key"].isin(epi["location_key"].unique())]
countries.to_csv("countries.csv", index=False)

print(len(countries), "countries with case data")
print("missing coordinates:", countries[countries["latitude"].isna()]["country_name"].tolist())
print("missing population:", countries[countries["population"].isna()]["country_name"].tolist())
print("population under 100k:", countries[countries["population"] < 100_000][["country_name", "population"]].values.tolist())
print(countries[countries["location_key"].isin(["LK", "US", "FR", "NZ"])].to_string(index=False))
