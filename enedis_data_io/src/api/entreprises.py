"""
Module pour lire les données depuis l'API de Enedis pour les entreprises

Lien vers les API:
> https://mon-compte-entreprise.enedis.fr/vos-donnees-energetiques/vos-api

Note: l'authentification est activée par défaut (d'où la visualisation en lecture seule)
"""

from requests import Session

SESSION = Session()

BASE_URL = "https://ext.prod.api.enedis.fr:443/oauth2/v3"


def fetch_token(
    client_id: str | None = None,
    client_secret: str | None = None,
) -> str:
    """Methode pour obtenir un token

    :param client_id: _description_, defaults to None
    :param client_secret: _description_, defaults to None
    :return: _description_
    """
    # La documentation de l'API était éronnée - la structure qui fonctionne vient d'ici:
    # > https://github.com/bokub/conso-api/blob/master/lib/token.ts
    r = SESSION.post(
        f"{BASE_URL}/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    r.raise_for_status()
    token = r.json()
    return token["access_token"]
