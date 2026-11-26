"""
Paramètres numériques du solver aux éléments finis

Ces paramètres complètent les dimensions du réseau (``ReseauLames``) : ils ne
dépendent que de la méthode numérique, pas de la géométrie.
"""

from dataclasses import dataclass

@dataclass
class ParamsFEM:
    """
    Paramètres numériques pour la résolution des fréquences de Parker
    avec la méthode aux éléments finis
    """
    taille_maille_min: float = 0    # Taille minimale des mailles au centre du domaine (m). Si vaut zéro, la taille sera calculée automatiquement
    taille_maille_max: float = 0    # Taille maximale des mailles à l'extérieur du domaine (m). Si vaut zéro, la taille sera calculée automatiquement
    rayon: float = 0                # Rayon du domaine circulaire (m). Si vaut zéro, le rayon sera calculé automatiquement            

    def __post_init__(self) -> None:
        if self.taille_maille_min < 0 or self.taille_maille_max < 0:
            raise ValueError("Les tailles de mailles ne peuvent être négatives")
        if self.rayon < 0:
            raise ValueError("Le rayon du domaine ne peut être négatif")