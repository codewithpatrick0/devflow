from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str

    # No defaults on purpose: a signing key that falls back to a hardcoded
    # value is the same as having no signature at all. Access and refresh are
    # signed with different keys, so leaking one does not compromise the other.
    secret_key: str
    refresh_secret_key: str
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

settings = Settings()