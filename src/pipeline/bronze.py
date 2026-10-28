import hashlib
from pathlib import Path
import pandas as pd
from pipeline.parse import parse_file


def file_sha256(path: Path) -> str:
    """Return the SHA-256 hash of a file's bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_bronze(path: Path, bronze_dir: Path, ingested_at: str) -> dict[str, int]:
    """Parse one .DAT file and write one Parquet file per record type.

    Returns the number of rows written per record type.
    """
    counts = {}
    for record_type, df in parse_file(path).items():
        df["source_file"] = path.name
        df["ingested_at"] = ingested_at
        out = bronze_dir / f"record_type={record_type}" / f"{path.stem}.parquet"
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(out, index=False)
        counts[record_type] = len(df)
    return counts

MANIFEST_COLUMNS = ["source_file", "sha256", "ingested_at", "b_rows"]


def ingest_new_files(raw_files: list[Path], bronze_dir: Path, ingested_at: str) -> list[str]:
    """Write bronze for files whose (name, hash) is not in the manifest yet.

    Returns the names of the files ingested in this run.
    """
    manifest_path = bronze_dir / "_manifest.csv"
    old_rows = []
    if manifest_path.exists():
        old_rows = pd.read_csv(manifest_path, dtype=str).to_dict("records")
    seen = {(row["source_file"], row["sha256"]) for row in old_rows}

    new_rows = []
    for path in sorted(raw_files):
        digest = file_sha256(path)
        if (path.name, digest) in seen:
            continue
        counts = write_bronze(path, bronze_dir, ingested_at)
        new_rows.append({"source_file": path.name, "sha256": digest,
                         "ingested_at": ingested_at, "b_rows": counts["B"]})

    if new_rows:
        bronze_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(old_rows + new_rows, columns=MANIFEST_COLUMNS).to_csv(manifest_path, index=False)
    return [row["source_file"] for row in new_rows]