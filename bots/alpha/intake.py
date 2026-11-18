from bots.common import BotOutput, require_mapping, non_empty_text

class IntakeBot:
    name = "alpha.intake"
    def run(self, payload):
        data = require_mapping(payload)
        brief = non_empty_text(data.get("brief") or data.get("description"), "brief")
        vertical = non_empty_text(data.get("vertical") or "general", "vertical", 80).lower()
        return BotOutput(self.name, "ACCEPTED", {"brief": brief, "vertical": vertical})
