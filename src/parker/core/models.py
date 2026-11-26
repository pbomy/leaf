from dataclasses import dataclass, field

@dataclass
class ReseauLames:
    """
    Classe décrivant les dimensions d'un réseau de lames
    """
    d: float = 0   # Epaisseur des lames en m
    b: float = 0   # Largeur des lames en m
    L: float = 0   # Envergure (longueur) des lames en m
    N: int   = 0     # Nombre de lames
    s: float = 0    # Espacement entre les lames en m
    chi:float= 0   # Angle de décalage des lames en radians

    def __post__init__(self):
        if self.b<=0 or self.d<=0 or self.L<=0 or self.s<=0:
            raise ValueError("Les dimensions du réseau ne peuvent être nulles ou négatives")        

    def b_star(self):
        """
        Retourne le rapport b/s
        """
        return self.b/self.s

    def L_star(self):
        """
        Retourne le rapport L/s
        """
        return self.L/self.s

@dataclass
class Resultats:
    """
    Contient les résultats produits par un solver
    """

    solver_name: str
    fields: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, str] = field(default_factory=dict)

    def add_field(self, key:str, value:float) -> None:
        self.fields[key] = value