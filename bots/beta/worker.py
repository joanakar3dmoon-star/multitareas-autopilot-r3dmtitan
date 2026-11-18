from bots.beta.opportunity import OpportunityBot
from bots.beta.lead_qualifier import LeadQualifierBot
from bots.beta.commission import CommissionAuditBot

class BetaBotWorker:
    """Qualifies supplied marketplace data; does not scrape, message or transact."""
    def __init__(self):
        self.opportunities = OpportunityBot()
        self.leads = LeadQualifierBot()
        self.commissions = CommissionAuditBot()
    def run(self, task):
        payload = task.payload
        result = {"task_id": task.task_id, "pulpo": "BETA", "state": "NEEDS_ADAPTER",
                  "opportunities": self.opportunities.run(payload).data}
        if "need" in payload or "contact_permission" in payload:
            result["lead"] = self.leads.run(payload).data
        if "expected_minor" in payload or "received_minor" in payload:
            result["commission"] = self.commissions.run(payload).data
        result["next"] = "connect_approved_marketplace_and_attribution_adapter"
        return result
