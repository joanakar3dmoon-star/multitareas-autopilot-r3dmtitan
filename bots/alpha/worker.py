from bots.alpha.intake import IntakeBot
from bots.alpha.planner import PlannerBot
from bots.alpha.qa import QualityBot

class AlphaBotWorker:
    """Creates an actionable work plan; external execution remains adapter-gated."""
    def __init__(self):
        self.intake = IntakeBot()
        self.planner = PlannerBot()
        self.qa = QualityBot()
    def run(self, task):
        intake = self.intake.run({**task.payload, "vertical": task.vertical})
        plan = self.planner.run(intake.data)
        supplied_artifact = task.payload.get("artifact")
        qa = self.qa.run(supplied_artifact) if supplied_artifact else None
        return {"task_id": task.task_id, "pulpo": "ALPHA", "state": "NEEDS_ADAPTER",
                "intake": intake.data, "plan": plan.data,
                "qa": qa.data if qa else {"status": "PENDING", "reason": "artifact_not_supplied"},
                "next": "connect_authorized_delivery_and_execution_adapter"}
