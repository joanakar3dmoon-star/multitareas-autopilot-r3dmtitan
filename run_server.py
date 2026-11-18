"""Start authenticated API and worker loop in one persistent process."""
import os
import threading
from api_server import build_server, run_worker_loop

def main():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    server = build_server(host=host, port=port)
    stop_event = threading.Event()
    worker = threading.Thread(target=run_worker_loop,
                              args=(server.runtime, stop_event),
                              name="multitareas-worker", daemon=True)
    server.worker_thread = worker
    worker.start()
    try:
        server.serve_forever(poll_interval=0.5)
    finally:
        stop_event.set()
        worker.join(timeout=10)
        server.server_close()

if __name__ == "__main__":
    main()
