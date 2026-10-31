from datetime import date

from pipeline.gold import suburb_quarter_metrics, to_dealings

SALES_SCHEMA = ("dealing_number string, purchase_price long, contract_date date, "
                "locality string, post_code string, nature_of_property string, pct_interest int")


def test_multi_property_dealing_counted_once(spark):
    rows = [("AV1", 900000, date(2026, 2, 15), "SAMPLEVILLE", "2999", "R", 100)] * 3
    result = to_dealings(spark.createDataFrame(rows, SALES_SCHEMA)).collect()
    assert len(result) == 1
    assert result[0].property_count == 3
    assert result[0].purchase_price == 900000


def test_separate_dealings_stay_separate(spark):
    rows = [
        ("AV1", 500000, date(2026, 2, 15), "SAMPLEVILLE", "2999", "R", 100),
        ("AV2", 600000, date(2026, 2, 16), "SAMPLEVILLE", "2999", "R", 100),
    ]
    assert to_dealings(spark.createDataFrame(rows, SALES_SCHEMA)).count() == 2


def test_quarter_label(spark):
    rows = [("AV1", 500000, date(2026, 11, 3), "SAMPLEVILLE", "2999", "R", 100)]
    assert to_dealings(spark.createDataFrame(rows, SALES_SCHEMA)).first().contract_quarter == "2026-Q4"

DEALINGS_SCHEMA = ("locality string, contract_quarter string, property_count long, "
                   "nature_of_property string, pct_interest int, purchase_price long")


def home(price, suburb="SAMPLEVILLE"):
    return (suburb, "2026-Q1", 1, "R", 100, price)


def test_median_uses_only_typical_homes(spark):
    rows = [home(p) for p in (100, 200, 300, 400, 500)] + [
        ("SAMPLEVILLE", "2026-Q1", 1, "V", 100, 9000000),  # vacant land
        ("SAMPLEVILLE", "2026-Q1", 3, "R", 100, 9000000),  # multi-property dealing
        ("SAMPLEVILLE", "2026-Q1", 1, "R", 50, 9000000),   # partial interest
    ]
    row = suburb_quarter_metrics(spark.createDataFrame(rows, DEALINGS_SCHEMA)).first()
    assert row.sales_count == 8
    assert row.median_sample_size == 5
    assert row.median_price == 300


def test_median_empty_when_too_few_sales(spark):
    rows = [home(100), home(200)]
    row = suburb_quarter_metrics(spark.createDataFrame(rows, DEALINGS_SCHEMA)).first()
    assert row.sales_count == 2
    assert row.median_price is None


def test_suburbs_are_separate(spark):
    rows = [home(100, "A"), home(200, "B"), home(300, "B")]
    df = suburb_quarter_metrics(spark.createDataFrame(rows, DEALINGS_SCHEMA))
    counts = {r.locality: r.sales_count for r in df.collect()}
    assert counts == {"A": 1, "B": 2}