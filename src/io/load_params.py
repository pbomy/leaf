"""
Chargement d'un fichier ``params.py`` utilisateur.

Un fichier de paramètres est un simple script Python définissant :
- ``solver_name`` : le nom du solver à utiliser (ex : ``"Koch 2D"``) ;
- des variables (flottants, entiers) correspondant aux champs de
  ``ReseauLames`` (géométrie du réseau) et de la classe de paramètres
  numériques du solver choisi.
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
from dataclasses import fields
from pathlib import Path

import src.parker.solvers  # noqa: F401  (déclenche l'enregistrement des solvers)
from src.parker.core.base import BaseSolver
from src.parker.core.models import ReseauLames


class ParamsError(Exception):
    """Erreur de chargement ou de validation d'un fichier de parametres."""


def _charger_module(params_file: Path):
    """
    Charge un fichier Python comme module et retourne ce module.

    Lève ``ParamsError`` si le fichier est introuvable ou illisible.
    """
    if not params_file.is_file():
        raise ParamsError(f"Fichier de parametres introuvable : {params_file}")

    spec = importlib.util.spec_from_file_location(params_file.stem, params_file)
    if spec is None or spec.loader is None:
        raise ParamsError(f"Impossible de charger {params_file} comme module Python")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


def _variables_utilisateur(module) -> dict:
    """
    Extrait les variables « de configuration » d'un module.

    Sont conservées les variables publiques qui ne sont ni des fonctions,
    ni des classes, ni des modules : ce sont les paramètres fournis par
    l'utilisateur dans son fichier ``params.py``.
    """
    return {
        name: value
        for name, value in vars(module).items()
        if not name.startswith("_")
        and not inspect.isfunction(value)
        and not inspect.isclass(value)
        and not inspect.ismodule(value)
    }


def solver_par_nom(solver_name: str) -> type:
    """
    Retourne la classe du solver dont ``SOLVER_NAME`` vaut ``solver_name``.

    Lève ``ValueError`` si aucun solver ne correspond, en listant les
    noms disponibles.
    """
    for classe in BaseSolver.__subclasses__():
        if classe.SOLVER_NAME == solver_name:
            return classe

    noms_disponibles = ", ".join(c.SOLVER_NAME for c in BaseSolver.__subclasses__())
    raise ValueError(
        f"Le solver {solver_name} ne correspond à aucun solver disponible, "
        f"les solvers disponibles sont : {noms_disponibles}"
    )


def _construire_dataclass(cls, variables: dict):
    """
    Instancie la dataclass ``cls`` en ne reprenant de ``variables`` que les
    champs déclarés par la classe (les autres variables sont ignorées).
    """
    noms_champs = {f.name for f in fields(cls)}
    instance = cls()
    for name, value in variables.items():
        if name in noms_champs:
            setattr(instance, name, value)
    return instance


def load_params_class(params_file: str | Path) -> tuple[str, ReseauLames, object]:
    """
    Charge un fichier ``params.py`` et retourne le triplet
    ``(solver_name, reseau, parametres_numeriques)``.

    - ``reseau``               : instance de ``ReseauLames`` remplie avec les
                                 dimensions géométriques du fichier ;
    - ``parametres_numeriques``: instance de la classe de paramètres du solver
                                 sélectionné, remplie avec les valeurs du fichier.
    """
    params_file = Path(params_file).resolve()

    module = _charger_module(params_file)
    user_vars = _variables_utilisateur(module)

    # Nom du solver demandé
    try:
        solver_name = user_vars["solver_name"]
    except KeyError:
        raise ParamsError("Aucun nom de solver n'a été renseigné sous le nom ``solver_name``")

    # Classe du solver correspondant
    solver_class = solver_par_nom(solver_name)

    # Remplissage de la géométrie et des paramètres numériques
    reseau: ReseauLames = _construire_dataclass(ReseauLames, user_vars)
    parametres = _construire_dataclass(solver_class.param_num, user_vars)  # type: ignore

    return solver_name, reseau, parametres
