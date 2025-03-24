from time import sleep

import sys
import os

# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.insert(0, src_dir)

import pyspark
import openai
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when, udf
from pyspark.sql.types import StructType, StructField, StringType, FloatType
from config.config import config
# Add the src directory to the Python path


def start_streaming(spark):
    try:
        # Read streaming data from the socket
        stream_df = spark.readStream.format('socket') \
            .option('host', '192.168.7.144') \
            .option('port', 9999) \
            .load()
        
        schema = StructType([
                StructField("review_id", StringType()),
                StructField("user_id", StringType()),
                StructField("business_id", StringType()),
                StructField("stars", FloatType()),
                StructField("date", StringType()),
                StructField("text", StringType())
            ])

        stream_df = stream_df.select(from_json(col('value'), schema).alias("data")).select("data.*")


        # Write the streaming data to the console
        query = stream_df.writeStream \
            .outputMode('append') \
            .format('console') \
            .option('truncate', False) \
            .start()

        # Keep the query running
        query.awaitTermination()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    spark_conn = SparkSession.builder \
        .appName("SocketStreamConsumer") \
        .getOrCreate()

    start_streaming(spark_conn)