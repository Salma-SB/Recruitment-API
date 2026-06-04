# Recruitment API

API REST pour une plateforme de recrutement développée avec Django et Django REST Framework. Elle permet aux candidats de gérer leur profil et postuler à des offres, aux recruteurs de publier des offres et consulter les candidats. Un moteur de matching basé sur l'IA (OpenAI GPT-4o-mini) analyse la compatibilité entre les profils et les offres.

## Technologies utilisées

- **Backend** : Django 5.2 + Django REST Framework
- **Base de données** : PostgreSQL
- **Authentification** : JWT via SimpleJWT
- **Documentation** : Swagger (drf-spectacular)
- **IA** : OpenAI GPT-4o-mini

## Prérequis

- Python 3.10+
- PostgreSQL

## Installation

Cloner le projet :

```bash
git clone https://github.com/Salma-SB/Recruitment-API.git
cd Recruitment-API
```

Créer et activer un environnement virtuel :

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

## Configuration

Copier le fichier `.env.example` et le renommer en `.env` :

```bash
cp .env.example .env
```

Remplir les variables dans `.env` :

```env
SECRET_KEY=votre-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=recruitment_db
DB_USER=postgres
DB_PASSWORD=votre-mot-de-passe
DB_HOST=localhost
DB_PORT=5432

OPENAI_API_KEY=votre-cle-openai
```

Créer la base de données PostgreSQL :

```sql
CREATE DATABASE recruitment_db;
```

Appliquer les migrations :

```bash
python manage.py migrate
```

Créer un compte administrateur :

```bash
python manage.py createsuperuser
```

Lancer le serveur :

```bash
python manage.py runserver
```

L'API est disponible sur `http://127.0.0.1:8000`

## Documentation Swagger

```
http://127.0.0.1:8000/api/docs/
```

## Endpoints

### Authentification

```
POST /api/auth/register/candidat/   → Créer un compte candidat
POST /api/auth/register/recruteur/  → Créer un compte recruteur
POST /api/auth/login/               → Connexion (retourne un token JWT)
POST /api/auth/refresh/             → Rafraîchir le token
```

### Candidats

```
GET    /api/candidats/         → Liste des candidats
GET    /api/candidats/{id}/    → Détail d'un candidat
PATCH  /api/candidats/{id}/    → Modifier son profil
```

### Recruteurs

```
GET /api/recruteurs/candidats/                    → Liste des candidats
GET /api/recruteurs/candidats/?competence=python  → Filtrer par compétence
GET /api/recruteurs/candidats/?disponible=true    → Filtrer par disponibilité
```

### Offres d'emploi

```
GET    /api/offres-emploi/                         → Liste des offres
POST   /api/offres-emploi/                         → Créer une offre
PATCH  /api/offres-emploi/{id}/                    → Modifier une offre
DELETE /api/offres-emploi/{id}/                    → Fermer une offre
GET    /api/offres-emploi/{id}/candidat-recommend/ → Matching IA
```

### Candidatures

```
POST  /api/candidatures/                  → Postuler à une offre
GET   /api/candidatures/mes-candidatures/ → Consulter ses candidatures
PATCH /api/candidatures/{id}/statut/      → Changer le statut
```

## Authentification des requêtes

```
Authorization: Bearer <votre_token>
```

## Tests

```bash
python manage.py test api
```

## Administration

```
http://127.0.0.1:8000/admin/
```
