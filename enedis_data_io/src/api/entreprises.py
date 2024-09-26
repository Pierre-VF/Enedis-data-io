"""
Module pour lire les données depuis l'API de Enedis pour les entreprises

Lien vers les API:
> https://mon-compte-entreprise.enedis.fr/vos-donnees-energetiques/vos-api

Lien vers l'état des services:
> https://datahub-enedis.fr/services-api/etat-des-services/

Note: l'authentification est activée par défaut (d'où la visualisation en lecture seule)
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd
from requests import Session

SESSION = Session()

BASE_URL = "https://ext.prod.api.enedis.fr:443"
TIMEZONE = "Europe/Paris"


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
        f"{BASE_URL}/oauth2/v3/token",
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


@dataclass
class MeterAddress:
    number_street_name: str
    postal_code_city: str
    insee_code: str


def meter_address(token: str, prm: str) -> MeterAddress:
    """Télécharge l'addresse correspondant à un PRM

    :param token: token de l'API
    :param prm: PRM du compteur
    :return: _description_
    """
    r = SESSION.get(
        url=f"{BASE_URL}/address/v1/{prm}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    r.raise_for_status()
    x = r.json().get("address")
    return MeterAddress(**x)


def meter_overview(token: str) -> list[str]:
    """Télécharge la liste des PRMs disponibles

    :param token: token de l'API
    :raises NotImplementedError: (pour l'instant, un grand nombre de compteur n'est pas supporté - si trop de pages sont disponibles, cette erreur est retournée)
    :return: liste des PRM sous format str
    """
    r = SESSION.post(
        url=f"{BASE_URL}/usage_point_id_perimeter/v1/usage_point_id",
        data='{"page_number": 1}',
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json;charset=UTF-8",
        },
    )
    r.raise_for_status()
    x = r.json()
    n_pages = x.get("query_parameters").get("page_total_count")
    if n_pages > 1:
        raise NotImplementedError(
            f"Fetching a large number of meters is not implemented (this would only fetch one page out of {n_pages})"
        )
    out = x.get("usage_point_id")
    return out


def daily_production(token: str, prm: str, start: str, end: str) -> pd.DataFrame:
    """
    Télécharge les données de production journalière (en Wh) sur une période donnée.

    :param token: token pour la requête API
    :param prm: numéro de livraison (PRM)
    :param start: début de la période (au maximum de 36 mois en arrière)
    :param end: fin (exclue) de la période (au minimum 15 jours en arrière)
    :return: production journalière au format pandas.DataFrame(production_wh)
    """
    r = SESSION.get(
        url=f"{BASE_URL}/mesures/v1/metering_data/daily_production",
        params=dict(usage_point_id=prm, start=start, end=end),
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    r.raise_for_status()
    x = r.json()
    df = pd.DataFrame(x["meter_reading"]["interval_reading"])
    df["t"] = pd.to_datetime(df["date"], utc=False)
    out = df[["value", "t"]].set_index("t").rename(columns={"value": "production_wh"})
    out = out.tz_localize(TIMEZONE)
    return out


def daily_consumption(token: str, prm: str, start: str, end: str) -> pd.DataFrame:
    """
    Télécharge les données de consommation journalière (en Wh) sur une période donnée.

    :param token: token pour la requête API
    :param prm: numéro de livraison (PRM)
    :param start: début de la période (au maximum de 36 mois en arrière)
    :param end: fin (exclue) de la période (au minimum 15 jours en arrière)
    :return: consommation journalière au format pandas.DataFrame(production_wh)
    """
    r = SESSION.get(
        url=f"{BASE_URL}/mesures/v1/metering_data/daily_consumption",
        params=dict(usage_point_id=prm, start=start, end=end),
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    r.raise_for_status()
    x = r.json()
    df = pd.DataFrame(x["meter_reading"]["interval_reading"])
    df["t"] = pd.to_datetime(df["date"], utc=False)
    out = df[["value", "t"]].set_index("t").rename(columns={"value": "consumption_wh"})
    out = out.tz_localize(TIMEZONE)
    return out


def half_hourly_production(token: str, prm: str, start: str, end: str) -> pd.DataFrame:
    """
    Télécharge les données de production à la demi-heure (en Wh) sur une période donnée.

    :param token: token pour la requête API
    :param prm: numéro de livraison (PRM)
    :param start: début de la période (au maximum de 24 mois en arrière)
    :param end: fin (exclue) de la période (au minimum 15 jours en arrière)
        Note: le début et la fin doivent être séparés de moins de 7 jours
    :return: production journalière au format pandas.DataFrame(production_wh)
    """
    t_start = datetime.fromisoformat(start)
    t_end = datetime.fromisoformat(end)
    if t_end > t_start + timedelta(days=7):
        raise ValueError("There must be less than 7 days between start and end")
    r = SESSION.get(
        url=f"{BASE_URL}/mesures/v1/metering_data/production_load_curve",
        params=dict(usage_point_id=prm, start=start, end=end),
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    r.raise_for_status()
    x = r.json()
    df = pd.DataFrame(x["meter_reading"]["interval_reading"])
    df["t"] = pd.to_datetime(df["date"], utc=False)
    out = df[["value", "t"]].set_index("t").rename(columns={"value": "production_wh"})
    out = out.tz_localize(TIMEZONE)
    return out
