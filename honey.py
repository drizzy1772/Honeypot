


#HONEYYYYYYYY





import socket
import threading
import datetime
import json
from pathlib import Path
from typing import Tuple

HOST = "127.0.0.1"
PORT = 2222
LOGFILE = Path("connections.jsonl")
BANNER = "SSH-2.0-OpenSSH_7.4p1 Ubuntu-10\r\n"
RECV_TIMEOUT = 5.0
MAX_RECV_BYTES = 4096


def now_iso() -> str:
    return datetime.datetime.utcnow().isoformat() + "Z"


def safe_decode(data: bytes) -> str:
    try:
        return data.decode("utf-8", errors="replace")
    except Exception:
        return repr(data)


def log_entry(entry: dict):
    s = json.dumps(entry, ensure_ascii=False)
    with LOGFILE.open("a", encoding="utf-8") as f:
        f.write(s + "\n")
    print(s)


def handle_client(conn: socket.socket, addr: tuple[str, int]):
    ip, port = addr
    ts = now_iso()
    log_entry({"ts": ts, "event": "connect", "ip": ip, "port": port})

    try:
        conn.settimeout(RECV_TIMEOUT)

        
        conn.sendall(BANNER.encode("utf-8"))

        
        data = conn.recv(MAX_RECV_BYTES)
        if data:
            log_entry({"ts": now_iso(), "event": "data", "ip": ip, "data": safe_decode(data)})
    except Exception as e:
        log_entry({"ts": now_iso(), "event": "error", "ip": ip, "error": str(e)})
    finally:
        conn.close()
        log_entry({"ts": now_iso(), "event": "disconnect", "ip": ip})


def start_server(host: str = HOST, port: int = PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(100)
    log_entry({"ts": now_iso(), "event": "start", "msg": f"Server started on {host}:{port}"})

    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.daemon = True
        t.start()


if __name__ == "__main__":
    LOGFILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOGFILE.exists():
        LOGFILE.write_text("", encoding="utf-8")
    start_server()