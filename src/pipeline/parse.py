from collections import defaultdict
from pathlib import Path

import pandas as pd

B_COLUMNS = [
    "record_type", "district_code", "property_id", "sale_counter", "download_datetime",
    "property_name", "unit_number", "house_number", "street_name", "locality",
    "post_code", "area", "area_type", "contract_date", "settlement_date",
    "purchase_price", "zoning", "nature_of_property", "primary_purpose",
    "strata_lot_number", "component_code", "sale_code", "pct_interest", "dealing_number",
]
LINK = ["record_type", "district_code", "property_id", "sale_counter", "download_datetime"]
COLUMNS = {
    "A": ["record_type", "file_type", "district_code", "download_datetime", "submitter_user_id"],
    "B": B_COLUMNS,
    "C": LINK + ["legal_description"],
    "D": LINK + ["purchaser_vendor"],
    "Z": ["record_type", "total_records", "total_b", "total_c", "total_d"],
}

def split_line(line: str, path: Path, line_no: int) -> tuple[str, list[str]]:
    """Split one line into (record_type, fields), checking it against COLUMNS."""
    fields = line.split(";")[:-1]  # every line ends with ';'
    record_type = fields[0]
    if record_type not in COLUMNS:
        raise ValueError(f"{path.name} line {line_no}: unknown record type {record_type!r}")
    expected = len(COLUMNS[record_type])
    if len(fields) < expected or any(fields[expected:]):
        raise ValueError(f"{path.name} line {line_no}: {len(fields)} fields, expected {expected}")
    return record_type, fields[:expected]

def parse_file(path: Path) -> dict[str, pd.DataFrame]:
    """Parse one PSI .DAT file into one DataFrame per record type (all values as strings)."""
    rows = defaultdict(list)
    for line_no, line in enumerate(path.read_text(encoding="ascii").splitlines(), start=1):
        if not line:
            continue
        record_type, fields = split_line(line, path, line_no)
        rows[record_type].append(fields)
    return {rt: pd.DataFrame(rows[rt], columns=cols) for rt, cols in COLUMNS.items()}