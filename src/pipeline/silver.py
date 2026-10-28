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


SALE_KEY = ["source_file", "district_code", "property_id", "sale_counter"]


def legal_descriptions(c: DataFrame) -> DataFrame:
    """Join each sale's C records into one legal description, in file order."""
    ordered = F.sort_array(F.collect_list(F.struct("record_index", "legal_description")))
    return c.groupBy(SALE_KEY).agg(
        F.concat_ws("", F.transform(ordered, lambda x: x["legal_description"]))
        .alias("legal_description")
    )


def party_counts(d: DataFrame) -> DataFrame:
    """Count purchasers and vendors per sale."""
    return d.groupBy(SALE_KEY).agg(
        F.sum(F.when(F.col("purchaser_vendor") == "P", 1).otherwise(0)).alias("purchaser_count"),
        F.sum(F.when(F.col("purchaser_vendor") == "V", 1).otherwise(0)).alias("vendor_count"),
    )


def enrich_sales(b: DataFrame, c: DataFrame, d: DataFrame) -> DataFrame:
    """Attach legal description and party counts to each sale. Left joins keep every sale."""
    return (
        b.join(legal_descriptions(c), SALE_KEY, "left")
        .join(party_counts(d), SALE_KEY, "left")
    )