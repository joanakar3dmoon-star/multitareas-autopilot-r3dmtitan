"""Exposure check against explicit user-supplied limits; never authorizes orders."""
import math
from bots.common import BotOutput, require_mapping

class PortfolioRiskGateBot:
    name = "gamma.risk_gate"

    def run(self, payload):
        data = require_mapping(payload, "risk")
        exposure = data.get("exposure_pct")
        limit = data.get("limit_pct")
        valid_exposure = (isinstance(exposure, (int, float)) and not isinstance(exposure, bool)
                          and math.isfinite(exposure) and exposure >= 0)
        valid_limit = (isinstance(limit, (int, float)) and not isinstance(limit, bool)
                       and math.isfinite(limit) and limit > 0)
        if not valid_exposure or not valid_limit:
            raise ValueError("explicit finite exposure_pct >= 0 and limit_pct > 0 are required")
        passed = exposure <= limit
        return BotOutput(self.name, "WITHIN_LIMIT" if passed else "BREACH",
                         {"exposure_pct": exposure, "limit_pct": limit, "passed": passed,
                          "order_authorized": False})
