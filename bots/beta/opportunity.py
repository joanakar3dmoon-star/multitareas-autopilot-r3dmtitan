from bots.common import BotOutput, require_mapping

class OpportunityBot:
    name = "beta.opportunity"
    def run(self, payload):
        data = require_mapping(payload)
        candidates = data.get("candidates", [])
        if not isinstance(candidates, list):
            raise ValueError("candidates must be a list")
        ranked = []
        for item in candidates[:100]:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "")).strip()[:240]
            commission = item.get("commission_rate", 0)
            try: rate = float(commission)
            except (TypeError, ValueError): rate = 0.0
            if title and 0 <= rate <= 100:
                ranked.append({"title": title, "commission_rate": rate, "source": str(item.get("source", ""))[:160]})
        ranked.sort(key=lambda x: x["commission_rate"], reverse=True)
        return BotOutput(self.name, "REVIEW", {"candidates": ranked, "count": len(ranked)})
