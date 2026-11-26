"""
Socle commun à tous les solvers : définition du contrat ``BaseSolver``.

Règle d'architecture : ce module ne dépend que de ``core.models``.
"""

import logging
from abc import ABC, abstractmethod

from src.parker.core.models import ReseauLames, Resultats

logger = logging.getLogger(__name__)


class BaseSolver(ABC):
    """
    Contrat commun pour tous les solvers.

    Tout solver doit :
    - définir ``SOLVER_NAME`` (nom déclaré dans le fichier ``params.py``) ;
    - définir ``param_num`` (classe des paramètres numériques attendus) ;
    - implémenter ``run()`` qui retourne un objet ``Resultats``.
    """

    # Nom du solver tel qu'il doit être renseigné dans ``solver_name``
    SOLVER_NAME = "base"

    # Sert uniquement de documentation : les sous-classes redéclarent ces
    # attributs avec leurs propres types de paramètres.
    reseau: type = ReseauLames
    param_num: type = object

    def __init__(self, reseau: ReseauLames, params, logger: logging.Logger | None = None) -> None:
        """
        Paramètres
        ----------
        reseau : dimensions du réseau de lames
        params : paramètres numériques propres au solver
        logger : logger optionnel (un logger par défaut est créé sinon)
        """
        self.reseau = reseau
        self.params = params
        self.logger = logger or logging.getLogger(__name__)

    @abstractmethod
    def run(self) -> Resultats:
        """Lance le calcul et retourne les résultats."""
        raise NotImplementedError
