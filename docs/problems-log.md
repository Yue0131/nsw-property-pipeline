# Problems log

## 2026-10-28 — Bronze did not pick up a schema change
- **Problem:** After adding `record_index` to bronze, re-running ingested 0 files.
- **Cause:** The manifest skips files whose name and hash are unchanged. The code changed, not the files.
- **Fix:** Deleted `data/bronze/` and re-ran (full rebuild). A schema change needs a backfill.

## 2026-10-30 — `fixture 'spark' not found`
- **Problem:** Silver tests could not find the shared Spark session.
- **Cause:** `tests/conftest.py` was missing or misnamed; pytest only loads that exact file name.
- **Fix:** Created `tests/conftest.py` with a session-scoped `spark` fixture.

## 2026-10-30 — `AssertionError` when importing silver.py
- **Problem:** Importing `silver.py` failed inside `F.col(...)`.
- **Cause:** In PySpark 3.5, `F.col` needs an active Spark session. The quality rules were built at
  module level, so they ran on import, before Spark started.
- **Fix:** Wrapped the rules in a function, `quality_rules()`, so they are built when called.

## 2026-10-30 — Deduplication removed real sales
- **Problem:** On real data, deduplication removed 221 rows; exploration suggested about 35.
- **Investigation:** Grouped the repeated keys by number of distinct download times. 35 keys spanned
  two weeks (true repeats). 157 keys were inside one file: several strata lots sold in one dealing
  share the same property_id and differ only by strata_lot_number. unit_number was not reliable.
- **Fix:** Key changed to (dealing_number, property_id, strata_lot_number). Removed rows dropped to
  43: 35 cross-week repeats and 8 sales written twice in the same file. Added a test for strata lots.

## 2026-10-30 — Rows missing from a diagnostic join
- **Problem:** A check listed 8 duplicate groups but the join showed only 1.
- **Cause:** In a Spark join, null never equals null. The other 7 groups had no strata_lot_number.
  (groupBy and window partitions do treat nulls as one group, so the deduplication itself was fine.)
- **Fix:** Filled nulls with a placeholder before joining in the diagnostic.

## 2026-10-31 — Charts showed as links in the README
- **Problem:** The README showed blue links instead of images.
- **Cause:** Markdown images need a leading `!`; without it they are links.
- **Fix:** Added `!` before both image lines.

---

## Block 5 → docs/data-notes.md: append to "Data problems found during exploration"

### Found while building silver (2026-10-30, 4 weeks)
- [x] Strata lots sold in one dealing share one property_id (the strata plan's parent property) and
      differ by strata_lot_number and legal_description, e.g. 7 lots of SP96758 in one dealing.
      unit_number can repeat across lots, so it cannot identify a lot.
- [x] 8 sales appear twice inside the same file, identical except for sale_counter.
- [x] 37 B records have no property_id (required field); they are quarantined.
- [x] 2 contract dates are before 2001 (1926, 1976); quarantined as errors.
