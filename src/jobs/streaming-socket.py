import argparse
import json
import socket
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

# Add the src directory to the Python path.
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from config.config import config


def handle_date(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Stream newline-delimited review JSON records over a TCP socket."
    )
    parser.add_argument(
        "--file-path",
        default=str(config["datasets"]["reviews_path"]),
        help="Path to the newline-delimited JSON file to stream.",
    )
    parser.add_argument(
        "--host",
        default=config["socket_server"]["bind_host"],
        help="Interface to bind the socket server to.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=config["socket_server"]["port"],
        help="Port to bind the socket server to.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=config["socket_server"]["chunk_size"],
        help="Number of records to group before sending.",
    )
    parser.add_argument(
        "--send-delay",
        type=float,
        default=config["socket_server"]["send_delay_seconds"],
        help="Delay in seconds between emitted records.",
    )
    return parser.parse_args()


def send_data_over_socket(file_path, host, port, chunk_size, send_delay):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    print(f"Listening for connections on {host}:{port}")

    last_sent_index = 0
    while True:
        conn, addr = s.accept()
        print(f"Connection from {addr}")
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for _ in range(last_sent_index):
                    next(file)

                records = []
                for line in file:
                    records.append(json.loads(line))
                    if len(records) == chunk_size:
                        chunk = pd.DataFrame(records)
                        print(chunk)
                        for record in chunk.to_dict(orient="records"):
                            serialized_data = json.dumps(record, default=handle_date).encode("utf-8")
                            conn.send(serialized_data + b"\n")
                            time.sleep(send_delay)
                            last_sent_index += 1

                        records = []
        except (BrokenPipeError, ConnectionResetError):
            print("Client disconnected.")
        finally:
            conn.close()
            print("Connection closed")


if __name__ == "__main__":
    args = parse_args()
    send_data_over_socket(
        file_path=args.file_path,
        host=args.host,
        port=args.port,
        chunk_size=args.chunk_size,
        send_delay=args.send_delay,
    )
