# mon_logiciel

Logiciel de calcul numerique structure autour de solvers autonomes.
Chaque solver est un dossier dans `src/mon_logiciel/solvers/` avec ses
propres parametres (`params.py`) et son implementation (`solver.py`).

## Installation

```bash
cd mon_logiciel
python -m venv .venv
source .venv/bin/activate      # Linux/macOS ; .venv\Scripts\activate sous Windows
pip install -e ".[dev]"
```

## Utilisation

```bash
mon_logiciel run meca --params examples/params_meca.py --output resultats/
pytest
```

## Arborescence

```
src/mon_logiciel/
├── core/      # socle commun : BaseSolver, modeles de donnees (ne depend de personne)
├── solvers/   # un dossier par solver (params.py + solver.py)
├── io/        # chargement des params, sauvegarde des resultats
├── cli.py     # point d'entree ligne de commande (mince : parse et delegue)
└── app.py     # orchestration : charge params -> lance solver -> sauvegarde
```

## Ajouter un nouveau solver

1. Creer un dossier `src/mon_logiciel/solvers/<nom>/`
2. Y definir une dataclass de parametres dans `params.py`
3. Implementer un `Solver(BaseSolver)` dans `solver.py`
4. L'enregistrer dans `solvers/__init__.py`

Regle d'architecture : les dependances ne vont que dans un sens
(`core` <- `solvers` <- `io`/`app`/`cli`).
