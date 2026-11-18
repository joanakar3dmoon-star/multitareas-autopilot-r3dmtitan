"""Opt-in scheduler entry point. No background process starts on import."""
from __future__ import annotations

import signal
import time
from typing import Callable

from core.runtime import WorkerRuntime


class Scheduler:
    def __init__(self, runtime: WorkerRuntime, interval_seconds: float = 2.0,
                 batch_size: int = 10, on_cycle: Callable[[list[dict]], None] | None = None) -> None:
        if interval_seconds < 0.1:
            raise ValueError("interval_seconds must be >= 0.1")
        self.runtime = runtime
        self.interval_seconds = interval_seconds
        self.batch_size = batch_size
        self.on_cycle = on_cycle
        self._stopping = False

    def stop(self, *_args) -> None:
        self._stopping = True

    def run_forever(self) -> None:
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)
        while not self._stopping:
            results = self.runtime.run_batch(self.batch_size)
            if self.on_cycle:
                self.on_cycle(results)
            if not results:
                time.sleep(self.interval_seconds)
