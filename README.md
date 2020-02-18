# API Library

Projet d'API Library réalisé en cours de dev' back.

Documentation d'utilisation: https://mathyeu.gitbook.io/api-flask/

## Installation

### Clonage du projet

    $ git clone git@github.com:Totiii/Projet-API-Dev-BAck.git
    
### Pré-requis
- Python : https://www.python.org/downloads/
- Flask : `$ pip install Flask`

### Installation des dépendances

    $ pip install -r requirements.txt
    
### Ajouter la variable d'environement

    Mac : $ export FLASK_APP=app.py
    Windows : 
     - Terminal : $ set FLASK_APP=app.py
     - Powershell : $env:FLASK_APP = "app.py"
    
### Démarrage  du serveur
    
    $ flask run

### Migration de base de données (optionnel)


    $ flask db migrate

    $ flask db upgrade
https://flask-migrate.readthedocs.io/en/latest/#why-use-flask-migrate-vs-alembic-directly

> Thibaud POMMIER 
> Mathieu AUGAIN
