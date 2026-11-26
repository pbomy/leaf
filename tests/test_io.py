"""
Tests du chargement des paramètres (``src/io/load_params.py``).
"""

import pytest
from pathlib import Path

from src.io.load_params import ParamsError, load_params_class, solver_par_nom
from src.parker.core.models import ReseauLames
from src.parker.solvers.koch.params import ParamsKoch
from src.parker.solvers.koch.solvers import SolverKoch2D

FICHIER_PARAMS = Path(__file__).parent / "params.py"


def test_charge_params_complet():
    """Le fichier de paramètres remplit correctement les trois objets."""
    solver_name, reseau, params = load_params_class(FICHIER_PARAMS)

    assert solver_name == "Koch 2D"
    assert isinstance(reseau, ReseauLames)
    assert isinstance(params, ParamsKoch)

    assert reseau.b == 6e-2
    assert reseau.d == 2e-3
    assert reseau.s == 6e-2
    assert reseau.chi == 0.0

    assert params.M == 0.3
    assert params.N_discret_x == 60


def test_solver_inconnu():
    """Un nom de solver inexistant est rejeté avec la liste des noms valides."""
    with pytest.raises(ValueError, match="Koch 2D"):
        solver_par_nom("solver fantome")


def test_fichier_introuvable():
    """Un chemin invalide lève une ParamsError."""
    with pytest.raises(ParamsError):
        load_params_class(Path("n/existe/pas/params.py"))


def test_solver_retrouve_par_nom():
    """La classe SolverKoch2D est bien enregistrée et retrouvable par son nom."""
    assert solver_par_nom("Koch 2D") is SolverKoch2D
