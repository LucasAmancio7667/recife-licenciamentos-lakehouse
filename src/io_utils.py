from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

def read_raw_data(spark: SparkSession, path: str) -> DataFrame:
    df = (
        spark.read
        .option("delimiter", ";")
        .option("header", "true")
        .option("escape", '"')
        .csv(path)
    )
    return (
        df
        .withColumn("_ingestion_ts", F.current_timestamp())
        .withColumn("_source_file", F.col("_metadata.file_name"))
    )


def write_bronze(df: DataFrame, table_name: str) -> None:
    (
        df.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(table_name)
    )