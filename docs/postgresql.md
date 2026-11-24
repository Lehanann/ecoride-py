# PostgreSQL

EcoRide utilise PostgreSQL comme base de données principale.

Une image Docker préconfigurée est disponible sur Docker Hub afin de simplifier l'installation de l'environnement de développement.

---

## Pourquoi Docker
L'utilisation d'une image Docker personnalisée permet de rendre l'environnement de développement reproductible et de réduire les opérations manuelles nécessaires à la mise en place de PostgreSQL.

---

## Image Docker personnalisée

EcoRide s'appuie sur une image PostgreSQL personnalisée publiée sur Docker Hub :
```bash
docker pull lehanann/postgresql:16-bookworm
```

Cette image permet :

- la création automatique de la base de données.
- la création automatique de l'utilisateur applicatif.
- la création automatique du schéma PostgreSQL ecoride.
- l'initialisation automatisée de l'environnement de développement.

Le code source de l'image est disponible dans le dépôt Docker associé.

Cette image est construite à partir de :
```text
FROM postgres:16-bookworm
```

Elle apporte plusieurs personnalisations :

- configuration de la locale française (fr_FR.UTF-8).
- création automatisée de la base de données.
- création automatisée de l'utilisateur applicatif.
- création automatisée du schéma PostgreSQL ecoride.
- attribution automatique des privilèges nécessaires.
- intégration transparente avec Docker Compose.

Extrait du Dockerfile :
```dockerfile
FROM postgres:16-bookworm

RUN localedef -i fr_FR -c -f UTF-8 \
    -A /usr/share/locale/locale.alias \
    fr_FR.UTF-8

ENV LANG=fr_FR.UTF-8

COPY --chown=postgres:postgres \
    ./create_database.sh \
    /docker-entrypoint-initdb.d/create_database.sh

RUN chmod +x \
    /docker-entrypoint-initdb.d/create_database.sh
```

---

## Utilisation d'un schéma PostgreSQL dédié

L'application n'utilise pas le schéma PostgreSQL par défaut (public).

Toutes les tables sont créées dans le schéma :
```text
ecoride
```

Ce choix permet :

- d'isoler les données applicatives.
- de faciliter l'administration de la base.
- de préparer une éventuelle cohabitation avec d'autres applications.
- d'illustrer l'utilisation avancée des fonctionnalités PostgreSQL.

---

## Initialisation automatique

L'image Docker intègre un script d'initialisation exécuté au premier démarrage du conteneur PostgreSQL.

Le script :

- crée la base de données applicative.
- crée l'utilisateur applicatif.
- crée le schéma ecoride.
- attribue les droits nécessaires.
- retire les permissions inutiles du schéma public.

Extrait :
```shell
CREATE DATABASE :PG_DB;

CREATE USER :PG_USR;

GRANT CONNECT ON DATABASE :PG_DB TO :PG_USR;

\connect :PG_DB;

CREATE SCHEMA :PG_SCHEMA;

GRANT USAGE, CREATE
ON SCHEMA :PG_SCHEMA
TO :PG_USR;

REVOKE USAGE, CREATE
ON SCHEMA PUBLIC
TO :PG_USR;
```

---

## Déploiement avec Docker Compose

Créer un fichier `compose.yaml` :

```yaml
services:
  sqldb:
    image: lehanann/postgresql:16-bookworm
    container_name: pgsql-ecoride
    restart: always

    environment:
      - POSTGRES_PASSWORD=password_postgres
      - PGDATA=/var/lib/postgresql/data

      - PG_DB=ecoride
      - PG_USR=ecoride
      - PG_PWD=password_ecoride
      - PG_SCHEMA=ecoride

    ports:
      - "5432:5432"

    volumes:
      - pgsql-db:/var/lib/postgresql/data

  pgadmin:
    image: dpage/pgadmin4:8.11
    container_name: pgadmin-ecoride
    restart: always

    environment:
      - PGADMIN_DEFAULT_EMAIL=user_root@example.net
      - PGADMIN_DEFAULT_PASSWORD=password_docker_pgadmin

    ports:
      - "8080:80"

    depends_on:
      - sqldb

volumes:
  pgsql-db:
```
Les variables PG_DB, PG_USR, PG_PWD et PG_SCHEMA sont des variables personnalisées exploitées par le script d'initialisation fourni avec l'image Docker EcoRide.

Démarrer les services :

```bash
docker compose up -d
```

---

## Services exposés

| Service | URL |
|----------|----------|
| PostgreSQL | localhost:5432 |
| pgAdmin | http://localhost:8080 |

---

## Accès pgAdmin

```txt
Email    : user_root@example.net
Mot de passe : password_docker_pgadmin
```

---

## Schéma PostgreSQL

EcoRide exploite le schéma PostgreSQL :

```txt
ecoride
```
```text
ecoride.users
ecoride.roles
ecoride.cars
ecoride.carpoolings
ecoride.reservations
ecoride.opinions
```

L'ensemble des tables applicatives est créé dans ce schéma afin d'isoler les données métier de l'application.

---

## Vérification

Connexion au conteneur :

```bash
docker exec -it pgsql-ecoride bash
```

Connexion PostgreSQL :

```bash
psql -U ecoride -d ecoride
```

Afficher les schémas disponibles :

```sql
SELECT schema_name
FROM information_schema.schemata;
```

---

## Résultat attendu

Après le démarrage du conteneur :

- PostgreSQL est accessible sur le port 5432.
- la base de données ecoride est créée.
- l'utilisateur applicatif ecoride est créé.
- le schéma ecoride est créé.
- les privilèges nécessaires sont attribués.
- pgAdmin est accessible sur le port 8080.