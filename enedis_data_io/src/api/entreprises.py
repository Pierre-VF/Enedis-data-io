"""
Module pour lire les données depuis l'API de Enedis pour les entreprises

Pour la simplicité d'usage, il est recommandé d'utiliser l'interface objet via la classe **ApiManager**

Lien vers les API:
> https://mon-compte-entreprise.enedis.fr/vos-donnees-energetiques/vos-api

Lien vers l'état des services:
> https://datahub-enedis.fr/services-api/etat-des-services/

Note: l'authentification est activée par défaut (d'où la visualisation en lecture seule)
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta

import pandas as pd

from enedis_data_io.src.api import WEB_SESSION
from enedis_data_io.src.api.config import SETTINGS
from enedis_data_io.src.types_helpers import DATE_INPUT

BASE_URL = "https://ext.prod.api.enedis.fr:443"
TIMEZONE = "Europe/Paris"


def fetch_token(
    client_id: str | None = None,
    client_secret: str | None = None,
) -> tuple[str, datetime]:
    """Methode pour obtenir un token

    :param client_id: _description_, defaults to None
    :param client_secret: _description_, defaults to None
    :return: Token pour l'API, datetime d'expiration du token
    """
    # La documentation de l'API était éronnée - la structure qui fonctionne vient d'ici:
    # > https://github.com/bokub/conso-api/blob/master/lib/token.ts
    r = WEB_SESSION.post(
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
    return token["access_token"], datetime.now() + timedelta(
        seconds=token["expires_in"]
    )


@dataclass
class MeterAddress:
    number_street_name: str
    postal_code_city: str
    insee_code: str


def fetch_meter_address(token: str, prm: str) -> MeterAddress:
    """Télécharge l'addresse correspondant à un PRM

    :param token: token de l'API
    :param prm: PRM du compteur
    :return: _description_
    """
    r = WEB_SESSION.get(
        url=f"{BASE_URL}/address/v1/{prm}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    r.raise_for_status()
    x = r.json().get("address")
    return MeterAddress(
        number_street_name=x.get("number_street_name"),
        insee_code=x.get("insee_code"),
        postal_code_city=x.get("postal_code_city"),
    )


def fetch_meter_overview(token: str) -> list[str]:
    """Télécharge la liste des PRMs disponibles

    :param token: token de l'API
    :raises NotImplementedError: (pour l'instant, un grand nombre de compteur n'est pas supporté - si trop de pages sont disponibles, cette erreur est retournée)
    :return: liste des PRM sous format str
    """
    r = WEB_SESSION.post(
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


def _f_date(x: DATE_INPUT) -> date:
    if isinstance(x, str):
        return date.fromisoformat(x)
    elif isinstance(x, date):
        return x
    elif isinstance(x, datetime):
        return x.date
    else:
        raise TypeError()


def _parse_start_end_as_dates(
    start: DATE_INPUT,
    end: DATE_INPUT,
) -> tuple[date, date]:
    return _f_date(start), _f_date(end)


def _parse_start_end_as_str(
    start: DATE_INPUT,
    end: DATE_INPUT,
) -> tuple[str, str]:
    x1, x2 = _parse_start_end_as_dates(start, end)
    return str(x1), str(x2)


def fetch_daily_production(
    token: str,
    prm: str,
    start: DATE_INPUT,
    end: DATE_INPUT,
) -> pd.DataFrame:
    """
    Télécharge les données de production journalière (en Wh) sur une période donnée.

    :param token: token pour la requête API
    :param prm: numéro de livraison (PRM)
    :param start: début de la période (au maximum de 36 mois en arrière)
    :param end: fin (exclue) de la période (au minimum 15 jours en arrière)
    :return: production journalière au format pandas.DataFrame(production_wh)
    """
    start, end = _parse_start_end_as_str(start, end)
    r = WEB_SESSION.get(
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


def fetch_daily_consumption(
    token: str,
    prm: str,
    start: DATE_INPUT,
    end: DATE_INPUT,
) -> pd.DataFrame:
    """
    Télécharge les données de consommation journalière (en Wh) sur une période donnée.

    :param token: token pour la requête API
    :param prm: numéro de livraison (PRM)
    :param start: début de la période (au maximum de 36 mois en arrière)
    :param end: fin (exclue) de la période (au minimum 15 jours en arrière)
    :return: consommation journalière au format pandas.DataFrame(production_wh)
    """
    start, end = _parse_start_end_as_str(start, end)
    r = WEB_SESSION.get(
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


def fetch_half_hourly_production(
    token: str,
    prm: str,
    start: DATE_INPUT,
    end: DATE_INPUT,
) -> pd.DataFrame:
    """
    Télécharge les données de production à la demi-heure (en Wh) sur une période donnée.

    :param token: token pour la requête API
    :param prm: numéro de livraison (PRM)
    :param start: début de la période (au maximum de 24 mois en arrière)
    :param end: fin (exclue) de la période (au minimum 15 jours en arrière)
        Note: le début et la fin doivent être séparés de moins de 7 jours
    :return: production journalière au format pandas.DataFrame(production_wh)
    """
    start, end = _parse_start_end_as_str(start, end)
    t_start = datetime.fromisoformat(start)
    t_end = datetime.fromisoformat(end)
    if t_end > t_start + timedelta(days=7):
        raise ValueError("There must be less than 7 days between start and end")
    r = WEB_SESSION.get(
        url=f"{BASE_URL}/mesures/v1/metering_data/production_load_curve",
        params=dict(usage_point_id=prm, start=start, end=end),
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    r.raise_for_status()
    x = r.json()
    df = pd.DataFrame(x["meter_reading"]["interval_reading"])

    if df.empty:
        raise RuntimeError("No data available in period")
    first_value = df["value"][0]
    if isinstance(first_value, list):
        # For 3 phase management
        df["date"] = df["date"].apply(lambda x: x[0])
        df["value"] = df["value"].apply(
            lambda x: float(x[0]) + float(x[1]) + float(x[2])
        )
    df["t"] = pd.to_datetime(df["date"], utc=False)
    out = df[["value", "t"]].set_index("t").rename(columns={"value": "production_wh"})
    out = out.tz_localize(TIMEZONE, ambiguous="infer")
    return out


# Object-oriented interface to facilitate the work


class ApiManager:
    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> None:
        if client_id is None:
            client_id = SETTINGS.ENEDIS_API_USERNAME
        if client_secret is None:
            client_secret = SETTINGS.ENEDIS_API_PASSWORD
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__token: str | None = None
        self.__token_expiry: str | None = None

    @property
    def token(self) -> str:
        if (self.__token is None) or (
            self.__token_expiry and self.__token_expiry >= datetime.now()
        ):
            # Refresh the token if it's either now available or expiring
            self.__token, self.__token_expiry = fetch_token(
                client_id=self.__client_id, client_secret=self.__client_secret
            )
        return self.__token

    def meters(self) -> list[str]:
        return fetch_meter_overview(self.token)

    def meter_address(self, prm: str) -> MeterAddress:
        return fetch_meter_address(self.token, prm=prm)

    def daily_consumption(
        self, prm: str, start: DATE_INPUT, end: DATE_INPUT
    ) -> pd.DataFrame:
        return fetch_daily_consumption(token=self.token, prm=prm, start=start, end=end)

    def daily_production(
        self, prm: str, start: DATE_INPUT, end: DATE_INPUT
    ) -> pd.DataFrame:
        return fetch_daily_production(token=self.token, prm=prm, start=start, end=end)

    def half_hourly_production(
        self, prm: str, start: DATE_INPUT, end: DATE_INPUT
    ) -> pd.DataFrame:
        return fetch_half_hourly_production(
            token=self.token, prm=prm, start=start, end=end
        )
