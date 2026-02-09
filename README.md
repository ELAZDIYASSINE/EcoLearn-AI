EcoLearn AI - Plateforme d'apprentissage écologique
===================================================

**Concept** : Plateforme qui génère des parcours d'apprentissage personnalisés via IA et calcule automatiquement l'empreinte carbone de chaque session pour financer la plantation d'arbres.

Tech stack : **FastAPI**, **PostgreSQL**, **React + D3.js**, **Docker**, **GitHub Actions**, **AWS ECS / CloudWatch**.

---

## Architecture globale

- **Backend (`backend/`)**
  - API FastAPI
  - Service Learning : génération de contenu pédagogique adaptatif (intégration API OpenAI via HTTP)
  - Service Carbon : calcul d'empreinte carbone et calcul du nombre d'arbres à financer
  - Service Reforestation : intégration (stub) vers une API de plantation d'arbres
  - Stockage Postgres (parcours, métriques carbone, plantations)

- **Frontend (`frontend/`)**
  - SPA minimale en **React** (via CDN) servie en statique par **Nginx**
  - Dashboard utilisateur avec graphique D3.js pour visualiser l'impact environnemental

- **Base de données**
  - **PostgreSQL** containerisé
  - Tables simples : utilisateurs, sessions d’apprentissage, métriques carbone, évènements de plantation

- **Infra & DevOps**
  - `docker-compose.yml` avec **3 conteneurs** : `api`, `db`, `frontend`
  - Pipeline **GitHub Actions** avec 4 stages : tests, analyse/qualité, build, déploiement
  - Déploiement cible : **AWS ECS** (Fargate ou EC2) avec logs vers **CloudWatch**

---

## Lancer le projet en local (MVP)

Prérequis :
- Docker + Docker Compose
- (Optionnel) Python 3.11+ si tu veux lancer le backend hors Docker

```bash
# Build & run
docker compose up --build

# Backend accessible sur http://localhost:8000/docs
# Frontend accessible sur http://localhost:8080
```

Variables d’environnement importantes (à mettre dans un `.env` à la racine ou dans ton outil de secrets) :

- **Backend**
  - `DATABASE_URL` (par défaut : `postgresql://eco_user:eco_pass@db:5432/ecolearn`)
  - `OPENAI_API_KEY` (optionnel, sinon le service Learning renvoie un contenu mocké)
  - `REFOREST_API_URL` (optionnel, URL de l’API de reforestation)
  - `REFOREST_API_KEY` (optionnel)

---

## Plan de développement sur 5 jours

### Jour 1 – Architecture & Setup DevOps

- **Objectifs**
  - Valider le concept EcoLearn AI et les personas (étudiants, entreprises, écoles).
  - Concevoir l’architecture logique et technique (diagrammes simples).
  - Initialiser le repo (backend FastAPI, frontend React, Postgres).
  - Mettre en place la containerisation de base (3 Dockerfiles + `docker-compose.yml`).
  - Créer un pipeline CI minimal (GitHub Actions) : installation + tests backend.

- **Livrables clés**
  - Structure de repo propre.
  - Docker fonctionnel en local (API + DB + Front basique).
  - Pipeline CI qui s’exécute sur chaque push.

### Jour 2 – Développement & CI/CD

- **Objectifs**
  - Implémenter les endpoints core :
    - `/health`
    - `/learning/path` (génération de parcours + calcul carbone)
    - `/carbon/summary/{user_id}`
  - Ajouter les premiers tests `pytest` (health + happy path Learning).
  - Compléter le pipeline CI/CD :
    - Job `tests` (pytest)
    - Job `quality` (flake8/black + SonarCloud)
    - Job `build` (build images Docker)
    - Job `deploy-staging` (stub vers AWS ECS).

- **Livrables clés**
  - API fonctionnelle en staging.
  - CI/CD complet (jusqu’au staging).

### Jour 3 – Features avancées & Monitoring

- **Objectifs**
  - Améliorer le service Learning (prompting plus riche, prise en compte du niveau utilisateur).
  - Finaliser le service Carbon (formule de calcul configurable).
  - Intégrer/stubber l’API de reforestation (création d’un évènement de plantation).
  - Implémenter le dashboard React :
    - Vue synthèse des sessions utilisateur.
    - Graphique D3.js (courbe ou bar chart : CO₂ évité / arbres financés).
  - Ajouter des métriques basiques (logs structurés, temps de réponse).

- **Livrables clés**
  - Dashboard de base opérationnel.
  - Logs applicatifs prêts à être envoyés vers CloudWatch.

### Jour 4 – Production & Scalabilité

- **Objectifs**
  - Préparer les manifests / définition de service pour AWS ECS.
  - Configurer le logging ECS vers **CloudWatch Logs** (au moins un log group par service).
  - Ajouter quelques tests de charge simples (k6, Locust, ou `ab`/`hey` en local).
  - Rédiger la documentation d’exploitation (runbook simple).

- **Livrables clés**
  - Service déployable en prod sur ECS.
  - Monitoring basique actif via CloudWatch (logs + premiers dashboards).

### Jour 5 – Pitch & Démonstration

- **Objectifs**
  - Préparer un pitch 10 min :
    - Problème → Solution → Différenciation (IA + impact carbone traçable).
    - Démo live : création d’un parcours, affichage du CO₂ et des arbres financés.
    - Roadmap & modèle économique (B2B/B2Schools, licence, API).
  - Préparer une démo 5 min :
    - Scénario utilisateur simple (inscription, génération de parcours, visualisation dashboard).

- **Livrables clés**
  - Slides pitch.
  - Script de démo.

---

## Endpoint principaux (MVP)

- **GET** `/health` : statut du service.
- **POST** `/learning/path`
  - Entrée : `user_id`, `topic`, `level`, `duration_minutes`.
  - Sortie : contenu pédagogique, score de difficulté, métriques CO₂ et arbres suggérés.
- **GET** `/carbon/summary/{user_id}`
  - Retourne les cumuls (CO₂, arbres financés, sessions, dernières plantations).

---

## Prochaine étape

Dans cette base de code, on commence par :
- Créer le backend FastAPI (`backend/app`) avec modèles SQLAlchemy + schémas Pydantic.
- Ajouter le frontend React minimal (`frontend/`) avec un dashboard D3.js très simple.
- Mettre en place les Dockerfiles + `docker-compose.yml`.
- Ajouter le pipeline `.github/workflows/ci-cd.yml` avec 4 stages.

