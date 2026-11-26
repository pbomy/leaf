"""
Registre des solvers disponibles.

L'import de ce paquet déclenche l'import de tous les modules de solvers,
ce qui enregistre leurs classes auprès de ``BaseSolver`` (via
``BaseSolver.__subclasses__()``). C'est ce qui permet au chargement des
paramètres de retrouver le solver demandé à partir de son ``SOLVER_NAME``.
"""

from src.parker.solvers.koch import solvers as _solvers_koch  # noqa: F401
