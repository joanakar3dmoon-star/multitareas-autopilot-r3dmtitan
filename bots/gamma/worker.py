from bots.gamma.data_quality import MarketDataQualityBot
from bots.gamma.risk_gate import PortfolioRiskGateBot
from bots.gamma.research import ResearchBot

class GammaBotWorker:
    """Research and risk diagnostics only; never emits broker orders."""
    def __init__(self):
        self.data_quality = MarketDataQualityBot()
        self.risk = PortfolioRiskGateBot()
        self.research = ResearchBot()
    def run(self, task):
        research = self.research.run(task.payload)
        quality = self.data_quality.run(task.payload)
        risk = self.risk.run(task.payload.get("risk", {"exposure_pct": 0, "limit_pct": 1}))
        return {"task_id": task.task_id, "pulpo": "GAMMA", "state": "RESEARCH_ONLY",
                "research": research.data, "data_quality": quality.data, "risk": risk.data,
                "investment_order_allowed": False}
