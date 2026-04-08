import argparse
import json
import socket
import sys
import time
from datetime import datetime
from pathlib import Path

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


def resolve_input_path(file_path):
    normalized_path = Path(file_path.strip()).expanduser()
    if not normalized_path.is_absolute():
        normalized_path = (Path.cwd() / normalized_path).resolve()
    else:
        normalized_path = normalized_path.resolve()

    if not normalized_path.is_file():
        raise FileNotFoundError(
            f"Dataset file not found: {normalized_path}. "
            "Provide a valid file with --file-path or STREAM_INPUT_PATH."
        )

    return normalized_path


def send_data_over_socket(file_path, host, port, chunk_size, send_delay):
    input_path = resolve_input_path(file_path)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)
    print(f"Streaming records from {input_path}")
    print(f"Listening for connections on {host}:{port}")

    last_sent_index = 0
    try:
        while True:
            conn, addr = s.accept()
            print(f"Connection from {addr}")
            try:
                with input_path.open("r", encoding="utf-8") as file:
                    for _ in range(last_sent_index):
                        next(file)

                    records = []
                    for line in file:
                        records.append(json.loads(line))
                        if len(records) == chunk_size:
                            print(f"Sending {len(records)} record(s)")
                            for record in records:
                                serialized_data = json.dumps(record, default=handle_date).encode(
                                    "utf-8"
                                )
                                conn.sendall(serialized_data + b"\n")
                                time.sleep(send_delay)
                                last_sent_index += 1

                            records = []

                    if records:
                        print(f"Sending final {len(records)} record(s)")
                        for record in records:
                            serialized_data = json.dumps(record, default=handle_date).encode(
                                "utf-8"
                            )
                            conn.sendall(serialized_data + b"\n")
                            time.sleep(send_delay)
                            last_sent_index += 1
            except (BrokenPipeError, ConnectionResetError):
                print("Client disconnected.")
            finally:
                conn.close()
                print("Connection closed")
    except KeyboardInterrupt:
        print("Socket server stopped.")
    finally:
        s.close()


if __name__ == "__main__":
    args = parse_args()
    send_data_over_socket(
        file_path=args.file_path,
        host=args.host,
        port=args.port,
        chunk_size=args.chunk_size,
        send_delay=args.send_delay,
    )
