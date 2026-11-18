"""GAMMA: análisis y autoinversión tradicional; cripto excluido."""
VERTICALS = ("equities", "etfs", "bonds", "funds", "cash_management", "commodities_research", "macro_research")
FAMILIES = ("market_data", "fundamental_research", "quant_research", "macro", "portfolio", "allocation", "risk", "compliance", "alerts", "reconciliation", "learning")
MODE = "RESEARCH_ONLY"
EXCLUDED_ASSETS = ("cryptocurrency", "crypto_tokens")

class GammaWorker:
    def run(self, task):
        if task.vertical not in VERTICALS:
            raise ValueError("Vertical not enabled for GAMMA")
        return {"task_id": task.task_id, "state": "RESEARCH_ONLY", "pulpo": "GAMMA", "next": "broker_and_risk_controls_required"}
