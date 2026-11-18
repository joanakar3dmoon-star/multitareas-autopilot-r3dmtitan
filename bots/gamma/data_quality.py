from bots.common import BotOutput, require_mapping

class MarketDataQualityBot:
    name = "gamma.data_quality"
    def run(self, payload):
        data = require_mapping(payload)
        price = data.get("price")
        timestamp = data.get("observed_at")
        valid = isinstance(price, (int, float)) and price > 0 and isinstance(timestamp, str) and bool(timestamp.strip())
        return BotOutput(self.name, "VALID" if valid else "STALE_OR_INVALID",
                         {"price_valid": isinstance(price, (int, float)) and price > 0,
                          "timestamp_present": bool(timestamp), "tradable_signal": False})
