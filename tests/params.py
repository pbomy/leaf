"""
Exemple de fichier de paramètres utilisé par les tests (même format que
``examples/params_koch2d.py``).
"""

# ------------ Choix du solver ------------

solver_name = "Koch 2D"

# ------------ Géométrie du réseau de lames (ReseauLames) ------------

d = 2e-3            # Epaisseur des lames en m
b = 6e-2            # Largeur (corde) des lames en m
L = 50e-2           # Envergure (longueur) des lames en m
N = 5               # Nombre de lames
s = 6e-2            # Espacement entre les lames en m
chi = 0.0           # Angle de décalage des lames en radians

# ------------ Paramètres numériques (ParamsKoch) ------------

N_matrice = 2       # Taille de la troncature du système de Wiener-Hopf
N_discret_x = 60    # Nombre de valeurs du déterminant calculées pour l'optimisation
N_sumsize = 30      # Nombre de termes des produits infinis tronqués

N_x = 0             # Index du minimum local du déterminant retenu
N_y = 0             # Mode transverse utilisé pour borner la recherche
N_z = 0             # Réservé pour le solver Koch étendu à l'envergure

M = 0.3             # Nombre de Mach de l'écoulement
