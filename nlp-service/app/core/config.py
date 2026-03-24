from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "NLP Clustering & Topic Modeling Service"
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_PORT: int = 8001
    SPACY_MODEL: str = "en_core_web_sm"
    N_TOPICS: int = 5
    N_CLUSTERS: int = 5
    N_TOP_WORDS: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
