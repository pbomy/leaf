# Leaf

Logiciel de calcul numerique (fréquences de Parker d'un réseau de lames)
structuré autour de solvers autonomes.

Chaque solver est un dossier dans `src/parker/solvers/` avec ses paramètres
(`params.py`) et son implémentation (`solvers.py`).

## Installation

```bash
pip install -e ".[dev]"
```

## Utilisation

Lancer un calcul à partir d'un fichier de paramètres et récupérer un fichier
résultat au format JSON :

```bash
# Avec le paquet installé
leaf --params examples/params_koch2d.py --output resultats.json

# Ou directement depuis la racine du dépôt
python -m src.cli --params examples/params_koch2d.py --output resultats.json
```

Options de la ligne de commande :

| Option            | Rôle                                                      |
|-------------------|-----------------------------------------------------------|
| `--params`, `-p`  | chemin du fichier `params.py` (obligatoire)               |
| `--output`, `-o`  | chemin du fichier résultat JSON (défaut `resultats.json`) |
| `--verbose`, `-v` | affiche les messages d'exécution détaillés                |

Le fichier résultat JSON contient les valeurs calculées, le temps de
résolution, ainsi que toutes les dimensions du réseau et les paramètres
numériques utilisés (résultat autoporteur et reproductible).

Lancer les tests :

```bash
pytest
```

## Fichier de paramètres

Un fichier `params.py` est un simple script Python définissant des variables :

```python
solver_name = "Koch 2D" | "Koch 3D"  # solver à utiliser

# Géométrie du réseau de lames (ReseauLames)
d = 2e-3       # Epaisseur des lames en m
b = 6e-2       # Largeur des lames en m
L = 50e-2      # Envergure des lames en m
N = 5          # Nombre de lames
s = 6e-2       # Espacement entre les lames en m
chi = 0.0      # Angle de décalage des lames en radians

# Paramètres numériques du solver (ParamsKoch)
N_matrice = 2    # Troncature du système de Wiener-Hopf
N_discret_x = 200  # Points du balayage grossier en K*
N_sumsize = 50   # Troncature des produits infinis
N_x = 0          # Index du minimum local retenu
N_y = 0          # Mode transverse bornant la recherche
M = 0.3          # Nombre de Mach
```

Un exemple complet est fourni dans `examples/params_koch.py`.

## Arborescence

```
src/
├── constants.py          # constantes physiques (vitesse du son...)
├── parker/
│   ├── core/             # socle commun : BaseSolver, modeles de donnees (ne depend de personne)
│   └── solvers/          # un dossier par solver (params.py + solvers.py)
├── io/                   # chargement des params, sauvegarde des resultats
├── utils/                # Contient des fonctions utiles pour tous les modules du logiciel
├── cli.py                # point d'entree ligne de commande (mince : parse et delegue)
└── app.py                # orchestration : charge params -> lance solver -> sauvegarde
```

## Ajouter un nouveau solver

1. Créer un dossier `src/parker/solvers/<nom>/`
2. Y définir une dataclass de paramètres dans `params.py` (avec un
   `__post_init__` de validation si nécessaire)
3. Implémenter un `Solver(BaseSolver)` dans `solvers.py`, avec son
   `SOLVER_NAME` et son attribut `param_num`
4. L'importer dans `src/parker/solvers/__init__.py` pour l'enregistrer

Règle d'architecture : les dépendances ne vont que dans un sens
(`core`/`utils` <- `solvers` <- `io`/`app`/`cli`).
