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