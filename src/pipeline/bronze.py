import hashlib
from pathlib import Path

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