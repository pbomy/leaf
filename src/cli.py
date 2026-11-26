"""
Point d'entrée ligne de commande de Leaf.

Lance un calcul complet à partir d'un fichier ``params.py`` :

    python -m src.cli --params examples/params_koch2d.py --output resultats.json

(ou ``leaf --params ...`` après installation via ``pip install -e .``)
"""

import argparse
import logging
import sys
from pathlib import Path

from src.app import lancer_calcul


def construire_parser() -> argparse.ArgumentParser:
    """Construit l'analyseur d'arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        prog="leaf",
        description="Lance un calcul de fréquences de Parker à partir d'un fichier de paramètres.",
    )
    parser.add_argument(
        "--params", "-p",
        required=True,
        type=Path,
        help="chemin du fichier params.py contenant la configuration du calcul",
    )
    parser.add_argument(
        "--output", "-o",
        default="resultats.json",
        type=Path,
        help="chemin du fichier résultat à écrire (JSON, défaut : resultats.json)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="affiche les messages d'exécution détaillés",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """
    Point d'entrée principal : analyse les arguments, lance le calcul et
    retourne un code de sortie (0 : succès, 1 : échec).
    """
    args = construire_parser().parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s : %(name)s : %(message)s",
    )

    try:
        chemin_resultat = lancer_calcul(args.params, args.output)
    except Exception as exc:  # erreur de params, de solver ou de calcul
        print(f"Erreur : {exc}", file=sys.stderr)
        return 1

    print(f"Calcul terminé, résultats écrits dans : {chemin_resultat}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
