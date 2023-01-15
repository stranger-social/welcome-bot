from pydantic import BaseSettings

class Settings(BaseSettings):
    quiet: bool = True
    mastodon_base_url: str
    mastodon_domain: str
    mastodon_access_token: str
    database_hostname: str = "localhost"
    database_port: str = "5432"
    database_name: str = "welcomebot"
    database_username: str = "postgres"
    database_password: str = "postgres"
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"

settings = Settings()