# The pandemic, country by country

An interactive map that shows **when each country's reported COVID-19 cases passed 10, 100 and 1,000 per 100,000 people**. Press play and watch the pandemic move across the world, or click any country to see its own milestone dates and weekly curve.

Built for the AWS Builder Center **Weekend Challenge: Map it**.

- **Live map:** https://main.dt9qco707eorw.amplifyapp.com/
- **Demo video (under 3 minutes):** https://youtu.be/L72Zzxd-DjE
- **Builder Center post:** https://builder.aws.com/project/3LUY4zakuybjmsLSmtbuEMfgGHZ/weekend-challenge-map-it-the-pandemic-country-by-country

## What it shows

Every dot is a country. It starts grey, then turns yellow (past 10 per 100k), orange (past 100) and red (past 1,000) on the date it crossed each line. The timeline runs from January 2020 to September 2022.

- 195 of 198 countries on the map crossed 10 per 100k. South Korea was first, on 2 March 2020. Vanuatu was last, on 6 March 2022.
- 147 countries crossed 1,000 per 100k before the data stops.
- Western Sahara, North Korea and Turkmenistan report no cases in the dataset, so their dots stay grey.

Controls: **Play / Pause**, a date slider, a speed selector (1x, 2x, 4x), a country search box, a **Reset view** button, and a detail panel with milestone dates, rank among countries, and a weekly new-cases chart per 100,000 people.

## How it's built

```
Google COVID-19 Open Data (public CSV tables)
        |
        v   AWS CloudShell: Python scripts filter to countries,
        |   find milestone dates, build weekly series
        v
   data.js  +  series.js   (static files, about 190 KB in total)
        |
        v
   index.html  (MapLibre GL JS 4.7.1, loaded from the jsDelivr CDN, draws the map)
        |
        v   basemap style and tiles, requested with an API key
   https://maps.geo.${REGION}.amazonaws.com  (Amazon Location Service)
        |
        v
   AWS Amplify Hosting (public HTTPS link)
```

### AWS services used

| Service | What it does here |
| --- | --- |
| Amazon Location Service | Serves the vector basemap (Standard style, Dark colour scheme) from `maps.geo.${REGION}.amazonaws.com` through an API key restricted to the live site's address. |
| AWS CloudShell | Runs the Python data pipeline that turns the raw Google tables into the two small data files. |
| AWS Amplify Hosting | Hosts the static site over HTTPS. |

The page requests the basemap directly from the Amazon Location Service endpoint, using the style URL:

```
https://maps.geo.${REGION}.amazonaws.com/v2/styles/Standard/descriptor?key=${API_KEY}&color-scheme=Dark
```

The country search is client-side over the data in `data.js`. It does not call a place-search API. The only third-party script the page loads is MapLibre GL JS 4.7.1 from the jsDelivr CDN; everything else is in the repository.

## Data

- **Source:** [Google COVID-19 Open Data](https://health.google.com/covid-19/open-data/) (the epidemiology, index, geography and demographics tables). The project stopped updating on 15 September 2022, so the map ends there.
- **Population:** from the same dataset. Locations under 100,000 people are left out.
- **Milestone dates** are the first day a country's cumulative reported cases per 100,000 people reached 10, 100 or 1,000. The cumulative column is not monotonic (corrections cause dips), so the dates use a running maximum.
- **`data.js`** holds 198 countries: code, name, coordinates, population and the three milestone dates.
- **`series.js`** holds a weekly cumulative case series for each of those 198 countries (142 weekly points each).
- **Canada:** the national series was rebuilt by summing its provinces and territories.
- **Coordinates** are the dataset's own country points, so some dots (for example Sri Lanka) sit at a coarse central location rather than a capital. Four countries with no coordinates in the dataset (Armenia, Georgia, Macedonia, Palestine) were placed by hand.

The source data combines many providers, each with its own terms. Check the original terms in the [Google COVID-19 Open Data repository](https://github.com/GoogleCloudPlatform/covid-19-open-data) before reusing the data. The vaccination access table is not used in this project.

### Limits to keep in mind

Reported cases depend on how much testing a country did, and countries report in different ways, so the map shows **when reporting crossed a line, not true infection levels**. Countries that tested little cross the lines later than their real situation.

## Run it locally

1. Create an Amazon Location Service API key for the **Maps** actions and note its region.
2. In `index.html`, set the two constants near the top of the script:
   ```js
   const API_KEY = "YOUR_AMAZON_LOCATION_API_KEY";
   const REGION = "ap-southeast-1"; // must match the region of your key
   ```
   The page uses them to build the basemap URL `https://maps.geo.${REGION}.amazonaws.com/v2/styles/Standard/descriptor?key=${API_KEY}&color-scheme=Dark`.
3. Restrict the key to the addresses you use (for example `http://127.0.0.1:5500/*` for local testing and your deployed domain).
4. Serve the folder with any static server (for example the VS Code Live Server extension) and open it. Opening `index.html` straight from disk does not work, because the key is restricted by referrer.

The map is capped at zoom 4.9 because the basemap has no tiles at zoom 5 and above over land.

## Rebuild the data

The pipeline ran in AWS CloudShell. Scripts are in `pipeline/`, in this order:

1. `filter_epi.py` streams the epidemiology table and keeps national rows only.
2. `build_countries.py` joins names, coordinates and population.
3. `build_waves.py` finds the milestone dates (with `patch_canada.py` applied for Canada).
4. `make_data_js.py` writes `data.js`.
5. `make_series_js.py` writes `series.js`.

## Repository layout

```
index.html      the map page
data.js         country list and milestone dates
series.js       weekly cumulative case series
pipeline/       Python scripts used to build the data files
```

## Licence

This project is licensed under the MIT License.
