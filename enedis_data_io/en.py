"""
English language interface to the library's functionalities
"""

from enedis_data_io.src.api.entreprises import ApiManager as ApiCompanies
from enedis_data_io.src.api.entreprises import MeterAddress

__all__ = [ApiCompanies, MeterAddress]
