from pyspark.sql import SparkSession, functions as F, Window
import datetime, json

spark = SparkSession.builder.appName("bus-kpi").getOrCreate()
raw = spark.read.json("scraper/data/raw/*.json")

raw = raw.withColumn("snapshot_ts", F.to_timestamp("snapshot_ts")) \
         .withColumn("eta", F.to_timestamp("data.eta"))

w = Window.partitionBy("route","stop").orderBy("snapshot_ts")
arrived = raw.where(raw.eta.isNull() & F.lead("eta").over(w).isNotNull()) \
             .select("route","stop",F.col("snapshot_ts").alias("actual_ts"))

pred = raw.withColumn("delta",F.col("eta").cast("long")-F.col("snapshot_ts").cast("long")) \
          .where("delta between 0 and 60") \
          .withColumnRenamed("snapshot_ts","pred_ts") \
          .select("route","stop","pred_ts")

events = arrived.join(pred,["route","stop"]) \
           .withColumn("delay_sec",F.col("actual_ts").cast("long")-F.col("pred_ts").cast("long"))

cut = datetime.datetime.utcnow() - datetime.timedelta(hours=6)
kpi = (events.where(F.col("actual_ts")>=cut)
      .groupBy("route")
      .agg(
        (F.sum((F.abs("delay_sec")<=60).cast("int"))/F.count("*")).alias("punctual"),
        F.sum((F.abs("delay_sec")>300).cast("int")).alias("delay5")
      ))

# Write out JSON array
out = [row.asDict() for row in kpi.collect()]
with open("frontend/data/agg/kpi.json","w") as f:
    json.dump(out, f, indent=2)
