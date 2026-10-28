import shutil

from pathlib import Path

import pandas as pd

from pipeline.bronze import file_sha256, write_bronze, ingest_new_files

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

def make_raw_dir(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    shutil.copy(FIXTURE, raw)
    return raw


def test_second_run_skips_ingested_files(tmp_path):
    raw = make_raw_dir(tmp_path)
    bronze = tmp_path / "bronze"
    assert ingest_new_files(list(raw.glob("*.DAT")), bronze, INGESTED_AT) == [FIXTURE.name]
    assert ingest_new_files(list(raw.glob("*.DAT")), bronze, INGESTED_AT) == []


def test_changed_file_is_ingested_again(tmp_path):
    raw = make_raw_dir(tmp_path)
    bronze = tmp_path / "bronze"
    ingest_new_files(list(raw.glob("*.DAT")), bronze, INGESTED_AT)
    copy = raw / FIXTURE.name
    copy.write_text(copy.read_text().replace("750000", "760000"))
    assert ingest_new_files(list(raw.glob("*.DAT")), bronze, INGESTED_AT) == [FIXTURE.name]
    assert len(pd.read_csv(bronze / "_manifest.csv")) == 2


def test_rewriting_a_file_gives_same_bronze(tmp_path):
    write_bronze(FIXTURE, tmp_path, INGESTED_AT)
    files_before = sorted(tmp_path.rglob("*.parquet"))
    b_before = pd.read_parquet(tmp_path / "record_type=B" / f"{FIXTURE.stem}.parquet")
    write_bronze(FIXTURE, tmp_path, INGESTED_AT)
    assert sorted(tmp_path.rglob("*.parquet")) == files_before
    pd.testing.assert_frame_equal(
        pd.read_parquet(tmp_path / "record_type=B" / f"{FIXTURE.stem}.parquet"), b_before)