from __future__ import annotations

from typing import Optional

import requests

from ..config import get_settings


def trigger_reforestation(trees: int, co2_kg: float) -> Optional[str]:
    """
    Appel (stub) vers une API de reforestation.

    Retourne un identifiant externe si disponible.
    Dans le MVP, on fait un simple appel HTTP si l'URL et la clé sont définies.
    """
    settings = get_settings()
    if not settings.reforest_api_url or not settings.reforest_api_key:
        # Pas de config → on simule un ID.
        return None

    headers = {
        "Authorization": f"Bearer {settings.reforest_api_key}",
        "Content-Type": "application/json",
    }
    payload = {"trees": trees, "co2_kg": co2_kg, "source": "EcoLearn AI"}

    try:
        resp = requests.post(settings.reforest_api_url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return str(data.get("id") or data.get("reference") or "")
    except Exception:
        # On ne bloque pas le parcours d'apprentissage si l'API externe échoue
        return None

