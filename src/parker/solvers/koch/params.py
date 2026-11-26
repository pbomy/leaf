"""
Paramètres numériques du solver Koch 2D.

Ces paramètres complètent les dimensions du réseau (``ReseauLames``) : ils ne
dépendent que de la méthode numérique, pas de la géométrie.
"""

from dataclasses import dataclass


@dataclass
class ParamsKoch:
    """
    Paramètres numériques pour la résolution des fréquences de Parker
    avec la méthode de Koch
    """
    N_matrice: int = 2       # Taille de la matrice N_matrice x N_matrice pour le système de Wiener-Hopf
    N_discret_x: int = 200   # Nombre de valeurs du déterminant calculées pour l'optimisation
    N_sumsize: int = 50      # Nombre de termes calculés dans les valeurs impliquant une somme ou un produit infini

    N_x: int = 0             # Index du minimum local du déterminant retenu
    N_y: int = 0             # Mode transverse utilisé pour borner la recherche (ex-nombre de noeuds en y)
    N_z: int = 0             # Nombre de noeuds dans la direction z (réservé pour Koch étendu)

    M: float = 0             # Nombre de Mach de l'écoulement

    def __post_init__(self) -> None:
        if self.M < 0:
            raise ValueError("Le nombre de Mach ne peut pas être négatif")
