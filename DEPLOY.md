# Deploying the Canadian Commute Explorer to Railway

This app is a Dash (Flask) application. On Railway it is built with **Nixpacks**,
which installs the Python dependencies, **regenerates the map data during the
build**, and then serves the app with **gunicorn**.

## What was added for deployment

| File | Purpose |
|------|---------|
| `requirements.txt` | App + data-pipeline + gunicorn dependencies (pinned). |
| `build_data.py` | One command that runs the full data pipeline (clean → merge → centroids). |
| `nixpacks.toml` | Runs `build_data.py` in the build phase; starts gunicorn in the start phase. |
| `railway.json` | Tells Railway to use the Nixpacks builder and sets a restart policy. |
| `.gitignore` (updated) | Ignores the **generated** data files (they are rebuilt on every deploy). |

The production start command (in `nixpacks.toml`) is:

```
gunicorn app:server --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120
```

`app:server` refers to the Flask `server` object exposed in `app.py`. Railway
provides the `$PORT` value automatically — you do **not** need to set it.

## Data: built on Railway

The pipeline is run during the build so its outputs are baked into the image and
visible to the running web process. It produces:

- `assets/test_output_2.geojson` (~36 MB, the layer the map draws)
- `assets/cma_ct_travel_stats_agg.json` (KPI aggregates)
- `assets/cma_bounds.json` (map zoom bounds)

These are now git-ignored on purpose — they are regenerated every deploy from the
two **source** inputs, which must stay committed:

- `CTTravelByMode.csv`
- `assets/census_2021_shapes.geojson` (~77 MB)

> Note: GDAL is **not** required. The old `osgeo` import was unused and has been
> removed, so the build needs no system packages.

## One-time git cleanup (run locally first)

A few generated files were previously tracked. Stop tracking them so Railway
rebuilds them cleanly:

```bash
git rm --cached assets/test_output.geojson \
                assets/test_output_2.geojson \
                assets/cma_ct_travel_stats_agg.json

git add .gitignore requirements.txt build_data.py nixpacks.toml railway.json \
        app.py cma_transit_mode_header.py cma_ca_label_generate.py \
        generate_cma_centroids.py assets/additional_styles.css \
        CTTravelByMode.csv assets/census_2021_shapes.geojson

git commit -m "Add Railway deploy config + build-on-deploy data pipeline"
```

## Option A — Deploy from GitHub (recommended)

1. Push the repo to GitHub. The 77 MB `census_2021_shapes.geojson` is under
   GitHub's 100 MB hard limit but over the 50 MB warning threshold — the push
   will succeed with a warning. (If you'd rather not store it in normal git,
   track it with **Git LFS**, or use Option B.)
2. In the Railway dashboard: **New Project → Deploy from GitHub repo** and pick
   this repo.
3. Railway detects `nixpacks.toml` / `railway.json` and builds automatically.
   Watch the build logs — you should see the `>>> [build_data]` lines and
   `Done in …s. Runtime artifacts ready`.
4. When the deploy is green, open **Settings → Networking → Generate Domain** to
   get a public URL.

Every `git push` to the connected branch triggers a fresh build (and a fresh
data rebuild).

## Option B — Deploy with the Railway CLI

This uploads your working directory directly, so GitHub file-size limits don't
apply.

```bash
npm i -g @railway/cli      # or: brew install railway
railway login
railway init               # create / link a project
railway up                 # build + deploy from the current folder
railway domain             # generate a public URL
```

## Resource sizing

- **Build:** the pipeline peaks at roughly **~0.9 GB RAM** (it loads the 77 MB
  source GeoJSON into memory). Railway's build environment handles this fine.
- **Runtime:** each time a user picks a topic, the app reads the ~36 MB GeoJSON,
  which transiently uses a few hundred MB per worker. If you see out-of-memory
  restarts on a small instance, either drop to `--workers 1` in `nixpacks.toml`
  or bump the service's memory in Railway.

## Local development is unchanged

```bash
python build_data.py     # (re)build the data once
python3 -m app           # dev server at http://127.0.0.1:8050
```

## Quick troubleshooting

- **Build fails on a missing input** → confirm `CTTravelByMode.csv` and
  `assets/census_2021_shapes.geojson` are committed.
- **App boots but the map/KPIs are empty** → the build step didn't run; confirm
  `nixpacks.toml` is in the repo root and check the build logs for `[build_data]`.
- **502 / worker timeout right after deploy** → first request reads a large file;
  the `--timeout 120` already accounts for this, but a very small instance may
  need a memory bump.
