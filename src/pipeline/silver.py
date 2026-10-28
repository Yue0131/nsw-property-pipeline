from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def blank_to_null(df: DataFrame) -> DataFrame:
    """Trim every column and turn empty strings into nulls."""
    return df.select([
        F.when(F.trim(F.col(c)) == "", None).otherwise(F.trim(F.col(c))).alias(c)
        for c in df.columns
    ])


def type_sales(df: DataFrame) -> DataFrame:
    """Cast bronze B records to proper types. Unparseable values become null."""
    df = blank_to_null(df)
    return (
        df.withColumn("contract_date", F.to_date("contract_date", "yyyyMMdd"))
        .withColumn("settlement_date", F.to_date("settlement_date", "yyyyMMdd"))
        .withColumn("purchase_price", F.col("purchase_price").cast("long"))
        .withColumn("area", F.col("area").cast("double"))
        .withColumn(
            "area_sqm",
            F.when(F.col("area_type") == "H", F.col("area") * 10000)
            .when(F.col("area_type") == "M", F.col("area")),
        )
        .withColumn("pct_interest", F.coalesce(F.col("pct_interest").cast("int"), F.lit(100)))
    )