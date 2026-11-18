"""Structural market-data validation; does not claim freshness."""
import math
from datetime import datetime
from bots.common import BotOutput, require_mapping

class MarketDataQualityBot:
    name = "gamma.data_quality"

    def run(self, payload):
        data = require_mapping(payload)
        price = data.get("price")
        timestamp = data.get("observed_at")
        price_valid = (isinstance(price, (int, float)) and not isinstance(price, bool)
                       and math.isfinite(price) and price > 0)
        timestamp_valid = False
        if isinstance(timestamp, str) and timestamp.strip():
            try:
                datetime.fromisoformat(timestamp.strip().replace("Z", "+00:00"))
                timestamp_valid = True
            except ValueError:
                timestamp_valid = False
        structural = price_valid and timestamp_valid
        return BotOutput(self.name, "STRUCTURALLY_VALID" if structural else "INVALID",
                         {"price_valid": price_valid, "timestamp_parseable": timestamp_valid,
                          "freshness_checked": False, "tradable_signal": False})
