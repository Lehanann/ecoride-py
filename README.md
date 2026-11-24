# EcoRide Backend

Backend de l'application **EcoRide**, une plateforme de covoiturage écoresponsable développée dans le cadre d'un projet d'étude.

Cette version constitue une refonte complète du backend initialement réalisé avec Laravel vers un backend Python moderne basé sur **FastAPI**.

## Fonctionnalités

### Utilisateur

- Création de compte
- Authentification JWT
- Gestion du profil utilisateur
- Gestion des crédits
- Réservation de covoiturages
- Dépôt d'avis après un trajet terminé
- Gestion des véhicules
- Gestion des réservations

### Chauffeur

- Gestion des véhicules
- Création et gestion de covoiturages
- Publication et clôture des trajets
- Consultation des réservations

### Employé

- Modération des avis déposés par les utilisateurs


### Administrateur

- Tableau de bord administrateur
- Consultation des statistiques de la plateforme
- Suivi de l'activité des covoiturages
- Suivi des revenus générés

---

## Technologies utilisées

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

### Bases de données

- PostgreSQL

### Authentification

- JWT (JSON Web Token)

### Outils

- Typer (CLI)
- Pytest
- Alembic

---

## Architecture

Le projet repose sur une architecture en couches :

```text
API Routes
    ↓
Services
    ↓
Repositories
    ↓
PostgreSQL
```

Organisation principale :

```text
app/
├── api/
├── core/
├── models/
├── repositories/
├── schemas/
├── services/
├── utils/
└── workers/

cli/
└── commands/
```

---

## Prérequis

- Python 3.12+
- PostgreSQL 16
- Docker(recommandé)
- Git

Une documentation détaillée de l'installation PostgreSQL est disponible dans :

docs/porstgresql.md

---

## Installation

### Cloner le projet

```bash
git clone https://github.com/Lehanann/ecoride-py
cd ecoride-py
```

### Créer un environnement virtuel

Linux :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows :

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Installer les dépendances

```bash
pip install -r requirements.txt
```

### Installer le projet

```bash
pip install -e .
```

---

## Configuration

Créer un fichier `.env`.

Exemple :

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/ecoride
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

#path storage
STORAGE=storage

#database Postgresql
PG_USR=user-ecoride
PG_PWD=password-user-ecoride
PG_HOST=127.0.0.1
PG_PORT=5432
PG_DB=ecoride
PG_SCHEMA=ecoride
```

Adapter les valeurs selon votre environnement.

---

## Base de données PostgreSQL
EcoRide utilise PostgreSQL.

Une procédure complète d'installation est disponible dans :

docs/postgresql.md

Créer une base de données :
```sql
CREATE DATABASE ecoride;
```

Les scripts SQL d'exemple sont disponibles dans :

```text
scripts/
```

---

## Création des comptes

Le projet expose un outil en ligne de commande basé sur Typer.

Afficher l'aide :

```bash
ecoride --help
```

Afficher les commandes utilisateurs :

```bash
ecoride users --help
```

Afficher les commandes rôles :

```bash
ecoride roles --help
```

### Création d'un administrateur

```bash
ecoride users create administrator \
    --username admin \
    --email admin@ecoride.local \
    --password secret \
    --confirm-password secret
```
L'application autorise la création d'un unique administrateur.

### Création d'un employé

```bash
ecoride users create employee Jean Dupont
```
La commande demande ensuite les informations complémentaires nécessaires (numéro de téléphone, adresse, date de naissance, mot de passe, etc.).
Ces informations peuvent être renseignées ou ignorées selon le contexte.

---

## Lancement de l'application

#### Développement:
```bash
uvicorn app.main:app --reload
```

#### Production:
Utiliser un serveur ASGI comme Uvicorn derrière Nginx.
L'API sera accessible sur :

```text
http://localhost:8000
```

---

## Documentation API

Documentation Swagger :

```text
http://localhost:8000/docs
```

Documentation ReDoc :

```text
http://localhost:8000/redoc
```

---

## Frontend associé

Le frontend de l'application est développé avec :

- Next.js
- React
- TypeScript
- Tailwind CSS
- Shadcn/UI

Consulter le dépôt frontend associé pour les instructions d'installation et d'utilisation.
https://github.com/Lehanann/ecoride-next

---

## Déploiement

Une architecture de déploiement courante :

```text
Internet
    ↓
Nginx
    ↓
Next.js (Frontend)
    ↓
FastAPI (Backend)
    ↓
PostgreSQL
```

---

## Objectif pédagogique

Ce projet a été développé dans le cadre d'un projet d'étude afin de démontrer :

- la conception d'une API REST moderne avec FastAPI ;
- l'utilisation de SQLAlchemy et Pydantic ;
- l'authentification par JWT ;
- l'organisation d'un projet Python en couches ;
- l'intégration avec un frontend Next.js ;
- la mise en place d'une application complète de covoiturage.

Le projet est destiné à illustrer une démarche de développement et des compétences techniques Python. Il n'a pas vocation à constituer un produit de production.