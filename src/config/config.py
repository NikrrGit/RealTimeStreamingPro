import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_REVIEW_DATASET = BASE_DIR / "datasets" / "Yelp JSON" / "yelp_academic_dataset_review.json"


config = {
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY"),
    },
    "streaming": {
        "socket_host": os.getenv("STREAM_SOCKET_HOST", "localhost"),
        "socket_port": int(os.getenv("STREAM_SOCKET_PORT", "9999")),
    },
    "socket_server": {
        "bind_host": os.getenv("STREAM_BIND_HOST", "0.0.0.0"),
        "port": int(os.getenv("STREAM_SOCKET_PORT", "9999")),
        "chunk_size": int(os.getenv("STREAM_CHUNK_SIZE", "2")),
        "send_delay_seconds": float(os.getenv("STREAM_SEND_DELAY_SECONDS", "5")),
    },
    "spark": {
        "master": os.getenv("SPARK_MASTER"),
    },
    "datasets": {
        "reviews_path": Path(os.getenv("STREAM_INPUT_PATH", DEFAULT_REVIEW_DATASET)),
    },
}
