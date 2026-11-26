"""
Configuration pytest : rend le paquet ``src`` importable quel que soit le
répertoire depuis lequel la suite de tests est lancée.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
