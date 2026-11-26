"""
Conversion d'unité
"""

from math import pi

def _deg_to_rad(alpha:float) -> float:
    """Convertit un angle en degré en radians"""
    return alpha * pi /180

def _rad_to_deg(alpha:float) -> float:
    """Convertit un angle en radians en degrés"""
    return alpha * 180 / pi

def _ms_to_kmh(U:float) -> float:
    """Convertit une vitesse en m/s en km/h"""
    return U * 3.6

def _kmh_to_ms(U:float) -> float:
    """Convertit une vitesse en km/h en m/s"""
    return U / 3.6