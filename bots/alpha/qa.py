from bots.common import BotOutput, require_mapping

class QualityBot:
    name = "alpha.qa"
    def run(self, artifact):
        data = require_mapping(artifact, "artifact")
        checks = {"has_content": bool(data.get("content") or data.get("artifact_ref")),
                  "has_scope": bool(data.get("scope") or data.get("brief"))}
        passed = all(checks.values())
        return BotOutput(self.name, "PASS" if passed else "NEEDS_WORK", {"checks": checks, "passed": passed})
