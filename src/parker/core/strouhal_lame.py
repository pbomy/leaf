"""
Fonctions pour l'estimation du nombre de Strouhal des lames et de la loi pour traduire les vitesses en fréquence

Ne dépend d'aucun autre module du projet
"""

import numpy as np

def _determ_St(b:float, d:float) -> float:
    """
    Permet de déterminer le nombre de Strouhal d'une lame en fonction de ses dimensions b (largeur de la lame dans le sens de l'écoulement) et d (l'épaisseur) en m

    L'abaque de l'article Parker et Welsh 1983 est utilisé pour la régression ayant mené à une loi exponentielle de coefficients m, p = -0.04734656, 0.2606545

    St = m * log10(AR) + p

    Paramètres
    ----------
    b : Largeur de la lame (m)
    d : Epaisseur de la lame (m)

    Retour
    ----------
    Nombre de Strouhal de la lame
    """

    AR = b/d    # Rapport d'aspect
    m, p = -0.04734656, 0.2606545       
    return m * np.log10(AR) + p

def _f_to_U(St:float, d:float, f:float) -> float:
    """
    Calcule la vitesse nécessaire pour que le ton éolien d'une plaque d'épaisseur d (m) de nombre de Strouhal St atteigne la fréquence f (Hz)

    Paramètres
    ----------
    St : Nombre de Strouhal
    d : Epaisseur de la lame (m)
    f : Fréquence (Hz)

    Retour
    ----------
    Vitesse de l'écoulement (m/s)
    """
    return f * d / St