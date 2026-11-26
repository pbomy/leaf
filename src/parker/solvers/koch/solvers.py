"""
Contient les solveurs pour les méthodes de Koch 2D et Koch étendu à l'envergure
"""

from src.parker.core.base import BaseSolver
from src.parker.core.base import ReseauLames, Resultats
from src.parker.solvers.koch.params import ParamsKoch
from src.parker.solvers.koch.utils import koch2D_solver

import time

class SolverKoch2D(BaseSolver):
    """
    Solver utilisant la méthode de Koch en 2D
    """
    SOLVER_NAME = "Koch 2D"
    reseau      = ReseauLames
    param_num   = ParamsKoch

    def run(self) -> Resultats:
        t0 = time.perf_counter()
        f = koch2D_solver(self.param_num.N_x, self.param_num.N_y, self.reseau.b, self.reseau.s, self.reseau.chi, self.param_num.M, self.param_num.N_matrice, self.param_num.N_discret_x, self.param_num.N_sumsize)

        resultats = Resultats(solver_name=self.SOLVER_NAME)
        resultats.add_field("Fréquence beta", f)
        resultats.metadata['Temps de résolution'] = f"{time.perf_counter() - t0:6f} s"

        return resultats
        