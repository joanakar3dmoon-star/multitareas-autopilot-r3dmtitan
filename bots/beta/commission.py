"""Read-only commission reconciliation using integer minor currency units."""
import re
from bots.common import BotOutput, require_mapping

class CommissionAuditBot:
    name = "beta.commission_audit"

    def run(self, payload):
        data = require_mapping(payload)
        expected = data.get("expected_minor")
        received = data.get("received_minor")
        currency = data.get("currency")
        if (not isinstance(expected, int) or isinstance(expected, bool) or
                not isinstance(received, int) or isinstance(received, bool) or
                min(expected, received) < 0):
            raise ValueError("expected_minor and received_minor must be non-negative integers")
        code = str(currency or "").upper()
        if not re.fullmatch(r"[A-Z]{3}", code):
            raise ValueError("currency must be a three-letter ISO-style code")
        return BotOutput(self.name, "MATCH" if expected == received else "DISCREPANCY",
                         {"expected_minor": expected, "received_minor": received,
                          "difference_minor": received - expected, "currency": code})
