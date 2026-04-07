# RealTimeStreaming

A real-time streaming project using PySpark and Docker. The project consists of the following key components:

- **Spark Cluster**: A Dockerized Spark cluster with one master and one worker node.
- **Data Stream Simulation**: A Python socket server that reads Yelp review data from a JSON file and sends it over a socket to mimic a real-time data stream.
- **Spark Streaming Job**: A PySpark script that consumes the data stream, processes it, and outputs the results to the console.

This setup is ideal for learning and testing Spark Streaming in a controlled, real-time environment.

## Features
- Real-time data streaming using PySpark.
- Dockerized Spark cluster with master and worker nodes.
- Socket-based data ingestion.

## Technologies Used
- Apache Spark: For distributed data processing.
- Docker & Docker Compose: For containerizing and managing the Spark cluster.
- Python: For the socket server and Spark streaming job.
- PySpark: Spark’s Python API for streaming and processing.
- Pandas: For handling data in the socket server.

## Configuration
The project no longer depends on machine-specific paths or IP addresses. Configure runtime values with environment variables or CLI flags.

- `STREAM_INPUT_PATH`: path to the review dataset file.
- `STREAM_BIND_HOST`: host/interface for the socket server to bind to. Default: `0.0.0.0`
- `STREAM_SOCKET_HOST`: host the Spark job connects to. Default: `localhost`
- `STREAM_SOCKET_PORT`: shared socket port for both scripts. Default: `9999`
- `STREAM_CHUNK_SIZE`: number of records sent per batch. Default: `2`
- `STREAM_SEND_DELAY_SECONDS`: delay between records. Default: `5`
- `SPARK_MASTER`: optional Spark master URL for the consumer job.
- `SPARK_MASTER_HOST`, `SPARK_MASTER_PORT`, `SPARK_MASTER_WEB_PORT`: optional Docker Compose overrides.
- `OPENAI_API_KEY`: optional API key if you later add OpenAI-backed processing.

Examples:

```bash
STREAM_INPUT_PATH="/path/to/yelp_reviews.json" venv/bin/python src/jobs/streaming-socket.py
```

```bash
STREAM_SOCKET_HOST=127.0.0.1 STREAM_SOCKET_PORT=9999 venv/bin/python src/jobs/spark-streaming.py
```

The socket server now normalizes the dataset path by trimming accidental whitespace, expanding `~`, resolving relative paths, and failing fast with a clear error if the file does not exist.

For a quick end-to-end local check, the repo includes [sample_reviews.json](/Users/macbook/Projects/RealTimeStreaming/src/datasets/Yelp%20JSON/sample_reviews.json). Run the socket server in one terminal:

```bash
venv/bin/python src/jobs/streaming-socket.py --file-path "src/datasets/Yelp JSON/sample_reviews.json" --host 127.0.0.1 --port 9999 --chunk-size 1 --send-delay 0.2
```

Then run the Spark consumer in another:

```bash
venv/bin/python src/jobs/spark-streaming.py --host 127.0.0.1 --port 9999
```

On macOS, the consumer now automatically falls back from Java 23 to Java 21 when Java 21 is installed. You can also set `SPARK_JAVA_HOME` explicitly if needed.
