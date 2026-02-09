from __future__ import annotations

from typing import Tuple

import requests

from ..config import get_settings
from ..schemas import LearningPathRequest, LearningPathContent


def _call_openai_stub(prompt: str) -> str:
    """
    Appel simplifié vers OpenAI.

    Pour le MVP, on renvoie un contenu généré localement si aucune clé n'est fournie.
    """
    settings = get_settings()
    if not settings.openai_api_key:
        return (
            "Introduction à l'écologie numérique.\n\n"
            "1. Comprendre l'empreinte carbone du numérique\n"
            "2. Bonnes pratiques pour réduire sa consommation\n"
            "3. Quiz rapide pour valider les acquis"
        )

    # Exemple d'appel HTTP générique – à adapter selon la lib OpenAI utilisée.
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "Tu es un tuteur spécialisé en écologie et développement durable.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }
    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=20
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception:
        # Fallback en cas d'erreur API
        return (
            "Introduction à l'écologie numérique.\n\n"
            "1. Comprendre l'empreinte carbone du numérique\n"
            "2. Bonnes pratiques pour réduire sa consommation\n"
            "3. Quiz rapide pour valider les acquis"
        )


def generate_learning_content(req: LearningPathRequest) -> Tuple[LearningPathContent, float]:
    """
    Génère un contenu pédagogique adaptatif à partir de la requête utilisateur.
    Retourne le contenu et un score de difficulté.
    """
    prompt = (
        f"Génère un mini-parcours d'apprentissage sur le sujet '{req.topic}' "
        f"pour un niveau {req.level} d'une durée d'environ {req.duration_minutes} minutes. "
        "Structure la réponse avec un titre, un résumé et 3 à 5 étapes actionnables."
    )

    raw = _call_openai_stub(prompt)

    # Parsing très simplifié : on ne dépend pas de la structure exacte.
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    title = lines[0] if lines else f"Parcours sur {req.topic}"
    summary = lines[1] if len(lines) > 1 else "Parcours généré automatiquement."
    steps = [l for l in lines[2:]] or [
        "Découvrir les bases du sujet.",
        "Approfondir avec des ressources recommandées.",
        "Tester ses connaissances avec un quiz.",
    ]

    # Score de difficulté très simple en fonction du niveau
    difficulty_map = {"beginner": 0.3, "intermediate": 0.6, "advanced": 0.9}
    difficulty_score = difficulty_map.get(req.level.lower(), 0.5)

    content = LearningPathContent(title=title, summary=summary, steps=steps)
    return content, difficulty_score

