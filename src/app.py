"""
Orchestration d'un calcul : chargement des paramètres, exécution du solver,
sauvegarde du fichier résultat.

Ce module est le point de passage entre la ligne de commande (``cli.py``)
et les briques ``io`` / ``solvers``.
"""

import logging
from pathlib import Path

from src.io.load_params import load_params_class, solver_par_nom
from src.io.save_results import enregistrer_resultats
from src.parker.core.models import Resultats

logger = logging.getLogger(__name__)


def lancer_calcul(fichier_params: str | Path, fichier_sortie: str | Path) -> Path:
    """
    Lance un calcul complet à partir d'un fichier ``params.py``.

    Étapes :
    1. chargement et validation des paramètres ;
    2. instanciation du solver correspondant à ``solver_name`` ;
    3. exécution du calcul ;
    4. sauvegarde des résultats dans ``fichier_sortie`` (format JSON).

    Retourne le chemin du fichier résultat écrit.
    """
    # 1. Chargement des paramètres (géométrie + paramètres numériques)
    solver_name, reseau, parametres = load_params_class(fichier_params)
    reseau.valider()

    # 2. Instanciation du solver demandé
    solver_class = solver_par_nom(solver_name)
    solver = solver_class(reseau, parametres)

    logger.info("Solver '%s' : lancement du calcul", solver_name)

    # 3. Exécution du calcul
    resultats: Resultats = solver.run()

    # 4. Sauvegarde du fichier résultat
    chemin_sortie = enregistrer_resultats(resultats, reseau, parametres, fichier_sortie)

    logger.info("Résultats écrits dans %s", chemin_sortie)

    return chemin_sortie
