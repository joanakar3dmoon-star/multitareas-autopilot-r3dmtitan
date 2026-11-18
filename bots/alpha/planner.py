from bots.common import BotOutput, non_empty_text

class PlannerBot:
    name = "alpha.planner"
    def run(self, intake):
        brief = non_empty_text(intake.get("brief"), "brief")
        vertical = intake.get("vertical", "general")
        common = ["confirm_scope", "prepare_work_plan", "produce_first_version", "quality_check", "prepare_delivery"]
        if vertical in ("websites", "web_apps"):
            common.insert(2, "implement_and_test_web_assets")
        elif vertical in ("content", "design"):
            common.insert(2, "create_content_or_design_assets")
        elif vertical == "automation":
            common.insert(2, "implement_and_test_workflow")
        return BotOutput(self.name, "PLANNED", {"brief": brief, "vertical": vertical, "steps": common})
