Je te propose deux README distincts, un pour le dépôt **Backend Django** et un pour le dépôt **Frontend React**. Ils sont rédigés dans un format professionnel adapté à un projet universitaire et à une éventuelle reprise par Kaléinno.

---

# README - Backend Django

````markdown
# CartoDataSup - Backend API

## Présentation

CartoDataSup est une plateforme d'analyse territoriale des données Parcoursup développée dans le cadre d'un projet MIAGE PRO en partenariat avec Kaléinno.

Le backend est développé avec Django et Django REST Framework. Il permet :

- L'authentification des utilisateurs via JWT
- L'importation des données Parcoursup
- Le traitement et l'enregistrement des données dans la base
- Le calcul et l'exposition des indicateurs statistiques
- La mise à disposition d'API REST consommées par le frontend React

---

## Technologies utilisées

- Python 3.x
- Django
- Django REST Framework
- JWT Authentication
- SQLite (Développement)
- PostgreSQL (Production)
- Railway (Déploiement)

---

## Installation locale

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd cartodatasup_django
````

### 2. Créer un environnement virtuel

```bash
python -m venv env
```

### 3. Activer l'environnement

#### Windows

```bash
env\Scripts\activate
```

#### Linux / MacOS

```bash
source env/bin/activate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 5. Appliquer les migrations

```bash
python manage.py migrate
```

### 6. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

### 7. Lancer le serveur

```bash
python manage.py runserver
```

Le serveur sera disponible sur :

```text
http://127.0.0.1:8000/
```

---

## Importation des données Parcoursup

### Via commande Django

```bash
python manage.py import_data
```

### Via l'application

Un administrateur peut importer directement un fichier CSV depuis l'interface utilisateur.

Le système :

1. Analyse le fichier CSV
2. Crée les établissements
3. Crée les formations
4. Crée les candidatures
5. Met à jour les indicateurs disponibles

---

## Authentification

Le projet utilise JWT.

### Connexion

```http
POST /api/login/
```

### Rafraîchissement du token

```http
POST /api/token/refresh/
```

---

## Principaux endpoints

### Authentification

```text
POST /api/login/
POST /api/token/refresh/
```

### Filtres

```text
GET /filters/
```

### Importation

```text
POST /import-data/
```

### Indicateurs

```text
GET /public-vs-private/
GET /formations/admission-rate/
GET /formations/filling-rate/
GET /formations/candidates/
...
```

---

## Déploiement

Le backend est déployé sur Railway.

### Variables d'environnement

```env
SECRET_KEY=
DEBUG=False
DATABASE_URL=
```

---

## Équipe Projet

Projet réalisé dans le cadre du Master MIAGE - Parcours Data & Business Intelligence.

Partenaire :

Kaléinno

Université de Rennes


## 🛠️ Prérequis Système
Avant de commencer, assurez-vous d'avoir installé sur votre Mac :
* **Homebrew** (Gestionnaire de paquets pour macOS)
* **Anaconda / Miniconda** (Pour la gestion des versions Python)
* **Node.js** (Version LTS recommandée, incluant `npm`)

---

## 💻 1. Installation du Backend (Django)

Le backend utilise **Django 5.1.6** et nécessite au minimum **Python 3.12** (ou Python 3.13) en architecture ARM64.

### Étape 1.1 : Préparer l'environnement virtuel
Pour éviter les conflits avec le Python système de macOS, on utilise l'exécutable d'Anaconda pour initialiser un environnement virtuel isolé :

```bash
# Se placer dans le dossier backend
cd cartodatasup_django

# Supprimer un ancien environnement défectueux si nécessaire
rm -rf .venv

# Créer le nouvel environnement avec le Python récent d'Anaconda
/opt/anaconda3/bin/python3 -m venv .venv

# Activer l'environnement virtuel
source .venv/bin/activate

```

### Étape 1.2 : Installer les dépendances système et Python

Si le paquet `psycopg2-binary` requiert une compilation, installez d'abord la bibliothèque PostgreSQL native :

```bash
# Installer libpq via Homebrew
brew install libpq
export PATH="/opt/homebrew/opt/libpq/bin:$PATH"

# Mettre à jour pip et installer les packages du projet
pip install --upgrade pip
pip install -r requirements.txt

```

### Étape 1.3 : Configuration de la Base de Données

Le projet utilise `dj_database_url` pour la configuration de la base de données.

* **Option A (Développement rapide) :** Modifier temporairement `backend/settings.py` pour utiliser **SQLite** :
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

```


* **Option B (PostgreSQL local) :** Exporter la variable d'environnement avant le lancement :
```bash
export DATABASE_URL="postgres://username:password@localhost:5432/nom_bdd"

```



### Étape 1.4 : Base de données & Initialisation

Appliquez les migrations existantes, générez les éventuelles modifications manquantes et importez les données initiales :

```bash
# Appliquer les migrations de base
python manage.py migrate

# Détecter et appliquer les changements locaux (ex: application 'admissions')
python manage.py makemigrations
python manage.py migrate

# Créer le compte administrateur (Suivre les instructions à l'écran)
python manage.py createsuperuser

# Lancer le script d'importation des données initiales
python manage.py import_data

```

### Étape 1.5 : Lancer le serveur Backend

```bash
python manage.py runserver

```

Le backend sera disponible sur : **`http://127.0.0.1:8000/`**
L'interface d'administration sur : **`http://127.0.0.1:8000/admin/`**

