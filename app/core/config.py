from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(".env", override=True)

class Settings(BaseSettings):
    database_conn_str: str

    secret_key: str
    algorithm: str
    access_token_expire_time: int

    model_config = SettingsConfigDict(
        extra="allow",
        env_file=".env",
        env_file_encoding = "utf-8"
    )

    model_config = SettingsConfigDict(
            extra="allow",
            env_file=".env",
            env_file_encoding = "utf-8"
        )

    @property
    def database_conn_str(self):
        return self.database_conn_str

settings = Settings()
