from bots.common import BotOutput, require_mapping

class LeadQualifierBot:
    name = "beta.lead_qualifier"
    def run(self, payload):
        data = require_mapping(payload)
        consent = data.get("contact_permission") is True
        fields = ("need", "budget", "timeline")
        present = [key for key in fields if isinstance(data.get(key), str) and data[key].strip()]
        score = round(100 * len(present) / len(fields))
        return BotOutput(self.name, "QUALIFIED" if score >= 67 and consent else "REVIEW",
                         {"score": score, "known_fields": present, "contact_permission": consent,
                          "contact_allowed": consent})
