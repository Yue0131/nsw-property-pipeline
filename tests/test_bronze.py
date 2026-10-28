from pathlib import Path

import pandas as pd

from pipeline.bronze import file_sha256, write_bronze

FIXTURE = Path(__file__).parent / "fixtures" / "999_SALES_DATA_NNME_01012026.DAT"
INGESTED_AT = "2026-10-28T00:00:00+00:00"


def test_hash_changes_when_content_changes(tmp_path):
    f = tmp_path / "sample.DAT"
    f.write_text("A;1;\n")
    before = file_sha256(f)
    f.write_text("A;2;\n")
    assert file_sha256(f) != before


def test_write_bronze_adds_lineage_columns(tmp_path):
    counts = write_bronze(FIXTURE, tmp_path, INGESTED_AT)
    assert counts["B"] == 3
    b = pd.read_parquet(tmp_path / "record_type=B" / f"{FIXTURE.stem}.parquet")
    assert set(b["source_file"]) == {FIXTURE.name}
    assert set(b["ingested_at"]) == {INGESTED_AT}