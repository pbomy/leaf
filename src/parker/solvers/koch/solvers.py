"""
Solveurs pour les méthodes de Koch 2D et Koch étendu à l'envergure.

Chaque classe hérite de ``BaseSolver`` : son ``SOLVER_NAME`` permet de la
retrouver depuis un fichier ``params.py``, et ``param_num`` déclare la classe
des paramètres numériques qu'elle attend.
"""

import time

from src.parker.core.base import BaseSolver
from src.parker.core.models import ReseauLames, Resultats
from src.parker.solvers.koch.params import ParamsKoch
from src.parker.solvers.koch.utils import koch2D_solver, koch3D_solver
from src.parker.core.strouhal_lame import _determ_St, _f_to_U
from src.utils.units import _ms_to_kmh, _deg_to_rad


class SolverKoch2D(BaseSolver):
    """
    Solver utilisant la méthode de Koch en 2D
    """
    SOLVER_NAME = "Koch 2D"
    reseau: type = ReseauLames
    param_num: type = ParamsKoch

    def run(self) -> Resultats:
        """
        Lance la résolution de la fréquence de Parker en 2D et retourne
        le résultat sous forme d'objet ``Resultats``.
        """
        t0 = time.perf_counter()

        # Raccourcis de lecture : dimensions du réseau et paramètres numériques
        r = self.reseau
        p = self.params

        f = koch2D_solver(
            p.N_x, p.N_y,
            r.b, r.s, _deg_to_rad(r.chi),
            p.M,
            p.N_matrice, p.N_discret_x, p.N_sumsize,
        )

        St_lame = _determ_St(r.b, r.d)   # Nombre de Strouhal de la lame
        U_infty = _f_to_U(St_lame, r.d, f)

        resultats = Resultats(solver_name=self.SOLVER_NAME) # type: ignore
        resultats.add_field(f"Fréquence ({p.N_x}, {p.N_y})", f)
        resultats.add_field("Nombre de Strouhal", St_lame)
        resultats.add_field("Vitesse d'écoulement (km/h)", _ms_to_kmh(U_infty))
        resultats.metadata["Temps de résolution"] = f"{time.perf_counter() - t0:.6f} s"

        return resultats

class SolverKoch3D(BaseSolver):
    """
    Solver utilisant la méthode de Koch en 3D
    """
    SOLVER_NAME = "Koch 3D"
    reseau: type = ReseauLames
    param_num: type = ParamsKoch

    def run(self) -> Resultats:
        """
        Lance la résolution de la fréquence de Parker en 3D et retourne
        le résultat sous forme d'objet ``Resultats``.
        """
        t0 = time.perf_counter()

        # Raccourcis de lecture : dimensions du réseau et paramètres numériques
        r = self.reseau
        p = self.params

        f = koch3D_solver(
            p.N_x, p.N_y, p.N_z,
            r.b, r.L, r.s, _deg_to_rad(r.chi),
            p.M,
            p.N_matrice, p.N_discret_x, p.N_sumsize,
        )

        resultats = Resultats(solver_name=self.SOLVER_NAME)
        resultats.add_field(f"Fréquence ({p.N_x}, {p.N_y})", f)
        resultats.metadata["Temps de résolution"] = f"{time.perf_counter() - t0:.6f} s"

        return resultats
