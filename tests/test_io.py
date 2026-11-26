import sys
sys.path.append('C:/Users/pbomy/Documents/Outils aéroacoustiques/Leaf/')

from src.io.load_params import load_params_class
from pathlib import Path
from src.parker.core.models import ReseauLames
from src.parker.solvers.koch.params import ParamsKoch
from src.parker.solvers.koch.solvers import SolverKoch2D

param_path = Path('C:/Users/pbomy/Documents/Outils aéroacoustiques/Leaf/tests/params.py')

# reseau = ReseauLames()
# params = ParamsKoch()

solver_name, reseau, params_solver = load_params_class(param_path)

print(solver_name)
print(reseau)
print(params_solver)

# solver = SolverKoch2D(reseau, params)
# result = solver.run()

# print(result.fields)