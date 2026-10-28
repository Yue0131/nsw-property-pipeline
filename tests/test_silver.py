from datetime import date

from pipeline.silver import type_sales

COLUMNS = ["contract_date", "settlement_date", "purchase_price",
           "area", "area_type", "pct_interest", "post_code"]


def test_types_are_cast(spark):
    df = spark.createDataFrame([("20260115", "20260220", "750000", "500", "M", "", "0200")], COLUMNS)
    row = type_sales(df).first()
    assert row.contract_date == date(2026, 1, 15)
    assert row.purchase_price == 750000
    assert row.pct_interest == 100
    assert row.post_code == "0200"


def test_hectares_converted_to_square_metres(spark):
    df = spark.createDataFrame([("20260115", "20260220", "1", "2.5", "H", "", "2998")], COLUMNS)
    assert type_sales(df).first().area_sqm == 25000


def test_bad_or_blank_values_become_null(spark):
    df = spark.createDataFrame([("20261399", "  ", "abc", "", "", "", "")], COLUMNS)
    row = type_sales(df).first()
    assert row.contract_date is None
    assert row.settlement_date is None
    assert row.purchase_price is None
    assert row.area_sqm is None