"""Build silver sales from bronze: type, enrich, quality-check, deduplicate."""
from pathlib import Path

from pyspark.sql import functions as F

from pipeline.silver import dedupe_sales, enrich_sales, split_quality, type_sales
from pipeline.spark import get_spark

BRONZE_DIR = Path("data/bronze")
SALES_DIR = Path("data/silver/sales")
QUARANTINE_DIR = Path("data/silver/quarantine")


def main() -> None:
    spark = get_spark()
    b, c, d = (spark.read.parquet(str(BRONZE_DIR / f"record_type={rt}")) for rt in "BCD")

    sales = enrich_sales(type_sales(b.drop("record_type", "record_index")), c, d)
    good, quarantine = split_quality(sales)
    silver = dedupe_sales(good).withColumn("contract_year", F.year("contract_date"))

    silver.write.mode("overwrite").partitionBy("contract_year").parquet(str(SALES_DIR))
    quarantine.write.mode("overwrite").parquet(str(QUARANTINE_DIR))

    total = b.count()
    n_quarantine = spark.read.parquet(str(QUARANTINE_DIR)).count()
    n_silver = spark.read.parquet(str(SALES_DIR)).count()
    print(f"Bronze B rows: {total}")
    print(f"Quarantined: {n_quarantine}")
    print(f"Silver rows: {n_silver}")
    print(f"Duplicates removed: {total - n_quarantine - n_silver}")
    (spark.read.parquet(str(QUARANTINE_DIR))
     .select(F.explode("failed_rules").alias("rule"))
     .groupBy("rule").count().orderBy("rule").show(truncate=False))


if __name__ == "__main__":
    main()