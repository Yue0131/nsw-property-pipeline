from datetime import date

from pipeline.silver import SALE_KEY, enrich_sales, legal_descriptions, party_counts, split_quality, type_sales

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

KEY = ("f1", "999", "1000001", "1")
C_SCHEMA = ("source_file string, district_code string, property_id string, "
            "sale_counter string, record_index long, legal_description string")
D_SCHEMA = ("source_file string, district_code string, property_id string, "
            "sale_counter string, purchaser_vendor string")


def test_legal_description_joined_in_file_order(spark):
    c = spark.createDataFrame([(*KEY, 1, "3456"), (*KEY, 0, "LOT 1 DP 12")], C_SCHEMA)
    assert legal_descriptions(c).first().legal_description == "LOT 1 DP 123456"


def test_party_counts(spark):
    d = spark.createDataFrame([(*KEY, "P"), (*KEY, "V"), (*KEY, "V")], D_SCHEMA)
    row = party_counts(d).first()
    assert (row.purchaser_count, row.vendor_count) == (1, 2)


def test_sale_without_c_or_d_is_kept(spark):
    b = spark.createDataFrame([KEY], SALE_KEY)
    c = spark.createDataFrame([], C_SCHEMA)
    d = spark.createDataFrame([], D_SCHEMA)
    rows = enrich_sales(b, c, d).collect()
    assert len(rows) == 1
    assert rows[0].legal_description is None

Q_SCHEMA = ("dealing_number string, property_id string, contract_date date, "
            "settlement_date date, purchase_price long")
GOOD_ROW = ("AV1", "1", date(2026, 1, 1), date(2026, 2, 1), 500000)
BAD_ROW = (None, "2", date(1926, 1, 1), date(1925, 1, 1), 0)


def test_clean_row_passes(spark):
    good, bad = split_quality(spark.createDataFrame([GOOD_ROW], Q_SCHEMA))
    assert (good.count(), bad.count()) == (1, 0)


def test_bad_row_lists_every_failed_rule(spark):
    good, bad = split_quality(spark.createDataFrame([BAD_ROW], Q_SCHEMA))
    assert good.count() == 0
    assert sorted(bad.first().failed_rules) == [
        "contract_before_2001", "missing_dealing_number",
        "price_not_positive", "settlement_before_contract",
    ]


def test_no_row_is_lost(spark):
    df = spark.createDataFrame([GOOD_ROW, BAD_ROW, GOOD_ROW], Q_SCHEMA)
    good, bad = split_quality(df)
    assert good.count() + bad.count() == df.count()