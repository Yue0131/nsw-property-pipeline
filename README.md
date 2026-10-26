# NSW Property Sales Pipeline

> Work in progress. A batch data pipeline that ingests weekly NSW property sales data, cleans and quality-checks it, and produces suburb-level quarterly price and volume metrics.

## Problem
<!-- What question does this answer, and why does it need a pipeline rather than a one-off notebook? -->

## Data
- Source: NSW Valuer General, Bulk Property Sales Information (weekly `.DAT` files, 1990 onwards).
- Licence: see the NSW Government property sales information page. Used here for non-commercial, educational purposes. **No raw or processed data is stored in this repository.**

## Architecture
<!-- Diagram: raw → bronze → silver → gold, with what happens at each layer. -->

## How to run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
# python -m pipeline run   (coming soon)
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
