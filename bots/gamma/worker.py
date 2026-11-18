"""GAMMA research and risk diagnostics; never emits broker orders."""
from bots.gamma.data_quality import MarketDataQualityBot
from bots.gamma.risk_gate import PortfolioRiskGateBot
from bots.gamma.research import ResearchBot

class GammaBotWorker:
    def __init__(self):
        self.data_quality = MarketDataQualityBot()
        self.risk = PortfolioRiskGateBot()
        self.research = ResearchBot()

    def run(self, task):
        research = self.research.run(task.payload)
        quality = self.data_quality.run(task.payload)
        risk_input = task.payload.get("risk")
        risk = (self.risk.run(risk_input).data if risk_input is not None else
                {"status": "NOT_EVALUATED", "reason": "risk_data_not_supplied",
                 "order_authorized": False})
        return {"task_id": task.task_id, "pulpo": "GAMMA", "state": "RESEARCH_ONLY",
                "research": research.data, "data_quality": quality.data, "risk": risk,
                "investment_order_allowed": False}
