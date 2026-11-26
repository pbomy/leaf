
"""
Construction des fichiers .geo pour le maillage et réalisation
du maillage MEF avec GMSH.
"""

import shutil
import subprocess
from pathlib import Path

from src.parker.core.models import ReseauLames
from src.parker.solvers.fem.params import ParamsFEM


# ---------------------------------------------------------------------
# Gestion des chemins
# ---------------------------------------------------------------------


def _get_cur_path() -> Path:
    """
    Retourne le chemin du présent répertoire sous forme de Path.
    """
    return Path(__file__).parent.resolve()


# ---------------------------------------------------------------------
# Traitement des paramètres FEM
# ---------------------------------------------------------------------

def _traitement_params_FEM(params: ParamsFEM, reseau: ReseauLames) -> None:
    """
    Calcule automatiquement les paramètres laissés nuls et les
    actualise dans l'instance ParamsFEM à partir des dimensions
    d'une instance de ReseauLames.

    Paramètres
    ----------
    params : Instance de ParamsFEM.
    reseau : Instance de ReseauLames.
    """

    if params.rayon == 0:
        L_y = reseau.d * reseau.N + reseau.s * (reseau.N - 1)
        L_z = reseau.L

        params.rayon = 1.5 * max(L_y, L_z) / 2

    if params.taille_maille_min == 0:
        params.taille_maille_min = reseau.d

    if params.taille_maille_max == 0:
        params.taille_maille_max = params.taille_maille_min * 15


# ---------------------------------------------------------------------
# Génération des fichiers .geo
# ---------------------------------------------------------------------

def _make_geo(
    reseau: ReseauLames,
    params: ParamsFEM,
    plane: str
) -> None:
    """
    Génère un fichier .geo temporaire à partir du fichier modèle
    correspondant au plan XY ou YZ.

    Paramètres
    ----------
    reseau : Instance de ReseauLames.
    params : Instance de ParamsFEM.
    plane : Plan considéré ('xy' ou 'yz').
    """

    base_path = _get_cur_path()
    gmsh_path = base_path / "GMSH_files"
    temp_path = base_path / "temp"

    # Traitement des paramètres FEM
    _traitement_params_FEM(params, reseau)

    # Construction des paramètres Gmsh
    st = "".join(
        f"{name} = {value};\n"
        for name, value in reseau.__dict__.items()
    )

    st += "\n"

    st += "".join(
        f"{name} = {value};\n"
        for name, value in params.__dict__.items()
    )

    st += "\n"

    # Lecture du fichier .geo modèle
    geo_file = gmsh_path / f"gmsh_FEM_{plane}.geo"

    with open(geo_file, "r") as f:
        flines = f.readlines()

    # Insertion des paramètres à la troisième ligne
    flines.insert(2, st)

    # Écriture du fichier temporaire
    geo_temp_file = temp_path / f"gmsh_FEM_{plane}_temp.geo"

    with open(geo_temp_file, "w") as f:
        f.writelines(flines)


def make_xy_geo(reseau: ReseauLames, params: ParamsFEM) -> None:
    """
    Crée le fichier .geo temporaire pour le maillage dans le plan XY.
    """
    _make_geo(reseau, params, "xy")


def make_yz_geo(reseau: ReseauLames, params: ParamsFEM) -> None:
    """
    Crée le fichier .geo temporaire pour le maillage dans le plan YZ.
    """
    _make_geo(reseau, params, "yz")


# ---------------------------------------------------------------------
# Création des maillages avec Gmsh
# ---------------------------------------------------------------------

def _create_mesh(plane: str) -> None:
    """
    Lance Gmsh pour créer le maillage du plan XY ou YZ.

    Paramètres
    ----------
    plane : Plan considéré ('xy' ou 'yz').
    """

    temp_path = _get_cur_path() / "temp"

    # Fichier .geo temporaire
    path_geo = temp_path / f"gmsh_FEM_{plane}_temp.geo"

    if not path_geo.is_file():
        raise KeyError(
            f"Le fichier .geo {plane.upper()} n'a pas été créé"
        )

    # Recherche de l'exécutable Gmsh
    path_exec_gmsh = shutil.which("gmsh")

    if path_exec_gmsh is None:
        raise FileNotFoundError(
            "Gmsh est introuvable. Vérifiez qu'il est bien installé"
        )

    # Exécution de Gmsh
    path_mesh = temp_path / f"mesh_{plane}_temp.msh"

    subprocess.run([
        path_exec_gmsh,
        str(path_geo),
        "-2",
        "-o",
        str(path_mesh),
        "-nopopup"
    ])


def create_mesh_xy() -> None:
    """
    Crée le maillage dans le plan XY avec Gmsh.
    """
    _create_mesh("xy")


def create_mesh_yz() -> None:
    """
    Crée le maillage dans le plan YZ avec Gmsh.
    """
    _create_mesh("yz")
