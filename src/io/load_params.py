from __future__ import annotations

import importlib.util
import inspect
import sys
from dataclasses import fields, is_dataclass
from pathlib import Path
from src.parker.core.models import ReseauLames
from src.parker.core.base import BaseSolver


class ParamsError(Exception):
    """Erreur de chargement ou de validation d'un fichier de parametres."""


def load_params_class(params_file: str | Path) -> tuple[str, ReseauLames, object]:
    """Charge un fichier ``params.py`` et construit une instance de ``params_cls``
    """
    params_file = Path(params_file).resolve()
    if not params_file.is_file():
        raise ParamsError(f"Fichier de parametres introuvable : {params_file}")

    spec = importlib.util.spec_from_file_location(params_file.stem, params_file)
    if spec is None or spec.loader is None:
        raise ParamsError(f"Impossible de charger {params_file} comme module Python")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    user_vars = {
        name: value
        for name, value in vars(module).items()
        if not name.startswith("_")
        and not inspect.isfunction(value)
        and not inspect.isclass(value)
        and not inspect.ismodule(value)
    }

    try:
        solver_name = user_vars['solver_name']
    except:
        raise ParamsError("Aucun nom de solver n'a été renseigné sous le nom ``solver_name``")

    # ------------ Détection du solver -------------

    flag_solver = False
    l_SOLVER_NAMES = []
    for iSolver in BaseSolver.__subclasses__():
        l_SOLVER_NAMES.append(iSolver.SOLVER_NAME)
        if iSolver.SOLVER_NAME == solver_name:
            SolverClass = iSolver
            flag_solver = True

    if not flag_solver:
        raise ValueError(f'Le solver {solver_name} ne correspond à aucun solver disponible, les solvers disponibles sont : ' + ','.join(l_SOLVER_NAMES))

    # ------------ Implémentation des variables du réseau -------------

    reseau = ReseauLames()

    for name, value in user_vars.items():
        if name in {f.name for f in fields(ReseauLames)}:
            reseau.__setattr__(name, value)
    
    # ------------ Implémentation des variables numériques du solver -------------

    ParamsSolver = SolverClass.param_num # type: ignore

    params_solver = ParamsSolver()

    for name, value in user_vars.items():
        if name in {f.name for f in fields(ParamsSolver)}:
            params_solver.__setattr__(name, value)

    return solver_name, reseau, params_solver