"""
Contient les fonctions nécessaires pour la résolution du système d'équations
de Wiener-Hopf associé au problème de Koch.

Le coeur de la méthode est le suivant :

1. Un certain nombre de quantités auxiliaires (nombres d'ondes effectifs,
   fonctions caractéristiques K+ / K-, termes P et Q) sont calculées à partir
   des paramètres physiques (Mach, angle, fréquence...) : ce sont les
   fonctions ``_*_f``.
2. Ces quantités permettent d'assembler la matrice du système linéaire issu
   de la factorisation de Wiener-Hopf (fonctions ``_build_matrix*``).
3. La fréquence de Parker est obtenue en cherchant le nombre d'onde
   adimensionné K* qui annule le déterminant de cette matrice
   (fonction ``koch2D_solver``).
"""

from src.constants import c_0

import numpy as np
from scipy.signal import argrelmin
from scipy.optimize import minimize_scalar

# ---------------- Quantités adimensionnées et nombres d'ondes effectifs ----------------

def _delta_kr(i, j):
    """Symbole de Kronecker : vaut 1 si i == j, 0 sinon."""
    return 1 * (i == j)

def _f_star_f(f, d0):
    """Fréquence adimensionnée f* = f * d0 / c_0 (d0 : épaisseur des lames)."""
    return f * d0 / c_0

def _K_f(f_star, M):
    """Nombre d'onde acoustique K = 2*pi*f* / sqrt(1 - M²) (correction de Mach)."""
    return 2 * np.pi * f_star / np.sqrt(1 - M**2)

def _l_f(l0, d0, M):
    """Envergure adimensionnée l = l0 / (d0 * sqrt(1 - M²))."""
    return l0 / (d0 * np.sqrt(1 - M**2))

def _l_ratio_f(l_star, M):
    """Envergure adimensionnée donnée directement sous forme du rapport l* = L/s."""
    return l_star / np.sqrt(1 - M**2)

def _a_f(alpha0, M):
    """Composante 'a' du changement de variables a + i*b (direction de l'écoulement)."""
    return np.cos(alpha0) / np.sqrt(1 - M**2)

def _b_f(alpha0):
    """Composante 'b' du changement de variables a + i*b (direction transverse)."""
    return np.sin(alpha0)

def _d_f(alpha0, M):
    """Module d = sqrt(a² + b²) du changement de variables."""
    return np.sqrt(_a_f(alpha0, M)**2 + _b_f(alpha0)**2)

def _alpha_f(alpha0, M):
    """Angle modifié par l'écoulement : alpha = atan( sqrt(1 - M²) * tan(alpha0) )."""
    return np.arctan(np.sqrt(1 - M**2) * np.tan(alpha0))

def _sigma_f(sigma0, M, f_star, alpha0):
    """Décalage effectif sigma = sigma0 - M * K * a (effet Doppler de l'écoulement)."""
    return sigma0 - M * _K_f(f_star, M) * _a_f(alpha0, M)

def _mu_f(r, f_star, alpha0, M):
    """
    Modes transverses mu_r : racines réelles ou imaginaires pures selon que le
    mode est propagatif ou évanescent.
    """
    K = _K_f(f_star, M)
    b = _b_f(alpha0)
    if K > r * np.pi / b:
        # Mode propagatif : mu_r réel négatif
        return -np.sqrt(K**2 - (r * np.pi / b)**2)
    else:
        # Mode évanescent : mu_r imaginaire pur
        return 1j * np.sqrt(-K**2 + (r * np.pi / b)**2)

def _sigma_plus_f(r, f_star, alpha0, M, sigma0):
    """Racine 'plus' sigma+ associée au mode r (fonction caractéristique)."""
    K = _K_f(f_star, M)
    d = _d_f(alpha0, M)
    sigma = _sigma_f(sigma0, M, f_star, alpha0)
    alpha = _alpha_f(alpha0, M)
    K_frac = (2 * r * np.pi - sigma) / d
    if K**2 > K_frac**2:
        return K_frac * np.cos(alpha) - np.sin(alpha) * np.sqrt(K**2 - K_frac**2)
    else:
        return K_frac * np.cos(alpha) + 1j * np.sin(alpha) * np.sqrt(K_frac**2 - K**2)

def _sigma_minus_f(r, f_star, alpha0, M, sigma0):
    """Racine 'minus' sigma- associée au mode r (fonction caractéristique)."""
    K = _K_f(f_star, M)
    d = _d_f(alpha0, M)
    sigma = _sigma_f(sigma0, M, f_star, alpha0)
    alpha = _alpha_f(alpha0, M)
    K_frac = (2 * r * np.pi - sigma) / d
    if K**2 > K_frac**2:
        return K_frac * np.cos(alpha) + np.sin(alpha) * np.sqrt(K**2 - K_frac**2)
    else:
        return K_frac * np.cos(alpha) - 1j * np.sin(alpha) * np.sqrt(K_frac**2 - K**2)

def _chi_f(xi, alpha0, M):
    """Exposant de phase géométrique intervenant dans les fonctions caractéristiques."""
    alpha = _alpha_f(alpha0, M)
    if alpha == 0:
        return -1j * xi / np.pi * (- _a_f(alpha0, M) * (alpha - np.pi / 2))
    else:
        return -1j * xi / np.pi * (_b_f(alpha0) * np.log(2 * np.sin(alpha)) - _a_f(alpha0, M) * (alpha - np.pi / 2))

# ---------------- Facteurs de Wiener-Hopf K+ et K- ----------------

def _produit_kcal(xi, f_star, alpha0, M, sigma0, Niter, signe):
    """
    Produit infini (tronqué à Niter termes) commun aux fonctions K+ et K-.

    Le paramètre ``signe`` vaut +1 pour K+ (numérateur 1 + xi/mu, racines
    sigma+) et -1 pour K- (numérateur 1 - xi/mu, racines sigma-).
    """
    prod = 1
    sigma = _sigma_plus_f if signe > 0 else _sigma_minus_f

    for r in range(Niter):
        mu = _mu_f(r, f_star, alpha0, M)
        if mu == 0:
            num = np.nan
        else:
            num = 1 + signe * xi / mu
        den = (1 + xi / sigma(r, f_star, alpha0, M, sigma0)) * (1 + (1 - _delta_kr(r, 0)) * xi / sigma(-r, f_star, alpha0, M, sigma0))
        if den == 0:
            prod *= np.nan
        else:
            prod *= num / den

    return prod

def _Kcal_plus_f(xi, f_star, alpha0, M, sigma0, Niter):
    """
    Facteur de Wiener-Hopf K+(xi) : terme de bord Kcal0 (dépendant de sigma),
    exposant de phase géométrique, puis produit infini tronqué.
    """
    K = _K_f(f_star, M)
    b = _b_f(alpha0)
    chi = _chi_f(xi, alpha0, M)
    sigma = _sigma_f(sigma0, M, f_star, alpha0)
    Kcal0 = -K * np.sin(K * b) / (4 * np.sin((b * K - sigma) / 2) * np.sin((b * K + sigma) / 2))

    prod = _produit_kcal(xi, f_star, alpha0, M, sigma0, Niter, signe=+1)

    return Kcal0 * np.exp(chi) * prod

def _Kcal_minus_f(xi, f_star, alpha0, M, sigma0, Niter):
    """
    Facteur de Wiener-Hopf K-(xi) : exposant de phase géométrique (terme de
    bord unitaire) puis produit infini tronqué.
    """
    chi = _chi_f(xi, alpha0, M)

    prod = _produit_kcal(xi, f_star, alpha0, M, sigma0, Niter, signe=-1)

    return np.exp(-chi) * prod

# ---------------- Coefficients P et Q de la matrice ----------------

def _P_f(r, l, f_star, alpha0, M, sigma0, Niter):
    """
    Coefficient P_r (version générique).

    ``l`` est l'envergure adimensionnée déjà calculée (via _l_f ou _l_ratio_f
    selon que les dimensions sont absolues ou exprimées en rapports b/s, L/s).
    """
    mu_r = _mu_f(r, f_star, alpha0, M)
    a = _a_f(alpha0, M)
    b = _b_f(alpha0)
    sigma = _sigma_f(sigma0, M, f_star, alpha0)
    Kcal = _Kcal_minus_f(-mu_r, f_star, alpha0, M, sigma0, Niter)

    return -2 * np.exp(1j * l * mu_r) * Kcal**2 * (1 - (-1)**r * np.cos(a * mu_r + sigma)) / (b * mu_r * (1 + _delta_kr(r, 0)))

def _Q_f(r, l, f_star, alpha0, M, sigma0, Niter):
    """Coefficient Q_r (version générique, cf. _P_f pour la convention de ``l``)."""
    mu_r = _mu_f(r, f_star, alpha0, M)
    a = _a_f(alpha0, M)
    b = _b_f(alpha0)
    sigma = _sigma_f(sigma0, M, f_star, alpha0)
    Kcal = _Kcal_plus_f(mu_r, f_star, alpha0, M, sigma0, Niter)

    return 2 * np.exp(1j * l * mu_r) * Kcal**2 * (1 - (-1)**r * np.cos(a * mu_r - sigma)) / (b * mu_r * (1 + _delta_kr(r, 0)))

def _P_f_d0(r, f_star, alpha0, l0, d0, M, sigma0, Niter):
    """Coefficient P_r pour des dimensions absolues (l calculée depuis l0, d0)."""
    l = _l_f(l0, d0, M)
    return _P_f(r, l, f_star, alpha0, M, sigma0, Niter)

def _Q_f_d0(r, f_star, alpha0, l0, d0, M, sigma0, Niter):
    """Coefficient Q_r pour des dimensions absolues (l calculée depuis l0, d0)."""
    l = _l_f(l0, d0, M)
    return _Q_f(r, l, f_star, alpha0, M, sigma0, Niter)

def _P_f_ratio(r, f_star, alpha0, l_star, M, sigma0, Niter):
    """Coefficient P_r pour des dimensions en rapports (l calculée depuis l* = L/s)."""
    l = _l_ratio_f(l_star, M)
    return _P_f(r, l, f_star, alpha0, M, sigma0, Niter)

def _Q_f_ratio(r, f_star, alpha0, l_star, M, sigma0, Niter):
    """Coefficient Q_r pour des dimensions en rapports (l calculée depuis l* = L/s)."""
    l = _l_ratio_f(l_star, M)
    return _Q_f(r, l, f_star, alpha0, M, sigma0, Niter)

# ---------------- Coefficients L_ij et N_ij du système ----------------

def _L_ij_f(i, j, l, f_star, alpha0, M, sigma0, Niter):
    """Coefficient L_ij : couplage du mode j vers l'équation i (via P_j)."""
    return _P_f(j, l, f_star, alpha0, M, sigma0, Niter) / (_mu_f(i, f_star, alpha0, M) + _mu_f(j, f_star, alpha0, M))

def _N_ij_f(i, j, l, f_star, alpha0, M, sigma0, Niter):
    """Coefficient N_ij : couplage du mode j vers l'équation i (via Q_j et l'effet Doppler)."""
    mu_i = _mu_f(i, f_star, alpha0, M)
    mu_j = _mu_f(j, f_star, alpha0, M)
    K = _K_f(f_star, M)
    return _Q_f(j, l, f_star, alpha0, M, sigma0, Niter) * (M * mu_j + K) / ((mu_i + mu_j) * (K - M * mu_i))

###################################
# building a matrix of the form : #
#                                 #
#     | I_N+1 |  -L   |           #
#     |_______|_______|           #
#     |       |       |           #
#     |  N    | I_N+1 |           #
#                                 #
###################################


def _construire_matrice(N_size, l, f_star, alpha0, M, sigma0, Niter, partie_reelle):
    """
    Assemble la matrice 2x2 blocs du système de Wiener-Hopf (identité / couplages -L et N).

    ``partie_reelle`` : si True, seules les parties réelles des couplages L_ij et
    N_ij sont insérées (cas de la résolution 2D où le problème final est réel).
    """
    mat = np.zeros((2 * N_size + 2, 2 * N_size + 2))
    for i in range(2 * N_size + 2):
        mat[i, i] = 1
    for i in range(N_size + 1):
        for j in range(N_size + 1):
            L_ij = _L_ij_f(i, j, l, f_star, alpha0, M, sigma0, Niter)
            N_ij = _N_ij_f(i, j, l, f_star, alpha0, M, sigma0, Niter)
            if partie_reelle:
                mat[i, N_size + 1 + j] = -np.real(L_ij)
                mat[N_size + 1 + i, j] =  np.real(N_ij)
            else:
                mat[i, N_size + 1 + j] = -L_ij
                mat[N_size + 1 + i, j] =  N_ij
    return mat

def _build_matrix(N_size, d0, l0, f, alpha0, M, sigma0, Niter):
    """
    Matrice du système pour des dimensions absolues : la fréquence ``f`` (en Hz)
    est convertie en f*, et l'envergure adimensionnée est issue de (l0, d0).
    """
    f_star = _f_star_f(f, d0)
    l = _l_f(l0, d0, M)
    return _construire_matrice(N_size, l, f_star, alpha0, M, sigma0, Niter, partie_reelle=False)

def _build_matrix_ratio(N_size, l_star, f_star, alpha0, M, sigma0, Niter):
    """Matrice du système pour des dimensions en rapports (l* = L/s et f* donnés)."""
    l = _l_ratio_f(l_star, M)
    return _construire_matrice(N_size, l, f_star, alpha0, M, sigma0, Niter, partie_reelle=True)

# ---------------- Résolution par optimisation du déterminant ----------------

def koch2D_solver(N_x, N_y, b, s, chi, M, N_matrix, Niter, N_sumsize, bidim = True, N_z = 0):
    """
    Résout la fréquence de Parker en 2D par la méthode de Koch.

    Paramètres
    ----------
    N_x : nombre de noeuds dans la direction x (sens de l'écoulement)
    N_y : nombre de noeuds dans la direction transverse y
    b, s, chi : largeur des lames (m), espacement (m), angle de décalage (rad)
    M : nombre de Mach
    N_matrix : taille de la troncature du système de Wiener-Hopf
    Niter : nombre de points du maillage en K* pour la détection des minima
    N_sumsize : nombre de termes des produits infinis tronqués
    bidim : True si le solver est utilisé pour un mode 2D afin d'adapter le message d'erreur
    N_z : nombre de noeuds de pression dans la direction de l'envergure z (utilisé uniquement si bidim=False et qu'aucun mode n'est calculable)

    Retour
    ------
    Fréquence de Parker (en Hz).
    """
    b_star = b / s
    alpha0 = np.pi / 2 - chi
    sigma0 = -(N_y + 1) * np.pi

    def det_equations(Kstar):
        """
        Calcul du déterminant de la matrice correspondant aux équations données
        par la méthode de Wiener-Hopf en fonction du nombre d'onde adimensionné
        K* dans le but de déterminer la valeur de K* pour laquelle ce
        déterminant s'annule.

        Fonction pour la pulsation omega_2D
        """
        return np.linalg.det(_build_matrix_ratio(N_matrix, b_star, Kstar, alpha0, M, sigma0, N_sumsize))

    # Bornes de recherche imposées par le mode transverse N_y
    min_bounds = [N_y / 2 + 1e-5, (N_y + 1) / 2 - 1e-5]

    # Balayage grossier : localisation des minima du déterminant
    X = np.linspace(min_bounds[0], min_bounds[1], Niter)
    Y = np.array([det_equations(k) for k in X])

    indices_mins = X[argrelmin(Y)]

    if len(indices_mins) <= N_x:
        if bidim:
            raise ValueError(f"Le présent réseau de lames n'admet pas de mode ({N_x}, {N_y})")
        else:
            raise ValueError(f"Le présent réseau de lames n'admet pas de mode ({N_x}, {N_y}, {N_z})")

    # Affinage : resserrer les bornes autour du N_x-ième minimum local (à 5 % près)
    if indices_mins[N_x] * 0.95 < min_bounds[0]:
        bound_low = min_bounds[0]
    else:
        bound_low = indices_mins[N_x] * 0.95

    if indices_mins[N_x] * 1.05 > min_bounds[1]:
        bound_high = min_bounds[1]
    else:
        bound_high = indices_mins[N_x] * 1.05

    new_bounds = [bound_low, bound_high]

    # Recherche fine du zéro du déterminant par minimisation bornée
    root = minimize_scalar(det_equations, bounds=new_bounds, method='bounded')

    return root.x * c_0 / s  # type: ignore

def koch3D_solver(N_x, N_y, N_z, b, L, s, chi, M, N_matrix, Niter, N_sumsize):
    """
    Résout la fréquence de Parker en 3D par la méthode de Koch.

    Paramètres
    ----------
    N_x : nombre de noeuds de pression dans la direction x (sens de l'écoulement)
    N_y : nombre de noeuds de pression dans la direction transverse y
    N_z : nombre de noeuds de pression dans la direction de l'envergure z
    b, L, s, chi : largeur des lames (m), envergure des lames (m), espacement (m), angle de décalage (rad)
    M : nombre de Mach
    N_matrix : taille de la troncature du système de Wiener-Hopf
    Niter : nombre de points du maillage en K* pour la détection des minima
    N_sumsize : nombre de termes des produits infinis tronqués

    Retour
    ------
    Fréquence de Parker (en Hz).
    """
    f_xy = koch2D_solver(N_x, N_y, b, s, chi, M, N_matrix, Niter, N_sumsize, bidim=False, N_z=N_z)    # Fréquence dans le plan XY
    f_yz = koch2D_solver(N_z, N_y, L, s, 0, 0, N_matrix, Niter, N_sumsize, bidim=False, N_z=N_z)      # Fréquence dans le plan YZ (dans ce plan, chi=0 et M=0)

    f_y  = np.pi * N_y / s      # Fréquence dans la direction y

    return (f_xy**2 + f_yz**2 - f_y**2)**0.5 