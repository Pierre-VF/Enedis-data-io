# Utilitaires de traitement de données d'Enedis

Divers utilitaires pour travailler avec les données électriques de Enedis

(Documentation à venir)

**Note: le code est actuellement en phase de développement avec une évolution rapide des fonctionalités. La rétrocompatibilité n'est donc pas encore assurée à ce stade.**

## Installation

Assurez vous d'avoir une version de Python 3.12 (non testé pour d'autres versions) et un environnement virtuel de votre choix activé.

Le package s'installe en une ligne:

> pip install git+https://github.com/Pierre-VF/Enedis-data-io

## Cas d'utilisation

### Interfaçage avec l'API entreprise

Un certain nombre de fonctionalités de l'API entreprise sont déjà implémentées.

Deux interfaces sont disponibles: une anglophone et une francophone.

Interface anglophone:
```python
from enedis_data_io.en import ApiCompanies

api_io = ApiCompanies(client_id=client_id, client_secret=client_secret)

# Vue d'ensemble des PRM disponibles
api_io.meters()

# Données de contexte par PRM
api_io.meter_address(prm: str)

# Production et consommation avec sortie au format Pandas DataFrame
api_io.daily_consumption(prm: str, start: str, end: str)
api_io.daily_production(prm: str, start: str, end: str)
api_io.half_hourly_production(prm: str, start: str, end: str)

```

Interface francophone:
```python
from enedis_data_io.fr import ApiEntreprises

api_io = ApiEntreprises(client_id=client_id, client_secret=client_secret)

# Vue d'ensemble des PRM disponibles
api_io.compteurs()

# Données de contexte par PRM
api_io.adresse_du_compteur(prm: str)

# Production et consommation avec sortie au format Pandas DataFrame
api_io.consommation_journaliere(prm: str, start: str, end: str)
api_io.production_journaliere(prm: str, start: str, end: str)
api_io.production_par_demi_heure(prm: str, start: str, end: str)


```

### Déchiffrage de fichiers

Déchiffrage de fichiers envoyés par FTP ou e-mail:

```python
from enedis_data_io.src.file_decryption import decrypt_file

file_path_in = "fichier_enedis.zip"
file_path_out = "fichier_decrypte.zip"
key = "_ cle fournie par Enedis _"

res = decrypt_file(file_path_in, key=key, output_file=file_path_out)

```

## Crédits et contributions

Le code est gracieusement mis à disposition par la coopérative citoyenne de production d'énergie [Énergies partagées en Alsace](https://energies-partagees-alsace.coop/) et développé par 
[PierreVF Consulting](https://www.pierrevf.consulting/).

Toute contribution à la base de code est la bienvenue.
