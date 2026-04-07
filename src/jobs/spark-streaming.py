import argparse
import os
import subprocess
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import FloatType, StringType, StructField, StructType

# Add the src directory to the Python path.
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.insert(0, src_dir)

from config.config import config


def configure_java_home():
    configured_java_home = os.getenv("SPARK_JAVA_HOME")
    if configured_java_home:
        os.environ["JAVA_HOME"] = configured_java_home
        return

    current_java_home = os.getenv("JAVA_HOME", "")
    if sys.platform != "darwin" or "23." not in current_java_home:
        return

    try:
        detected_java_home = subprocess.run(
            ["/usr/libexec/java_home", "-v", "21"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return

    if detected_java_home:
        os.environ["JAVA_HOME"] = detected_java_home


def parse_args():
    parser = argparse.ArgumentParser(
        description="Consume review events from a socket and print them with Spark Structured Streaming."
    )
    parser.add_argument(
        "--host",
        default=config["streaming"]["socket_host"],
        help="Socket host to connect to.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=config["streaming"]["socket_port"],
        help="Socket port to connect to.",
    )
    parser.add_argument(
        "--spark-master",
        default=config["spark"]["master"],
        help="Optional Spark master URL such as spark://spark-master:7077.",
    )
    return parser.parse_args()


def build_spark_session(master_url=None):
    builder = SparkSession.builder.appName("SocketStreamConsumer")
    if master_url:
        builder = builder.master(master_url)
    return builder.getOrCreate()


def start_streaming(spark, host, port):
    try:
        stream_df = (
            spark.readStream.format("socket")
            .option("host", host)
            .option("port", port)
            .load()
        )

        schema = StructType(
            [
                StructField("review_id", StringType()),
                StructField("user_id", StringType()),
                StructField("business_id", StringType()),
                StructField("stars", FloatType()),
                StructField("date", StringType()),
                StructField("text", StringType()),
            ]
        )

        parsed_df = stream_df.select(from_json(col("value"), schema).alias("data")).select(
            "data.*"
        )

        query = (
            parsed_df.writeStream.outputMode("append")
            .format("console")
            .option("truncate", False)
            .start()
        )
        query.awaitTermination()
    except KeyboardInterrupt:
        print("Streaming stopped.")
    except Exception as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    configure_java_home()
    args = parse_args()
    spark_conn = build_spark_session(args.spark_master)
    start_streaming(spark_conn, args.host, args.port)
