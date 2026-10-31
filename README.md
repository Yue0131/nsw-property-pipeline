# NSW Property Sales Pipeline

> Work in progress. A batch data pipeline that ingests weekly NSW property sales data, cleans and quality-checks it, and produces suburb-level quarterly price and volume metrics.

## Problem
<!-- What question does this answer, and why does it need a pipeline rather than a one-off notebook? -->

## Data
- Source: NSW Valuer General, [Bulk Property Sales Information](https://valuation.property.nsw.gov.au/embed/propertySalesInformation) (weekly `.DAT` files per Local Government Area, 2001 onwards; yearly files 1990–2001).
- Licence: [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/), as stated on the official page (checked 2026-10-26). Used here for non-commercial, educational purposes only.
- **No raw or processed data is stored in this repository.** Run the pipeline locally to reproduce results.
- © State of New South Wales through the NSW Valuer General. The Valuer General does not guarantee the completeness or accuracy of the data.

## Architecture
<!-- Diagram: raw → bronze → silver → gold, with what happens at each layer. -->

## Project structure

```
nsw-property-pipeline/
├── src/pipeline/
│   ├── parse.py          # Parse PSI .DAT files into one table per record type
│   ├── bronze.py         # Write bronze Parquet, manifest for incremental loads
│   ├── run_bronze.py     # Entry point: unzip weekly files and ingest to bronze
│   ├── spark.py          # Local Spark session settings
│   ├── silver.py         # Typing, enrichment, quality rules, deduplication
│   └── run_silver.py     # Entry point: build silver sales and quarantine
├── tests/                # pytest suite (made-up fixture data only)
├── notebooks/            # Phase 1 data exploration
├── docs/
│   ├── data-notes.md     # Source file format and data problems found
│   ├── decisions.md      # Design decisions and trade-offs
│   └── problems-log.md   # Issues hit during development and fixes
└── data/                 # Local only, not in Git (licence: CC BY-NC-ND 4.0)
    ├── raw/              # Weekly zips from NSW Valuer General
    ├── bronze/           # Parsed records as Parquet, all strings
    └── silver/           # Typed, cleaned, deduplicated sales + quarantine
```

## How to run
Requires conda (Python 3.11 and Java 17 for PySpark 3.5).

```bash
conda create -n nsw-pipeline -c conda-forge python=3.11 openjdk=17
conda activate nsw-pipeline
pip install -r requirements.txt
pytest -q
```

1. Download weekly zips in a browser from
   `https://www.valuergeneral.nsw.gov.au/__psi/weekly/YYYYMMDD.zip` (YYYYMMDD = a Monday)
   and put them in `data/raw/`.
2. Build the layers:

```bash
PYTHONPATH=src python -m pipeline.run_bronze   # raw zips -> bronze Parquet
PYTHONPATH=src python -m pipeline.run_silver   # bronze -> silver sales + quarantine
```

## Data quality
<!-- Rules, how failed records are quarantined, and a sample quality report. -->

## Results
<!-- 2–3 charts you made from the gold layer. -->

## Design decisions
See [docs/decisions.md](docs/decisions.md).

## Problems I hit and how I solved them
See [docs/problems-log.md](docs/problems-log.md).

## Limitations and next steps
<!-- Be honest: what this does not handle yet. -->
