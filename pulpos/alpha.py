"""ALPHA: multitareas, automatización y servicios digitales."""
VERTICALS = ("dealwork", "websites", "web_apps", "automation", "content", "design", "data", "qa", "support")
FAMILIES = ("scout", "intake", "planner", "browser_automation", "builder", "designer", "writer", "data_worker", "qa", "delivery", "support")

class AlphaWorker:
    def run(self, task):
        if task.vertical not in VERTICALS:
            raise ValueError("Vertical not enabled for ALPHA")
        return {"task_id": task.task_id, "state": "HUMAN_REVIEW", "pulpo": "ALPHA", "next": "register_platform_adapter_and_evidence"}
