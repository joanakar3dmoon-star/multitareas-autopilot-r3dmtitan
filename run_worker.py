"""Start the local queue worker. External bridges remain disabled until configured."""
import argparse
from core.app import build_runtime
from core.scheduler import Scheduler
from connectors.bridge.dispatcher import BridgeDispatcher

def main() -> None:
    parser = argparse.ArgumentParser(description="R3DM Multitareas Autopilot worker")
    parser.add_argument("--once", action="store_true", help="process at most one task and exit")
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--batch-size", type=int, default=10)
    args = parser.parse_args()
    runtime = build_runtime()
    bridge = BridgeDispatcher(runtime.store)
    if args.once:
        print(runtime.run_once())
        print({"bridge": bridge.dispatch_pending()})
        return

    def on_cycle(results):
        for item in results:
            print(item)
        bridge_result = bridge.dispatch_pending()
        if bridge_result.get("sent"):
            print({"bridge": bridge_result})

    Scheduler(runtime, interval_seconds=args.interval, batch_size=args.batch_size,
              on_cycle=on_cycle).run_forever()

if __name__ == "__main__":
    main()
