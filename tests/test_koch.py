import sys
sys.path.append('C:/Users/pbomy/Documents/Outils aéroacoustiques/Leaf/')

from src.parker.core.models import ReseauLames
from src.parker.solvers.koch.params import ParamsKoch
from src.parker.solvers.koch.solvers import SolverKoch2D

reseau = ReseauLames(2e-3, 6e-2, 50e-2, 5, 6e-2, 0)
params = ParamsKoch()

solver = SolverKoch2D(reseau, params)

sol = solver.run()

print(sol.fields, sol.metadata)