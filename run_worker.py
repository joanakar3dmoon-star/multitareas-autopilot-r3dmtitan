"""Start the local queue worker. No external integrations are activated here."""
import argparse
from core.app import build_runtime
from core.scheduler import Scheduler

def main() -> None:
    parser = argparse.ArgumentParser(description="R3DM Multitareas Autopilot worker")
    parser.add_argument("--once", action="store_true", help="process at most one task and exit")
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--batch-size", type=int, default=10)
    args = parser.parse_args()
    runtime = build_runtime()
    if args.once:
        print(runtime.run_once())
        return
    Scheduler(runtime, interval_seconds=args.interval, batch_size=args.batch_size,
              on_cycle=lambda results: [print(item) for item in results]).run_forever()

if __name__ == "__main__":
    main()
