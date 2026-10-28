from pathlib import Path

import pytest

from pipeline.parse import parse_file

FIXTURE = Path(__file__).parent / "fixtures" / "999_SALES_DATA_NNME_01012026.DAT"


def test_row_counts_per_record_type():
    result = parse_file(FIXTURE)
    counts = {rt: len(df) for rt, df in result.items()}
    assert counts == {"A": 1, "B": 3, "C": 4, "D": 7, "Z": 1}


def test_counts_match_z_trailer():
    result = parse_file(FIXTURE)
    z = result["Z"].iloc[0]
    assert int(z["total_b"]) == len(result["B"])
    assert int(z["total_c"]) == len(result["C"])
    assert int(z["total_d"]) == len(result["D"])
    assert int(z["total_records"]) == sum(len(df) for df in result.values())


def test_trailing_delimiter_is_dropped():
    b = parse_file(FIXTURE)["B"]
    assert b.loc[0, "dealing_number"] == "ZZ000001"


def test_d_records_keep_only_documented_fields():
    d = parse_file(FIXTURE)["D"]
    assert list(d.columns)[-1] == "purchaser_vendor"
    assert sorted(d["purchaser_vendor"].unique()) == ["P", "V"]


def test_unknown_record_type_raises(tmp_path):
    bad = tmp_path / "bad.DAT"
    bad.write_text("X;999;\n")
    with pytest.raises(ValueError, match="unknown record type"):
        parse_file(bad)


def test_extra_field_with_value_raises(tmp_path):
    bad = tmp_path / "bad.DAT"
    bad.write_text("D;999;1000001;1;20260101 01:00;P;SURPRISE;\n")
    with pytest.raises(ValueError, match="fields, expected 6"):
        parse_file(bad)