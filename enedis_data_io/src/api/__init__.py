"""
Management of API I/O
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Automatic retries on failures and support of timeout
TIMEOUT_DEFAULT = 2
RETRIES_DEFAULT = 2


WEB_SESSION = requests.Session()
_retries = Retry(
    total=RETRIES_DEFAULT,
    backoff_factor=0.1,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods={"POST", "GET"},
)
WEB_SESSION.mount("https://", HTTPAdapter(max_retries=_retries))
