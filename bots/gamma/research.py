from bots.common import BotOutput, require_mapping

ALLOWED_ASSET_CLASSES = {"equity", "etf", "bond", "fund", "gold", "commodity"}

class ResearchBot:
    name = "gamma.research"
    def run(self, payload):
        data = require_mapping(payload)
        asset_class = str(data.get("asset_class", "")).lower()
        if asset_class in {"crypto", "cryptocurrency", "token"}:
            raise ValueError("Crypto assets are excluded from GAMMA")
        if asset_class not in ALLOWED_ASSET_CLASSES:
            raise ValueError("Unsupported traditional asset class")
        return BotOutput(self.name, "RESEARCH_ONLY",
                         {"asset_class": asset_class, "symbol": str(data.get("symbol", ""))[:32],
                          "investment_order_allowed": False})
