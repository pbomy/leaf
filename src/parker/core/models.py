"""
Modèles de données partagés par tous les solvers :
dimensions du réseau de lames contenu (ReseauLames) et résultats produits (Resultats).

Règle d'architecture : ce module ne dépend d'aucun autre module du projet.
"""

from dataclasses import dataclass, field
from math import isfinite


@dataclass
class ReseauLames:
    """
    Classe décrivant les dimensions d'un réseau de lames.

    Toutes les longueurs sont en mètres, l'angle de décalage est en radians.
    """
    d: float = 0     # Epaisseur des lames en m
    b: float = 0     # Largeur (corde) des lames en m
    L: float = 0     # Envergure (longueur) des lames en m
    N: int = 0       # Nombre de lames
    s: float = 0     # Espacement entre les lames en m
    chi: float = 0   # Angle de décalage des lames en radians

    def valider(self) -> None:
        """
        Vérifie la cohérence géométrique du réseau.

        À appeler une fois les dimensions remplies (par exemple depuis un
        fichier de paramètres), avant de lancer le calcul.
        """
        if self.b <= 0 or self.d <= 0 or self.L <= 0 or self.s <= 0:
            raise ValueError("Les dimensions du réseau ne peuvent être nulles ou négatives")

    def b_star(self) -> float:
        """Retourne le rapport b/s (largeur relative des lames)."""
        return self.b / self.s

    def L_star(self) -> float:
        """Retourne le rapport L/s (envergure relative des lames)."""
        return self.L / self.s


@dataclass
class Resultats:
    """
    Contient les résultats produits par un solver.

    - ``fields``    : valeurs numériques calculées (fréquences, amplitudes...)
    - ``metadata``  : informations de contexte (temps de résolution, version...)
    """

    solver_name: str
    fields: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, str] = field(default_factory=dict)

    def add_field(self, key: str, value: float) -> None:
        """Ajoute (ou remplace) une valeur numérique au dictionnaire des résultats."""
        self.fields[key] = float(value)
