from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class _Settings(BaseSettings):
    ENEDIS_API_USERNAME: str
    ENEDIS_API_PASSWORD: str


load_dotenv()
SETTINGS = _Settings()
