#!/usr/bin/env python3
"""
Build & clean all data artifacts for the Canadian Commute Explorer.

Runs the full pipeline, in order:
  1. data_cleaning           -> assets/test_output.geojson      (intermediate)
                                assets/test_output_2.geojson    (served by the app)
                                assets/cma_ct_travel_stats_agg.json
  2. generate_cma_centroids  -> assets/cma_bounds.json

Required inputs (must exist before running):
  - CTTravelByMode.csv
  - assets/census_2021_shapes.geojson

Usage (locally or in the Railway build phase):
  python build_data.py
"""
import os
import sys
import time

# Always run from the project root so the pipeline's relative paths resolve,
# no matter what directory the build system invokes us from.
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

REQUIRED_INPUTS = [
    "CTTravelByMode.csv",
    "assets/census_2021_shapes.geojson",
]

EXPECTED_OUTPUTS = [
    "assets/test_output_2.geojson",
    "assets/cma_ct_travel_stats_agg.json",
    "assets/cma_bounds.json",
]


def main():
    start = time.time()
    print(">>> [build_data] Starting data build in:", ROOT)

    missing = [f for f in REQUIRED_INPUTS if not os.path.exists(f)]
    if missing:
        print("!!! [build_data] Missing required input file(s):", ", ".join(missing))
        print("    Make sure these are committed / present before building.")
        sys.exit(1)

    # Step 1 — cleaning + merge into GeoJSON.
    # Importing the module executes its top-level pipeline.
    print(">>> [build_data] Step 1/2: cleaning census data & merging into GeoJSON ...")
    import data_cleaning  # noqa: F401

    # Step 2 — CMA centroids / map bounds.
    print(">>> [build_data] Step 2/2: generating CMA centroids & bounds ...")
    import generate_cma_centroids  # noqa: F401

    missing_out = [f for f in EXPECTED_OUTPUTS if not os.path.exists(f)]
    if missing_out:
        print("!!! [build_data] Build finished but expected output(s) missing:",
              ", ".join(missing_out))
        sys.exit(1)

    elapsed = time.time() - start
    print(f">>> [build_data] Done in {elapsed:.1f}s. Runtime artifacts ready:")
    for f in EXPECTED_OUTPUTS:
        size_mb = os.path.getsize(f) / 1_000_000
        print(f"      - {f}  ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
