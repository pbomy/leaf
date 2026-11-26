"""
Sauvegarde des résultats d'un solver dans un fichier JSON.

Le fichier produit rassemble tout le contexte du calcul :
- le nom du solver et la date du calcul ;
- les valeurs calculées (champs) et les métadonnées (temps de résolution...) ;
- les dimensions du réseau et les paramètres numériques utilisés,
  afin que le résultat soit autoporteur et reproductible.
"""

import json
from dataclasses import asdict, fields
from datetime import datetime
from pathlib import Path

from src.parker.core.models import ReseauLames, Resultats


def enregistrer_resultats(
    resultats: Resultats,
    reseau: ReseauLames,
    params,
    chemin_sortie: str | Path,
) -> Path:
    """
   Sauvegarde un objet ``Resultats`` (avec le contexte du calcul) au format JSON.

    Le dossier parent est créé si nécessaire. Retourne le chemin du fichier écrit.
    """
    chemin_sortie = Path(chemin_sortie)

    contenu = {
        "solver": resultats.solver_name,
        "date": datetime.now().isoformat(timespec="seconds"),
        "resultats": {
            "valeurs": {cle: float(valeur) for cle, valeur in resultats.fields.items()},
            "metadonnees": dict(resultats.metadata),
        },
        "reseau": asdict(reseau),
        "params_numeriques": {f.name: getattr(params, f.name) for f in fields(params)},
    }

    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)
    chemin_sortie.write_text(
        json.dumps(contenu, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return chemin_sortie
