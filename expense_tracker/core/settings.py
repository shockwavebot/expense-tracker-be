# expense_tracker/core/settings.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Expense Tracker"
    API_V1_STR: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )

    # Database settings
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_SERVER: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_DB: str = Field(default="expense_tracker")

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return self.SYNC_DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')


settings = Settings()

# TODO remove me
# old config.py T
# class Settings(BaseSettings):
#     PROJECT_NAME: str = "Expense Tracker"
#     API_V1_STR: str = "/api/v1"

#     # Database settings
#     POSTGRES_SERVER: str = Field(default="localhost")
#     POSTGRES_USER: str = Field(default="postgres")
#     POSTGRES_PASSWORD: str = Field(default="postgres")
#     POSTGRES_DB: str = Field(default="expense_tracker")
#     POSTGRES_PORT: int = Field(default=5432)

#     @property
#     def SQLALCHEMY_DATABASE_URI(self) -> str:
#         """Get database URI as a string."""
#         return (
#             f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
#             f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
#         )

#     class Config:
#         case_sensitive = True
#         env_file = ".env"
