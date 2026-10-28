from pyspark.sql import SparkSession


def get_spark(app_name: str = "nsw-pipeline") -> SparkSession:
    """Create (or reuse) a local Spark session."""
    return (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.sql.legacy.timeParserPolicy", "CORRECTED")
        .getOrCreate()
    )