"""Default registry wiring three Pulpos, task catalog and safe local handlers."""
from core.orchestrator import Orchestrator
from core.catalog import TaskCatalog
from core.task_handlers import build_task_handlers
from bots.alpha.worker import AlphaBotWorker
from bots.beta.worker import BetaBotWorker
from bots.gamma.worker import GammaBotWorker

def build_orchestrator() -> Orchestrator:
    workers = {"ALPHA": AlphaBotWorker(), "BETA": BetaBotWorker(), "GAMMA": GammaBotWorker()}
    return Orchestrator(workers, catalog=TaskCatalog(),
                        task_handlers=build_task_handlers())
