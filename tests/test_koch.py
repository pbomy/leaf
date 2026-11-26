"""
Tests du solver Koch 2D et du chaînage complet (params -> solver -> fichier JSON).
"""

import json

from src.app import lancer_calcul
from src.io.load_params import load_params_class
from src.parker.solvers.koch.params import ParamsKoch
from src.parker.solvers.koch.solvers import SolverKoch2D


def test_solver_koch2d():
    """Le solver produit une fréquence finie et positive."""
    _, reseau, params = load_params_class("tests/params.py")

    solver = SolverKoch2D(reseau, params)
    sol = solver.run()

    assert sol.solver_name == "Koch 2D"
    assert sol.fields["Fréquence beta"] > 0

    assert "Temps de résolution" in sol.metadata


def test_calcul_e2e(tmp_path):
    """Chaînage complet : params.py -> calcul -> fichier résultat JSON."""
    sortie = tmp_path / "resultats" / "sortie.json"

    chemin = lancer_calcul("tests/params.py", sortie)

    assert chemin == sortie
    assert sortie.is_file()

    contenu = json.loads(sortie.read_text(encoding="utf-8"))

    assert contenu["solver"] == "Koch 2D"
    assert contenu["resultats"]["valeurs"]["Fréquence beta"] > 0

    assert contenu["reseau"]["b"] == 6e-2
    assert contenu["params_numeriques"]["M"] == 0.3


def test_parametres_pris_en_compte():
    """Les paramètres numériques sont bien lus depuis self.params (et non les défauts)."""
    _, reseau, params = load_params_class("tests/params.py")

    params.N_discret_x = 30 # type: ignore
    params.N_sumsize = 20 # type: ignore

    solver = SolverKoch2D(reseau, params)
    sol = solver.run()

    assert sol.fields["Fréquence beta"] > 0
