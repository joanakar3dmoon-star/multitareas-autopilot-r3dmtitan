"""BETA: marketplaces, afiliación, leads, citas y comisiones."""
VERTICALS = ("marketplace_services", "affiliate", "lead_generation", "appointments", "resale_opportunities", "partner_sales")
FAMILIES = ("deal_scout", "offer_hunter", "price_comparator", "fraud_check", "lead_qualifier", "crm", "scheduler", "sales_assistant", "attribution", "commission_reconciler", "after_sales")

class BetaWorker:
    def run(self, task):
        if task.vertical not in VERTICALS:
            raise ValueError("Vertical not enabled for BETA")
        return {"task_id": task.task_id, "state": "HUMAN_REVIEW", "pulpo": "BETA", "next": "verify_platform_terms_and_commission"}
