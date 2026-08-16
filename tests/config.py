from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    test_database_url: str

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )


test_settings = TestSettings()
