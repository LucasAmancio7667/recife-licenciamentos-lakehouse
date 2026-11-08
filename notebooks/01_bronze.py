# Databricks notebook source
from src.io_utils import read_raw_data, write_bronze
from pyspark.sql import functions as F

df_urbanistico = read_raw_data(spark, "/Volumes/workspace/raw/raw_empresas_recife/resources_39927a3d-3235-436a-9dc8-df7f4ea3b720_licenciamento_urbanistico.csv")   
df_ambiental = read_raw_data(spark, "/Volumes/workspace/raw/raw_empresas_recife/resources_982d6c85-906a-4ea8-90e0-31f55eac63f9_licenciamento_ambiental.csv")
df_sanitario = read_raw_data(spark, "/Volumes/workspace/raw/raw_empresas_recife/resources_d09900c8-14f2-4dc4-a128-b73a514ec791_licenciamento_sanitario.csv")


# COMMAND ----------

df_empresas_ativas = spark.read.option("delimiter", ";").option("header", "true").option("escape", '"').csv("/Volumes/workspace/raw/raw_empresas_recife/resources_6d5e72aa-3f4b-4dc3-817c-0e0305cef538_empresasativender.csv")
df_empresas_ativas = df_empresas_ativas.withColumn("_source_file", F.col("_metadata.file_name"))

df_empresas_inativas = spark.read.option("delimiter", ";").option("header", "true").option("escape", '"').csv("/Volumes/workspace/raw/raw_empresas_recife/resources_e080550e-7238-444b-a821-8f5acfd82df2_empresasinativender.csv")
df_empresas_inativas = df_empresas_inativas.withColumn("_source_file", F.col("_metadata.file_name"))

# COMMAND ----------

df_empresas = df_empresas_ativas.unionByName(df_empresas_inativas).withColumn("_ingestion_ts", F.current_timestamp())
df_empresas.show()


# COMMAND ----------

write_bronze(df_urbanistico, "workspace.bronze.bronze_urbanistico")
write_bronze(df_ambiental, "workspace.bronze.bronze_ambiental")
write_bronze(df_sanitario, "workspace.bronze.bronze_sanitario")
write_bronze(df_empresas, "workspace.bronze.bronze_empresas")

# COMMAND ----------

for t in ["urbanistico", "ambiental", "sanitario", "empresas"]:
    df = spark.table(f"workspace.bronze.bronze_{t}")   
    print(t, df.count(), len(df.columns))
    df.select("_source_file").distinct().show(truncate=False)