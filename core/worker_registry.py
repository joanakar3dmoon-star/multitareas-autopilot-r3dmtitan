"""Default registry wiring the three Pulpos to phase-three bot families."""
from core.orchestrator import Orchestrator
from bots.alpha.worker import AlphaBotWorker
from bots.beta.worker import BetaBotWorker
from bots.gamma.worker import GammaBotWorker

def build_orchestrator() -> Orchestrator:
    return Orchestrator({"ALPHA": AlphaBotWorker(), "BETA": BetaBotWorker(), "GAMMA": GammaBotWorker()})
