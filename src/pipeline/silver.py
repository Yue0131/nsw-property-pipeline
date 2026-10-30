from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import Window

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

def quality_rules() -> dict:
    """Rule name -> condition that is true when a row breaks the rule."""
    return {
        "missing_dealing_number": F.col("dealing_number").isNull(),
        "missing_property_id": F.col("property_id").isNull(),
        "missing_contract_date": F.col("contract_date").isNull(),
        "contract_before_2001": F.col("contract_date") < F.lit("2001-01-01").cast("date"),
        "settlement_before_contract": F.col("settlement_date") < F.col("contract_date"),
        "price_not_positive": F.col("purchase_price").isNull() | (F.col("purchase_price") <= 0),
    }


def split_quality(df: DataFrame) -> tuple[DataFrame, DataFrame]:
    """Return (good rows, quarantined rows). Quarantined rows list every rule they failed."""
    failed = F.array_compact(F.array(*[
         F.when(condition, F.lit(name)) for name, condition in quality_rules().items()
    ]))
    df = df.withColumn("failed_rules", failed)
    good = df.filter(F.size("failed_rules") == 0).drop("failed_rules")
    bad = df.filter(F.size("failed_rules") > 0)
    return good, bad

def dedupe_sales(df: DataFrame) -> DataFrame:
    """Keep one row per (dealing_number, property_id): the one from the latest download."""
    latest_first = Window.partitionBy("dealing_number", "property_id").orderBy(
        F.col("download_datetime").desc(), F.col("source_file").desc()
    )
    return (
        df.withColumn("_rank", F.row_number().over(latest_first))
        .filter(F.col("_rank") == 1)
        .drop("_rank")
    )