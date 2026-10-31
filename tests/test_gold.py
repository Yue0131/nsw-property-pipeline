from datetime import date

from pipeline.gold import to_dealings

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