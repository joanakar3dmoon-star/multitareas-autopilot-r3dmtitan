from bots.common import BotOutput, require_mapping

class PortfolioRiskGateBot:
    name = "gamma.risk_gate"
    def run(self, payload):
        data = require_mapping(payload)
        exposure = data.get("exposure_pct", 0)
        limit = data.get("limit_pct", 0)
        if not isinstance(exposure, (int, float)) or not isinstance(limit, (int, float)) or exposure < 0 or limit <= 0:
            raise ValueError("exposure_pct must be >= 0 and limit_pct must be > 0")
        passed = exposure <= limit
        return BotOutput(self.name, "WITHIN_LIMIT" if passed else "BREACH",
                         {"exposure_pct": exposure, "limit_pct": limit, "passed": passed,
                          "order_authorized": False})
