# RealTimeStreaming

This is a small data engineering project where I simulate a real-time review stream and process it with Spark Structured Streaming.

Instead of waiting for a live production source, I use Yelp-style review data in a file, send it over a socket as if it were arriving in real time, and let Spark consume and parse the stream inside a Dockerized cluster.

## Problem I Am Solving

One common data engineering problem is this:

How do I process events continuously as they arrive instead of waiting for a full batch file?

In a real business setting, reviews, clicks, orders, and logs do not arrive once a day in one neat file. They arrive little by little. Because of that, I wanted to build a simple project that shows the core streaming pattern:

- a producer generates events
- a stream carries those events
- a processing engine reads them continuously
- the system turns raw JSON into structured data

This project is my simplified version of that idea.

## Why I Chose This Design

I chose this structure on purpose because I wanted something that is easy to understand, easy to run locally, and still close enough to a real streaming pipeline to show the main engineering ideas.

### Current flow

1. A Python socket server reads review records from a JSON file.
2. It sends those records one by one over TCP.
3. A Spark Structured Streaming job reads the socket stream.
4. Spark parses the JSON into columns and prints the structured output.
5. Everything runs inside Docker using a Spark master and worker.

## Why I Did Not Use a Live Yelp API

At first, an API-based design sounds more realistic. But for this project, I decided the file-based stream is the better choice.

Why:

- it is reproducible
- it works offline
- it avoids API rate limits and authentication issues
- it is easier to demo and test
- it lets me focus on streaming and processing, not API restrictions

Public APIs are often limited and unreliable for a learning project like this. A local dataset gives me control over the data, the pace of the stream, and the testing process.

So the stream is still "real-time" in behavior, but the source is simulated from a file.

## Project Structure

- [src/jobs/streaming-socket.py](/Users/macbook/Projects/RealTimeStreaming/src/jobs/streaming-socket.py): reads newline-delimited JSON and streams it over a socket
- [src/jobs/spark-streaming.py](/Users/macbook/Projects/RealTimeStreaming/src/jobs/spark-streaming.py): Spark consumer that reads the socket stream and parses JSON into structured columns
- [src/config/config.py](/Users/macbook/Projects/RealTimeStreaming/src/config/config.py): central configuration for paths, ports, and Spark settings
- [src/docker-compose.yml](/Users/macbook/Projects/RealTimeStreaming/src/docker-compose.yml): Dockerized Spark master and worker setup
- [src/datasets/Yelp JSON/sample_reviews.json](/Users/macbook/Projects/RealTimeStreaming/src/datasets/Yelp%20JSON/sample_reviews.json): small sample dataset for testing the pipeline end to end

## What This Project Demonstrates

This project demonstrates a few important data engineering ideas:

- streaming data instead of batch-only processing
- separating producer and consumer responsibilities
- schema-based parsing of raw JSON
- containerized distributed processing with Spark
- running the same pipeline in a repeatable local environment

Even though the project is small, the structure is very similar to how real streaming systems are designed.

## Trade-Offs I Accepted

Every project has trade-offs. I kept this one intentionally simple, so I accepted a few limitations.

### What I gain with the current design

- simple to explain
- simple to run
- easy to debug
- works well for learning and demos
- no external dependency on a live source

### What I lose with the current design

- the socket source is not production-grade
- the stream is simulated, not truly live
- there is no message durability or replay support like Kafka
- the output currently goes to the console instead of storage
- there is no orchestration, monitoring, or alerting

So this is a good project for understanding streaming fundamentals, but not yet a production-ready pipeline.

## Why Spark Structured Streaming

I used Spark Structured Streaming because it is a strong choice when I want to process streaming data using a DataFrame model.

It gives me:

- a clear schema
- SQL/DataFrame-style transformations
- easy scaling from local to cluster mode
- a very common tool used in data engineering

For a project like this, Spark is a good middle ground between learning value and practical relevance.

## Why Docker

I used Docker so the project behaves the same way every time I run it.

Without Docker, Spark and Java setup can become messy very quickly. With Docker, I can start the cluster, mount my code and dataset, and test the full flow in a more controlled environment.

That makes the project easier to share, easier to reproduce, and easier to explain.

## Current Limitations

Right now, the project works, but it is still a foundation project rather than a finished production pipeline.

Main limitations:

- the current dataset in the repo is only a sample file
- the producer uses raw sockets instead of a durable streaming platform
- the Spark job only parses and prints data
- there are no aggregations, quality checks, or storage sinks yet
- there is no dashboard or downstream analytics layer

## How I Would Improve This Project

If I continue this project, these are the improvements I would make next.

### 1. Use the full Yelp academic review dataset

The current repo only includes a sample file for testing. The next step is to stream the real `yelp_academic_dataset_review.json` file so the pipeline handles larger volume and more realistic behavior.

### 2. Replace socket streaming with Kafka

Sockets are fine for learning, but Kafka would make the project much stronger from a data engineering perspective.

Kafka would add:

- replayability
- durability
- better producer/consumer decoupling
- more realistic streaming architecture

### 3. Add real transformations

Right now the Spark job mainly parses the records. I would extend it to:

- filter invalid rows
- calculate rolling metrics
- group by date or business
- compute rating summaries
- possibly add sentiment classification later

### 4. Write results to storage

Instead of printing to the console only, I would write the output to:

- Parquet
- PostgreSQL
- Elasticsearch
- or a small warehouse-style layer

That would make the project more useful for downstream analytics.

### 5. Add data quality and monitoring

I would also add:

- validation checks
- logging
- failure handling
- basic monitoring metrics

That would move the project closer to real operational data engineering work.

## Why I Think This Is Still a Good Project

Even in its current form, I think this is a good project because it shows that I understand the core streaming pattern:

- ingest
- stream
- process
- structure
- scale with containers

It is simple enough to explain clearly, but still technical enough to show real engineering thinking.

## How To Run It

### Start the Spark services

```bash
docker compose -f src/docker-compose.yml up -d
```

### Start the producer inside the Spark master container

```bash
docker compose -f src/docker-compose.yml exec spark-master /bin/sh -lc "python3 /opt/spark/jobs/streaming-socket.py --file-path '/opt/spark/datasets/Yelp JSON/sample_reviews.json' --host 127.0.0.1 --port 9999 --chunk-size 1 --send-delay 0.2"
```

### Submit the Spark streaming job

```bash
docker compose -f src/docker-compose.yml exec spark-master /bin/sh -lc "/opt/spark/bin/spark-submit --master spark://spark-master:7077 /opt/spark/jobs/spark-streaming.py --host 127.0.0.1 --port 9999"
```

### Stop the services

```bash
docker compose -f src/docker-compose.yml down
```

## Configuration

The project is configurable through environment variables and CLI flags.

- `STREAM_INPUT_PATH`: path to the review dataset file
- `STREAM_BIND_HOST`: host/interface for the socket server to bind to
- `STREAM_SOCKET_HOST`: host the Spark job connects to
- `STREAM_SOCKET_PORT`: socket port used by both producer and consumer
- `STREAM_CHUNK_SIZE`: number of records grouped before sending
- `STREAM_SEND_DELAY_SECONDS`: delay between records
- `SPARK_MASTER`: optional Spark master URL
- `SPARK_MASTER_HOST`, `SPARK_MASTER_PORT`, `SPARK_MASTER_WEB_PORT`: Docker Compose overrides
- `SPARK_JAVA_HOME`: optional Java home override for local Spark execution

## Final Note

If I were presenting this project, I would describe it like this:

"I built a small streaming data pipeline that simulates real-time Yelp review ingestion using Python sockets and processes the stream with Spark Structured Streaming inside Docker. I chose a simulated file-based source because it is reproducible and easier to test than a live API, and I designed the project to show the core data engineering ideas clearly. The next step would be replacing the socket source with Kafka and writing processed results to a proper storage layer."
