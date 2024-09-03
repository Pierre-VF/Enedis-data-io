# Utilitaires de traitement de données d'Enedis

Divers utilitaires pour travailler avec les données électriques de Enedis

(Documentation à venir)

## Installation

Assurez vous d'avoir une version de Python 3.12 (non testé pour d'autres versions) et un environnement virtuel de votre choix activé.

Le package s'installe en une ligne:

> pip install git+https://github.com/Pierre-VF/Enedis-data-io

## Cas d'utilisation

### Déchiffrage de fichiers

Déchiffrage de fichiers envoyés par FTP ou e-mail:
```python
from enedis_data_io.src.file_decryption import decrypt_file

file_path_in = "fichier_enedis.zip"
file_path_out = "fichier_decrypte.zip"
key = "_ cle fournie par Enedis _"

res = decrypt_file(file_path_in, key=key, output_file=file_path_out)
```
