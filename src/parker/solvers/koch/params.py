from dataclasses import dataclass

@dataclass
class ParamsKoch:
    """
    Paramètres numériques pour la résolution des fréquences de Parker avec la méthode de Koch
    """
    N_matrice: int   = 2         # Taille de la matrice N_matrice x N_matrice pour le système de Wiener-Hopf
    N_discret_x: int = 200       # Nombre de valeur du déterminant calculé pour l'optimisation
    N_sumsize: int   = 50        # Nombre de termes calculés dans les valeurs impliquant une somme ou un produit infini

    N_x: int    = 0     # Nombre de noeuds dans la direction x
    N_y: int    = 0     # Nombre de noeuds dans la direction y
    N_z: int    = 0     # Nombre de noeuds dans la direction z

    M: float    = 0     # Nombre de Mach

    def __post_init__(self) -> None:
        if self.M < 0:
            raise ValueError("The Mach number cannot be negative")