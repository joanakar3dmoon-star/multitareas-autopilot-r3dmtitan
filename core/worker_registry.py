"""Default registry wiring the three Pulpos and the declarative task catalog."""
from core.orchestrator import Orchestrator
from core.catalog import TaskCatalog
from bots.alpha.worker import AlphaBotWorker
from bots.beta.worker import BetaBotWorker
from bots.gamma.worker import GammaBotWorker

def build_orchestrator() -> Orchestrator:
    workers = {"ALPHA": AlphaBotWorker(), "BETA": BetaBotWorker(), "GAMMA": GammaBotWorker()}
    return Orchestrator(workers, catalog=TaskCatalog())
