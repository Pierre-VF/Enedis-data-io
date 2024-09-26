"""
Interface vers les fonctionnalités essentielles en Français
"""

import pandas as pd
from enedis_data_io.src.api.entreprises import ApiManager as _ApiManager
from enedis_data_io.src.api.entreprises import MeterAddress as AdresseCompteur


class ApiEntreprises:
    """
    Classe d'interface vers les fonctionalités entreprise

    (Documentation à réaliser)
    """
    def __init__(self, client_id: str, client_secret: str) -> None:
        self.__api_manager = _ApiManager(client_id=client_id, client_secret=client_secret)

    def compteurs(self) -> list[str]:
        return self.__api_manager.meters()
    
    def adresse_du_compteur(self, prm: str) -> AdresseCompteur:
        return self.__api_manager.meter_address(prm=prm)

    def consommation_journaliere(self, prm: str, start: str, end: str) -> pd.DataFrame:
        return self.__api_manager.daily_consumption(prm=prm, start=start, end=end)
    
    def production_journaliere(self, prm: str, start: str, end: str) -> pd.DataFrame:
        return self.__api_manager.daily_production(prm=prm, start=start, end=end)
    
    def production_par_demi_heure(self, prm: str, start: str, end: str)
        return self.__api_manager.half_hourly_production(prm=prm, start=start, end=end)


__all__ = [ApiEntreprises, AdresseCompteur]