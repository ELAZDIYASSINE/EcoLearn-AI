from __future__ import annotations

from ..config import get_settings


def compute_carbon_for_session(duration_minutes: int) -> float:
    """
    Calcule l'empreinte carbone d'une session en kg de CO₂.

    Formule simple et paramétrable :
      co2 = durée (min) * facteur (kgCO2/min).
    """
    settings = get_settings()
    return duration_minutes * settings.carbon_factor_kg_per_minute


def compute_trees_to_fund(co2_kg: float) -> float:
    """
    Approxime le nombre d'arbres à financer pour compenser l'empreinte CO₂.
    """
    settings = get_settings()
    if settings.kg_co2_per_tree <= 0:
        return 0.0
    return co2_kg / settings.kg_co2_per_tree

