import logging
from abc import ABC, abstractmethod
from src.parker.core.models import ReseauLames, Resultats

logger = logging.getLogger(__name__)

class BaseSolver(ABC):
    """
    Contrat commun pour tous les solvers
    """
    SOLVER_NAME = "base"

    def __init__(self, reseau:ReseauLames, params, logger=None) -> None:
        self.reseau = reseau
        self.params = params
        self.logger = logger or logging.getLogger(__name__)

    @abstractmethod
    def run(self) -> Resultats:
        raise NotImplementedError