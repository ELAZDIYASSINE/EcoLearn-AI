import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "EcoLearn AI"
    environment: str = os.getenv("ENVIRONMENT", "local")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://eco_user:eco_pass@db:5432/ecolearn",
    )
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    reforest_api_url: str | None = os.getenv("REFOREST_API_URL")
    reforest_api_key: str | None = os.getenv("REFOREST_API_KEY")
    carbon_factor_kg_per_minute: float = float(
        os.getenv("CARBON_FACTOR_KG_PER_MINUTE", "0.005")
    )  # ~0.3 kg/h
    kg_co2_per_tree: float = float(os.getenv("KG_CO2_PER_TREE", "20"))


@lru_cache
def get_settings() -> Settings:
    return Settings()

