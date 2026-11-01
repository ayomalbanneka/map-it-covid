import os
import shutil
import pandas as pd

BASE = "https://storage.googleapis.com/covid19-open-data/v3/"
keys = ["CA_AB", "CA_BC", "CA_MB", "CA_NB", "CA_NL", "CA_NS", "CA_NT",
        "CA_NU", "CA_ON", "CA_PE", "CA_QC", "CA_SK", "CA_YT"]
SWITCH = pd.Timestamp("2022-05-04")  # first day the national row holds real totals

# Keep an untouched copy so this script can be re-run safely
if not os.path.exists("countries_epi_raw.csv"):
    shutil.copy("countries_epi.csv", "countries_epi_raw.csv")
epi = pd.read_csv("countries_epi_raw.csv", parse_dates=["date"])

series = []
for k in keys:
    d = pd.read_csv(f"{BASE}location/{k}.csv", parse_dates=["date"])
    if "cumulative_confirmed" not in d.columns:
        print("skipping", k, "(no case totals)")
        continue
    series.append(d.set_index("date")["cumulative_confirmed"].rename(k))
prov = pd.concat(series, axis=1).ffill().fillna(0).sum(axis=1)

is_ca = epi["location_key"] == "CA"
nat = epi[is_ca].set_index("date")["cumulative_confirmed"]
fixed = pd.concat([prov[prov.index < SWITCH], nat[nat.index >= SWITCH]])
fixed = fixed[~fixed.index.duplicated()].sort_index()

print("provinces summed:", len(series))
print("provincial sum, day before switch:", prov[prov.index < SWITCH].iloc[-1],
      "| national row on switch day:", nat.loc[SWITCH])
print(fixed.resample("QS").last())

# Swap the fixed totals into Canada's rows, and blank the other Canada columns
epi.loc[is_ca, "cumulative_confirmed"] = epi.loc[is_ca, "date"].map(fixed).values
epi.loc[is_ca, ["new_confirmed", "new_deceased", "cumulative_deceased"]] = float("nan")
epi.to_csv("countries_epi.csv", index=False)
print("patched countries_epi.csv (raw copy kept as countries_epi_raw.csv)")
