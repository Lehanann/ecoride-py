from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from urllib.parse import quote_plus

class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PG_USR: str = Field(default="postgres")
    PG_PWD: str = Field(default="")
    PG_HOST: str = Field(default="localhost")
    PG_PORT: int = Field(default=5432)
    PG_DB: str = Field(default="postgres")
    PG_SCHEMA: str = Field(default="public")

    @property
    def dsn_async(self) -> str:
        encoded_pwd = quote_plus(self.PG_PWD)
        return(
            f"postgresql+psycopg_async://"
            f"{self.PG_USR}:{encoded_pwd}"
            f"@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"
        )

settings = Settings()
